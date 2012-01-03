# Copyright (c) 2004-2008 Nuxeo SAS <http://nuxeo.com>
# Copyright (c) 2004-2006 Chalmers University of Technology <http://www.chalmers.se>
# Authors :
# Julien Anguenot <ja@nuxeo.com>
# Jean-Marc Orliaguet <jmo@ita.chalmers.se>
# M.-A. Darche <madarche@nuxeo.com>
# Georges Racinet <gracinet@nuxeo.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# $Id$

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

"""Portlets Tool

The portlets tool manages portlets, and various ZEO-aware caches:
 - render caches, for the renderings of portlets (see the documentation in
the doc directory of this product)
 - lookup cache: a global object that caches a pre-version of list of portlets
to be displayed according to context. After filtering with conditions that
cannot be cached (such as guards), this becomes the actual list of portlets to
display.
"""

import warnings
from logging import getLogger
import operator
from DateTime import DateTime

from zope.interface import implements
from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from Acquisition import aq_base, aq_parent, aq_inner
from Globals import InitializeClass, DTMLFile
from Globals import  PersistentMapping
from OFS.Cache import Cacheable

from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission

from Products.CPSUtil.conflictresolvers import IncreasingDateTime
from Products.CPSCore.EventServiceTool import getPublicEventService
from Products.CPSCore.utils import bhasattr
from Products.CPSPortlets.interfaces import IPortletTool
from Products.CPSPortlets.PortletRAMCache import RAMCache, SimpleRAMCache
from Products.CPSPortlets.PortletsContainer import PortletsContainer
from Products.CPSPortlets.CPSPortletsPermissions import ManagePortlets

logger = getLogger(__name__)

# RAM cache
PORTLET_CONTAINER_ID = '.cps_portlets'
PORTLET_RAMCACHE_ID = 'portlets'

# Icons
ICON_RAMCACHE_ID = 'icons'
ACTIONICON_RAMCACHE_ID = 'actioncons'
IMG_TAG = '<img src="%s" width="%s" height="%s" alt="%s" title="%s" />'

# FTI
FTI_RAMCACHE_ID = 'fti'

# Actions
PORTLET_MANAGE_ACTION_ID = 'portlets'
PORTLET_MANAGE_ACTION_CATEGORY = 'folder'

# The ID of the portlet lookup cache
LOOKUP_CACHE_ID = '_v_portlet_lookup_cache'
# The ID of the date of the last update on the portlet lookup cache globally and
# on this particular instance.
LOOKUP_CACHE_DATE_GLOBAL_ID = 'portlet_lookup_cache_date'
LOOKUP_CACHE_DATE_INSTANCE_ID = '_v_portlet_lookup_cache_date'


class PortletsTool(UniqueObject, PortletsContainer, Cacheable):
    """Portlets Tool
    """
    implements(IPortletTool)

    id = 'portal_cpsportlets'
    meta_type = 'CPS Portlets Tool'

    security = ClassSecurityInfo()

    # RAM Cache
    caches = {}

    _properties = PortletsContainer._properties + (
        {'id': 'ignore_events', 'type': 'boolean', 'mode': 'w',
         'label': "Ignore events"},
        {'id': 'render_cache_disabled', 'type': 'boolean', 'mode': 'w',
         'label': "Disable the render cache (for dev/debug)"},
        {'id': 'shield_disabled', 'type': 'boolean', 'mode': 'w',
         'label': "Disable the render shield (for dev/debug)"},
        )

    ignore_events = False

    render_cache_disabled = False

    render_shield_disabled = False

    def __init__(self):
        self.initializeCacheParameters()
        CMFBTreeFolder.__init__(self, self.id)

    #
    # Catalog
    #

    security.declarePrivate('_getPortletCatalog')
    def _getPortletCatalog(self):
        """Return the portlet catalog
        """
        catalog = getToolByName(self, 'portal_cpsportlets_catalog', None)
        if catalog is None:
            # BBB for installer
            catalog = getToolByName(self, 'portal_catalog')
        return catalog

    security.declarePublic('listAllPortlets')
    def listAllPortlets(self, event_ids=[]):
        """List all the portlets over the portal

        Use the portlets catalog and the dedicated indexes for the
        query.
        """
        query = {}
        if event_ids:
            query['eventIds'] = event_ids
        portlets = set(brain.getObject()
                       for brain in self._getPortletCatalog()(**query))
        portlets.discard(None) # stale entries in catalog
        return portlets

    security.declarePublic('listPortlets')
    def listPortlets(self, **kw):
        """List all portlets meeting certain criteria.

           parameters:
           - topics
           - portal_types
        """
        catalog = self._getPortletCatalog()
        query = {}

        # topics
        topics = kw.get('topics')
        if topics:
            query['Subject'] = topics

        # portal types
        ptypes = kw.get('portal_types')
        if ptypes:
            query['portal_type'] = ptypes

        portlets = []
        for res in catalog.searchResults(query):
            portlet = res.getObject()
            if portlet is None:
                continue
            if portlet.isGlobal(): # GR PERF should ne handled by an index
                continue
            portlets.append(portlet)
        return portlets

    security.declarePublic('checkIdentifier')
    def checkIdentifier(self, identifier):
        """Check that the given portlet identifier is not already in use.

        The check is done on all of the portal portlets, independently of their
        location (global or local) in the portal. This is for safety.
        """
        # Get all portlets all over the portal
        portlets = self.listAllPortlets()
        existing_identifiers = []
        for portlet in portlets:
            if portlet:
                cidentifier = getattr(aq_base(portlet), 'identifier', None)
                if cidentifier is not None:
                    existing_identifiers.append(cidentifier)
        return (identifier not in existing_identifiers)

    security.declareProtected(ManagePortlets, 'getPortletByPath')
    def getPortletByPath(self, portlet_path=None):
        """Returns a portlet by its rpath or physical path.
        """
        if portlet_path is None:
            return None
        return self.unrestrictedTraverse(portlet_path, default=None)

    #########################################################################

    security.declarePublic('listPortletSlots')
    def listPortletSlots(self):
        """Return all the available slots
        """

        # Slots defined within portlets defined within the tool
        slots = PortletsContainer.listPortletSlots(self)

        # Get all portlets all over the portal
        # GR PERF: Awful. An index would be so much more efficient, here
        portlets = self.listAllPortlets()

        for portlet in portlets:
            local_slot = portlet.getSlot()
            if local_slot and local_slot not in slots:
                slots.append(local_slot)

        return slots

    security.declarePublic('listPortletTypes')
    def listPortletTypes(self):
        """Return the list of all defined portal_types which are portlets

        It means having the 'CPS Portlet' flag
        """
        ttool = getToolByName(self, 'portal_types')
        returned = []
        for ti in ttool.listTypeInfo():
            if ti.getProperty('cps_is_portlet', 0):
                returned.append(ti.getId())
        return returned

    ############################################################################
    security.declarePublic('getPortletContainerId')
    def getPortletContainerId(self):
        """Return the id of the portlet container.
        """
        return PORTLET_CONTAINER_ID

    security.declarePublic('getPortletContainerId')
    def getPortletContainer(self, context=None, create=0, local=0):
        """Returns the portlet container within the given context if it
        exists. Otherwise return the tool

        If the 'local' parameter is 1 then only local containers will
        be returned.
        """
        if context is not None:
            container_id = self.getPortletContainerId()
            if getattr(aq_base(context), container_id, None) is not None:
                return getattr(context, container_id)

            # We create the portlets container if it doesn't already exist
            if create:
                context.manage_addProduct['CPSPortlets'].addPortletsContainer()
                return getattr(context, container_id)

        if not local:
            return getToolByName(self, 'portal_cpsportlets')

    #######################################################################

    security.declarePublic('getBreadCrumbs')
    def getBreadCrumbs(self, context=None):
        """Return the list of parent folders
        """

        bmf = self.getBottomMostFolder(context=context)

        utool = getToolByName(self, 'portal_url')
        rpath = utool.getRelativeContentPath(bmf)
        obj = utool.getPortalObject()

        mtool = getToolByName(self, 'portal_membership')
        checkPerm = mtool.checkPermission

        folders = []
        # other portlets
        for elem in ('',) + rpath:
            if not elem:
                continue
            folders.append(
                {'id': obj.getId(),
                 'title': obj.title_or_id(),
                 'rpath': utool.getRelativeUrl(obj),
                 'editable': checkPerm(ManagePortlets, obj),
                }
            )
            obj = obj._getOb(elem)

        # include the current folder
        folders.append(
            {'id': bmf.getId(),
             'title': bmf.title_or_id(),
             'rpath': utool.getRelativeUrl(bmf),
             'editable': checkPerm(ManagePortlets, bmf),
            }
        )
        return folders

    security.declarePublic('getBottomMostFolder')
    def getBottomMostFolder(self, context=None):
        """Return the first folderish object above the context
        """
        if context is None:
            return None
        obj = context
        bmf = None
        while True:
            if obj.isPrincipiaFolderish:
                bmf = obj
                break
            parent = aq_parent(aq_inner(obj))
            if not obj or parent == obj:
                break
            obj = parent
        if bmf is None:
            bmf = context
        return bmf

    security.declarePublic('getFolders')
    def getFolders(self, context=None):
        """Return the list of folders in which portlets can be added
        """
        folders = []
        if context is None:
            return folders
        mtool = getToolByName(self, 'portal_membership')
        checkPerm = mtool.checkPermission
        folders_append = folders.append
        for c in context.contentValues():
            if not checkPerm(ManagePortlets, c):
                continue
            if not c.isPrincipiaFolderish:
                continue
            folder_id = c.getId()
            if folder_id.startswith('.') or \
                folder_id.startswith('portal_'):
                continue
            folders_append(c)
        return folders

    #######################################################################

    security.declarePublic('getPortlets')
    def getPortlets(self, context=None, slot=None, sort=True, override=True,
                    visibility_check=True, guard_check=True, **kw):
        """Return a list of portlets.
        """
        if context is None:
            return []

        portlets = self._getPortletsCacheable(self.getBottomMostFolder(context),
                                              slot, sort, override)
        return self._filterPortletsAfterCache(context, portlets,
                                              visibility_check, guard_check)

    def _getGlobalLookupCacheDate(self):
        idt = getattr(aq_base(self), LOOKUP_CACHE_DATE_GLOBAL_ID, None)
        if idt is None or isinstance(idt, DateTime):
            setattr(self, LOOKUP_CACHE_DATE_GLOBAL_ID,
                    IncreasingDateTime(LOOKUP_CACHE_DATE_GLOBAL_ID))

        return getattr(self, LOOKUP_CACHE_DATE_GLOBAL_ID)

    security.declarePrivate('_getPortletsCacheable')
    def _getPortletsCacheable(self, bmf, slot, sort, override):
        """Cacheable part of the portlets lookup logic.
        """

        utool = getToolByName(self, 'portal_url')
        portal = utool.getPortalObject()
        bmf_path = utool.getRelativeContentPath(bmf)

        allportlets_rpaths = self._lookupCacheGet(slot, bmf_path, sort,
                                                  override)
        if allportlets_rpaths is not None:
            try:
                return tuple(portal.unrestrictedTraverse(rpath)
                             for rpath in allportlets_rpaths)
            except (AttributeError, KeyError):
                # log and proceed to recomputation
                logger.error(
                    "There are ghost entries in the lookup cache. "
                    "Cluster-wide invalidation timestamp: %r "
                    "process-local invalidation timestamp: %r",
                    self._getGlobalLookupCacheDate(),
                    getattr(aq_base(self),
                            LOOKUP_CACHE_DATE_INSTANCE_ID, None))

        # Get portlets from the root to current path
        obj = portal
        # root portlets
        allportlets = self._getFolderPortlets(folder=obj, slot=slot)
        # other portlets
        for elem in ('',) + bmf_path:
            if not elem:
                continue
            obj = getattr(obj, elem, None)
            if obj is None:
                break
            allportlets.extend(self._getFolderPortlets(folder=obj, slot=slot))

        if sort:
            # Sorting the portlets by order
            allportlets.sort(key=operator.attrgetter('order'))

        # List of portlets that will not be displayed
        remove_set = set()

        # Applying overridance rules
        # GR PERF quadratic complexity (dubious).
        for portlet in allportlets:
            if override:
                # the portlet is protected
                if portlet.disable_override:
                    continue
                depth = portlet.getDepth()
                # Run through the slot's portlets to see whether one of them
                # can override this portlet.
                for p in allportlets:
                    # portlets cannot override themselves
                    if p is portlet:
                        continue
                    # the portlet does not do override
                    if not p.slot_override:
                        continue
                    if p.getDepth() <= depth:
                        continue
                    # override the portlet
                    remove_set.add(portlet)
                    break

        allportlets = [p for p in allportlets if p not in remove_set]

        self._lookupCacheSet(tuple(utool.getRpath(ptl) for ptl in allportlets),
                             slot, bmf_path, sort, override)

        return allportlets

    security.declarePrivate('_filterPortletsAfterCache')
    def _filterPortletsAfterCache(self, context, allportlets,
                                  visibility_check, guard_check, **kw):
        """Does the final, uncacheable, filtering of portlets.

        To be applied on the list returned by _lookupCacheGet
        Since it is dependent on many programmatic
        paramaters, the guard checking cannot be cached.

        The visibility depends on actual context rpath, and we use
        bottom most folder rpath as cache key for efficiency. Therefore
        the visibility check cannot be cached (see #2052 for details)

        XXX GR Do we need portlets whose guard failed *not* to override
        the upper ones ?
        """
        # List of portlets that will not be displayed
        remove_set = set()

        if guard_check:
            for portlet in allportlets:
                if visibility_check:
                    if not self._isPortletVisible(portlet, context):
                        remove_set.add(portlet)
                if portlet.getGuard() and not portlet.getGuard().check(
                    getSecurityManager(), portlet, context):
                    remove_set.add(portlet)

        return [portlet for portlet in allportlets
                if portlet not in remove_set]

    security.declarePrivate('_lookupCacheGet')
    def _lookupCacheGet(self, slot, rpath, sort, override):
        """Return portlets paths from the cache according to paramaters.

        ZEO awareness: if the global timestamp is older than ours, then
        another ZEO client has invalidated, and we ignore the entry,
        effectively forcing downstream code to recompute and update the cache.
        """
        self_base = aq_base(self)
        glob_date = self._getGlobalLookupCacheDate()
        inst_date = getattr(self_base, LOOKUP_CACHE_DATE_INSTANCE_ID, None)

        # None is smaller than all DateTime objects
        if inst_date < glob_date.value:
            return None

        portlets_cache_keywords = {'slot': slot, 'rpath': rpath, 'sort': sort,
                                   'override': override,}
        portlets = self.ZCacheable_get(keywords=portlets_cache_keywords)
        return portlets

    security.declarePrivate('_lookupCacheSet')
    def _lookupCacheSet(self, portlets, slot, rpath, sort, override):
        """Set portlets paths in cache for the given parameters."""
        portlets_cache_keywords = {'slot': slot, 'rpath': rpath, 'sort': sort,
                                   'override': override,
                                   }
        # The RAMCacheManager is local to this ZEO client
        self.ZCacheable_set(portlets, keywords=portlets_cache_keywords)

    security.declarePrivate('_invalidatePortletLookupCache')
    def _invalidatePortletLookupCache(self):
        warnings.warn(
            '_invalidatePortletLookupCache is deprecated in favor '
            'of lookupCacheInvalidate; this compatibility alias will be '
            'removed in CPS 3.6', DeprecationWarning, stacklevel=2)
        self.lookupCacheInvalidate()

    security.declareProtected(ManagePortlets, 'lookupCacheInvalidate')
    def lookupCacheInvalidate(self):
        """Remove all the cached portlet rpaths, ZEO aware

        This method should have an UI. Invalidation all caches at once
        is important for a site admin if anything goes wrong.
        """
        logger.info("Invalidating the lookup cache")
        self.ZCacheable_invalidate()
        now = DateTime()

        # timestamp kept for detection of future invalidations by other
        # ZEO clients
        setattr(self, LOOKUP_CACHE_DATE_INSTANCE_ID, now)

        # Share with other ZEO clients that the cache has expired
        self._getGlobalLookupCacheDate().set(now)

    security.declarePublic('getPortletContext')
    def getPortletContext(self, portlet=None):
        """Returns the context of the portlet"""

        if portlet is None:
            return None

        container = aq_parent(aq_inner(portlet))
        container_id = container.getId()

        # global portlet
        if container == self:
            return self

        # local portlet
        if container.getId() == self.getPortletContainerId():
            return portlet.getLocalFolder()
        return None

    ######################################################################

    security.declareProtected(View, 'createPortlet')
    def createPortlet(self, ptype_id, context=None, **kw):
        """Create a new portlet.

        If context is None the portlet is created within the PortletsTool
        (portal_portlets), otherwise the portlet is created locally in portlet
        container of the given context.

        Returns the id of the newly created portlet or None if something has
        failed.
        """
        # Determine where the portlet has to be created
        if context is None:
            if not _checkPermission(ManagePortlets, self):
                raise Unauthorized(
                    "You are not allowed to globally create portlets")

            # Here, it's within the tool
            destination = self
        else:
            if not _checkPermission(ManagePortlets, context):
                raise Unauthorized(
                    "You are not allowed to locally create portlets within %s"
                    % (context.absolute_url()))
            destination = self.getPortletContainer(context=context, create=1)

        # Check if the ptype_id is valid
        if ptype_id not in self.listPortletTypes():
            return None

        portlet_id = destination._createPortlet(ptype_id, **kw)
        getPublicEventService(self).notifyEvent('portlet_create', self, {})
        return portlet_id

    security.declareProtected(View, 'deletePortlet')
    def deletePortlet(self, portlet_id, context=None):
        """Delete portlet id

        Possible to warn event service for action
        """

        # XXX possible to cope with that in a better way ?
        if not _checkPermission(ManagePortlets, context):
            raise Unauthorized(
                "You are not allowed to delete portlets within %s" %(
                context.absolute_url()))

        if context is None:
            destination = self
        else:
            destination = self.getPortletContainer(context=context)

        getPublicEventService(self).notifyEvent('portlet_delete', self, {})
        return destination._deletePortlet(portlet_id)

    security.declareProtected(View, 'duplicatePortlet')
    def duplicatePortlet(self, portlet_id, context=None):
        """Duplicate a portlet

        Possible to warn event service for action
        """

        # XXX possible to cope with that in a better way ?
        if not _checkPermission(ManagePortlets, context):
            raise Unauthorized(
                "You are not allowed to manage portlets in %s" %(
                context.absolute_url()))

        if context is None:
            return None

        container = self.getPortletContainer(context=context)
        cookie = container.manage_copyObjects([portlet_id])
        res = container.manage_pasteObjects(cookie)

        # XXX canonize portlet id
        new_id = res[0]['new_id']
        portlet = getattr(container, new_id, None)
        getPublicEventService(self).notifyEvent('portlet_duplicate', self, {})
        return portlet

    security.declareProtected(View, 'movePortlet')
    def movePortlet(self, portlet=None,
                    dest_folder=None,
                    dest_slot=None, dest_ypos=0, leave=None, **kw):
        """Move portlet
           parameters: portlet,
                       dest_folder, dest_slot, dest_ypos,
           if 'leave' is set to 1 the source portlet will be left in place.
           Returns: the moved portlet.
        """

        if portlet is None:
            return None

        src_folder = portlet.getLocalFolder()
        if dest_folder is None:
            dest_folder = src_folder

        if dest_slot is None:
            dest_slot = portlet.getSlot()

        if leave:
            src_perm = View
        else:
            src_perm = ManagePortlets
        if not _checkPermission(src_perm, src_folder) or \
            not _checkPermission(ManagePortlets, dest_folder):
            raise Unauthorized(
                "You are not allowed to move portlets from %s to %s" %(
                src_folder.absolute_url(), dest_folder.absolute_url() ))

        dest_ypos = int(dest_ypos)

        if dest_folder != src_folder or leave:
            src_container = self.getPortletContainer(context=src_folder,
                                                     create=1)
            dest_container = self.getPortletContainer(context=dest_folder,
                                                     create=1)
            if leave:
                cookie = src_container.manage_copyObjects([portlet.getId()])
            else:
                cookie = src_container.manage_cutObjects([portlet.getId()])
            res = dest_container.manage_pasteObjects(cookie)
            new_id = res[0]['new_id']
            portlet = getattr(dest_container, new_id, None)

        self._insertPortlet(portlet=portlet, slot=dest_slot, order=dest_ypos)
        getPublicEventService(self).notifyEvent('portlet_move', self, {})
        return portlet

    security.declareProtected(View, 'insertPortlet')
    def insertPortlet(self, portlet=None, slot=None, order=0, **kw):
        """ Insert an existing portlet inside a slot at a given order.
        """
        if not _checkPermission(ManagePortlets, portlet):
            raise Unauthorized(
                "You are not allowed to modify %s" %(
                portlet.absolute_url()))

        getPublicEventService(self).notifyEvent('portlet_insert', self, {})
        self._insertPortlet(portlet=portlet, slot=slot, order=order)

    #
    # Portlet RAM Cache
    #

    security.declareProtected(ManagePortlets, 'initializeCacheParameters')
    def initializeCacheParameters(self):
        """Initialize the cache parameter mapping
        """
        self.cache_parameters = PersistentMapping()

    security.declareProtected(ManagePortlets, 'getCacheParameters')
    def getCacheParameters(self):
        """Return all cache parameters.
        """
        return self.cache_parameters

    security.declareProtected(ManagePortlets, 'resetCacheParameters')
    def resetCacheParameters(self):
        """Reset all cache parameters.
        """
        self.cache_parameters = {}
        self.updateCacheParameters(params=self.getCPSPortletCacheParams())

    security.declareProtected(View, 'getCacheParametersFor')
    def getCacheParametersFor(self, ptype_id=''):
        """Return the cache parameters by portal type
        """
        cache_parameters = self.cache_parameters
        if ptype_id in cache_parameters.keys():
            return cache_parameters[ptype_id][:]
        return ['no-cache']

    security.declareProtected(ManagePortlets, 'updateCacheParameters')
    def updateCacheParameters(self, params={}):
        """Update the cache parameters.
        """
        self.cache_parameters.update(params)
        self._p_changed = 1
        # rebuild portlets
        self.rebuild_portlets()

    def getPortletCache(self, create=0):
        """Returns the Portlet RAM cache object.
        """
        cacheid = '_'.join((PORTLET_RAMCACHE_ID,) + \
                            self.getPhysicalPath()[1:-1])
        try:
            return self.caches[cacheid]
        except KeyError:
            cache = RAMCache()
            self.caches[cacheid] = cache
            return cache

    security.declarePublic('getCacheReport')
    def getCacheReport(self):
        """Returns detailed statistics about the cache.
        """
        cache = self.getPortletCache()
        if cache is None:
            return None
        return cache.getReport()

    security.declarePublic('getCacheStats')
    def getCacheStats(self):
        """Returns statistics about the cache.
        """
        cache = self.getPortletCache()
        if cache is None:
            return None

        stats = cache.getStats()
        count = stats['count']
        hits = stats['hits']
        size = stats['size']

        if count > 0:
            effectivity = 100 * hits / count
        else:
            effectivity = 100

        return {'effectivity': effectivity,
                'size': size, }

    security.declarePublic('findCacheOrphans')
    def findCacheOrphans(self):
        """Returns the list of object ids that are in the cache
        but that no longer exist.
        """
        cache = self.getPortletCache()
        if cache is None:
            return []
        portlets = self.listAllPortlets()
        cached_portlets_paths = [p.getPhysicalPath() for p in portlets]
        orphans = []
        for index, entry in cache.getEntries():
            portlet_path = index[0]
            if portlet_path not in (cached_portlets_paths + orphans):
                orphans.append(portlet_path)
        return orphans

    security.declareProtected(ManagePortlets, 'invalidateCacheEntriesById')
    def invalidateCacheEntriesById(self, obid=None):
        """Removes local cache entries that match a given portlet id.
           This method can be used to clean orphaned cache entries.

           In a ZEO environment only the local RAM cache entries will be
           erased. If the portlet still exists then 'portlet.expireCache()'
           should be used instead in order to propagate the information
           between all ZEO instances.
        """
        cache = self.getPortletCache()
        if cache is None:
            return
        cache.delEntries(obid)

    security.declareProtected(ManagePortlets, 'invalidateCacheEntriesByUser')
    def invalidateCacheEntriesByUser(self, user=None):
        """Removes local cache entries that match a given user.

           In a ZEO environment only the local RAM cache entries will be
           erased. If the portlet still exists then 'portlet.expireCache()'
           should be used instead in order to propagate the information
           between all ZEO instances.
        """
        if user is None:
            return

        for entry in self.findCacheEntriesByUser(user):
            # 'entry' is the portlet's path
            portlet_id = entry[0]
            self.invalidateCacheEntriesById(portlet_id)

    security.declarePublic('findCacheEntriesByUser')
    def findCacheEntriesByUser(self, user=None):
        """Return the cache entry ids associated to a user.
        """
        if user is None:
            return []
        user = str(user)

        cache = self.getPortletCache()
        if cache is None:
            return None

        entries = []
        for k, v in cache.getEntries():
            if not v.has_key('user'):
                continue
            if str(v['user']) == user:
                entries.append(k)
        return entries

    #
    # RAM cache (portlet, icons, FTI)
    #
    security.declareProtected(ManagePortlets, 'clearCache')
    def clearCache(self, **kw):
        """Clear the cache."""

        # Portlets
        portletcache = self.getPortletCache()
        if portletcache is not None:
            portletcache.invalidate()

        # icons
        iconcache = self.getCache(ICON_RAMCACHE_ID)
        if iconcache is not None:
            iconcache.invalidate()

        aicache = self.getCache(ACTIONICON_RAMCACHE_ID)
        if aicache is not None:
            aicache.invalidate()

        # FTI
        fticache = self.getCache(FTI_RAMCACHE_ID)
        if fticache is not None:
            fticache.invalidate()

    #
    # Icon RAM Cache
    #

    security.declarePublic('getCache')
    def getCache(self, cache_key=None):
        """Returns the RAM cache object associated to a given cache key
        """
        if cache_key is None:
            return None

        cacheid = '_'.join((cache_key,) + \
                            self.getPhysicalPath()[1:-1])
        try:
            return self.caches[cacheid]
        except KeyError:
            cache = SimpleRAMCache()
            self.caches[cacheid] = cache
            return cache

    security.declarePublic('renderIcon')
    def renderIcon(self, portal_type=None, base_url='', alt=''):
        """Renders the icon"""
        # render portal type icon.
        if portal_type is None:
            return None

        cache = self.getCache(ICON_RAMCACHE_ID)

        # compute the cache index
        index = (portal_type, base_url, alt)

        img_tag = cache.getEntry(index)
        # the icon is not in the cache
        if img_tag is None:
            ttool = getToolByName(self, 'portal_types')
            ti = ttool.getTypeInfo(portal_type)
            if ti is None:
                return None
            icon_path = ti.getIcon()

            # see if an icon with the same name is present in the current
            # theme's icon folder. The path must be relative and cannot contain
            # any '/'.
            if '/' not in icon_path:
                icon_name = icon_path
                tmtool = getToolByName(self, 'portal_themes')
                utool = getToolByName(self, 'portal_url')
                theme, page = tmtool.getEffectiveThemeAndPageName()
                theme_container = tmtool.getThemeContainer(theme)

                icon_folder = theme_container.icons
                if icon_name in icon_folder.objectIds():
                    icon_path = utool.getRpath(icon_folder) + '/' + icon_name

            img = self.unrestrictedTraverse(icon_path, default=None)
            if img is None:
                return None
            trans = self.translation_service
            language = trans.getSelectedLanguage()
            alt_text = trans.translateDefault(alt, target_language=language)
            img_tag = IMG_TAG % (base_url + icon_path,
                                 getattr(img, 'width', 16),
                                 getattr(img, 'height', 16),
                                 alt_text, alt_text)
            if cache is not None:
                cache.setEntry(index, img_tag)
        return img_tag

    #
    # Action icons
    #
    security.declarePublic('renderActionIcon')
    def renderActionIcon(self, category=None, action_id=None,
                         base_url='', alt=''):
        """Renders the action's icon"""
        if category is None or action_id is None:
            return None

        aitool = getToolByName(self, 'portal_actionicons', None)
        if aitool is None:
            return None

        cache = self.getCache(ACTIONICON_RAMCACHE_ID)
        # compute the cache index
        index = (action_id, category, base_url, alt)

        img_tag = cache.getEntry(index)
        # the icon is not in the cache
        if img_tag is None:
            icon_path = aitool.queryActionIcon(category=category,
                action_id=action_id)
            if not icon_path:
                return

            # see if an icon with the same name is present in the current
            # theme's icon folder. The path must be relative and cannot contain
            # any '/'.
            if '/' not in icon_path:
                icon_name = icon_path
                tmtool = getToolByName(self, 'portal_themes')
                utool = getToolByName(self, 'portal_url')
                theme, page = tmtool.getEffectiveThemeAndPageName()
                theme_container = tmtool.getThemeContainer(theme)

                icon_folder = theme_container.icons
                if icon_name in icon_folder.objectIds():
                    icon_path = utool.getRpath(icon_folder) + '/' + icon_name

            # fall back to the icon path specified in CMFActionIcons
            img = self.unrestrictedTraverse(icon_path, default=None)
            if img is None:
                return None
            trans = self.translation_service
            language = trans.getSelectedLanguage()
            alt_text = trans.translateDefault(alt, target_language=language)
            img_tag = IMG_TAG % (base_url + icon_path,
                                 getattr(img, 'width', 0),
                                 getattr(img, 'height', 0),
                                 alt_text, alt_text)
            if cache is not None:
                cache.setEntry(index, img_tag)
        return img_tag

    #
    # FTI RAM cache
    #
    security.declarePublic('getFTIProperty')
    def getFTIProperty(self, portal_type=None, prop_id=None):
        """Return some factory type information
        cached in RAM for faster access"""

        if portal_type is None:
            return None

        if prop_id is None:
            return None

        if prop_id.startswith('_'):
            return None

        cache = self.getCache(FTI_RAMCACHE_ID)
        # compute the cache index
        index = (portal_type, prop_id)
        prop = cache.getEntry(index)
        if prop is None:
            ttool = getToolByName(self, 'portal_types')
            ti = ttool.getTypeInfo(portal_type)
            if ti is None:
                return None
            prop = ti.getProperty(prop_id, None)
            if cache is not None:
                cache.setEntry(index, prop)
        return prop

    #
    # Access key
    #
    security.declarePublic('getAccessKey')
    def getAccessKey(self):
        """Return the value of the key used to access the tool
        """
        # XXX make this configurable
        return '_'

    security.declarePublic('renderAccessKey')
    def renderAccessKey(self, actions=[], **kw):
        """Render the access key html markup
        """
        rendered = ''
        if not actions:
            atool = getToolByName(self, 'portal_actions')
            actions = atool.listFilteredActionsFor(self)

        actions_by_cat = actions.get(PORTLET_MANAGE_ACTION_CATEGORY)
        if actions_by_cat is None:
            return rendered
        portlet_manage_action = [
            ac for ac in actions_by_cat
            if ac.get('id') == PORTLET_MANAGE_ACTION_ID]

        if len(portlet_manage_action) > 0:
            action = portlet_manage_action[0]
        else:
            return rendered

        rendered = '<a href="%s" accesskey="%s"></a>' % \
            (action['url'], self.getAccessKey())
        return rendered

    #
    # Private
    #
    security.declarePrivate('_getDepthOf')
    def _getDepthOf(self, context=None):
        """Returns the depth of the context

        If context is None then we are at depth 0 since we are at the root of
        the portal
        """
        utool = getToolByName(self, 'portal_url')
        portal = utool.getPortalObject()
        if (context is not None and
            context != portal):
            return len(utool.getRelativeContentPath(context))
        return 0

    security.declarePrivate('_isPortletVisible')
    def _isPortletVisible(self, portlet, context):
        """Is the portlet visible in a given context
        """
        # Dublin Core
        if not portlet.isEffective(self.ZopeTime()):
            return 0

        # depth of the context
        cdepth = self._getDepthOf(context)
        # depth of the portlet
        pdepth = portlet.getDepth()
        # depth of the portlet relative to the context
        rdepth = cdepth - pdepth
        if rdepth < 0:
            return 0
        vrange = portlet.getVisibilityRange()
        start = vrange[0]
        end = vrange[1]

        visible = 1
        if start > 0 and start > rdepth:
            visible = 0
        if end > 0 and rdepth >= end:
            visible = 0
        return visible

    security.declarePrivate('_getFolderPortlets')
    def _getFolderPortlets(self, folder=None, slot=None):
        """Load all portlets in a .cps_portlets folder.
           The slot name can be used as a filter.
        """
        portlets = []
        if folder is None:
            return portlets
        portlet_container = self.getPortletContainer(
            context=folder,
            local=1)
        if portlet_container is None:
            return portlets
        for id in portlet_container.listPortletIds():
            portlet = portlet_container.getPortletById(id)
            if slot is not None:
                if portlet.getSlot() != slot:
                    continue
            portlets.append(portlet)
        return portlets

    security.declarePrivate('_insertPortlet')
    def _insertPortlet(self, portlet=None, slot=None, order=0):
        """Insert a portlet inside a slot at a given position.
        """
        if portlet is None:
            return

        # find all portlets inside the slot
        slot_portlets = []
        for p in self.listAllPortlets():
            if p.getSlot() != slot:
                continue
            slot_portlets.append(p)

        # Sorting the portlets by order
        slot_portlets.sort(key=operator.attrgetter('order'))

        # find the position in the list
        # where to insert the portlet
        pos = 0
        for p in slot_portlets:
            if int(p.getOrder()) >= order:
                pos = slot_portlets.index(p)
                break

        # remove the portlet and
        # insert it to its new position
        if portlet in slot_portlets:
            slot_portlets.remove(portlet)
        slot_portlets.insert(pos, portlet)

        # set the portlet's slot and order
        portlet.setSlot(slot)
        portlet.setOrder(order)

        # create a dictionary that holds portlets' order values
        order_dict = dict([(slot_portlets.index(p), int(p.getOrder()))
                           for p in slot_portlets])

        # shift portlets downwards if necessary
        for k in order_dict.keys():
            # skip the first position
            if k == 0:
                continue
            if order_dict[k] > order_dict[k-1]:
                continue
            # move this portlet downwwards
            newpos = order_dict[k-1] + 10
            # XXX: setOrder(newpos) raises an unauthorized exception
            slot_portlets[k].order = newpos
            # update the dictionary too
            order_dict[k] = newpos

    #
    # ZMI
    #
    security.declareProtected(ManagePortlets, 'manage_rebuildPortlets')
    manage_rebuildPortlets = DTMLFile('zmi/manage_rebuildPortlets',
                                       globals())
    security.declareProtected(ManagePortlets, 'manage_RAMCache')
    manage_RAMCache = DTMLFile('zmi/manage_RAMCache',
                                       globals())
    security.declareProtected(ManagePortlets, 'manage_CacheParameters')
    manage_CacheParameters = DTMLFile('zmi/manage_CacheParameters',
                                       globals())
    manage_options = (
        PortletsContainer.manage_options +
        ({'label': 'Rebuild',
          'action': 'manage_rebuildPortlets'},
         {'label': 'Render cache',
          'action': 'manage_RAMCache'},
         {'label': 'Render cache parameters',
          'action': 'manage_CacheParameters'},
         ) + Cacheable.manage_options
        )

    security.declareProtected(ManagePortlets, 'rebuild_portlets')
    def rebuild_portlets(self, REQUEST=None):
        """
        """
        portlets = self.listAllPortlets()
        for portlet in portlets:
            # Might be an error from the user For instance, it the user checked
            # the isPortlet porperty within a 'regular' CPSDocument instance
            # without using the CPSPortlet base class
            if getattr(portlet, '_rebuild', 0):
                portlet._rebuild()

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_rebuildPortlets' \
                + '?manage_tabs_message=%s Portlets rebuilt.' % len(portlets)
            REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(ManagePortlets, 'manage_clearCache')
    def manage_clearCache(self, REQUEST=None):
        """Clears the local RAM cache.
        """
        self.clearCache()

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_RAMCache' \
                + '?manage_tabs_message=Cache cleared'
            REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(ManagePortlets, 'manage_clearCacheOrphans')
    def manage_clearCacheOrphans(self, REQUEST=None):
        """Removes orphaned objects from the cache.
        """
        orphans = self.findCacheOrphans()
        for orphan in orphans:
            self.invalidateCacheEntriesById(orphan)

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_RAMCache' \
                + '?manage_tabs_message=Cache orphans removed'
            REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(ManagePortlets, 'manage_updateCacheParameters')
    def manage_updateCacheParameters(self, REQUEST=None, **kw):
        """Update cache parameters.
        """
        if REQUEST is not None:
            kw.update(REQUEST.form)

        params = {}
        suffix = '_type'
        suffix_length = len(suffix)
        for k, v in kw.items():
            if not k.endswith(suffix):
                continue
            params[k[:-suffix_length]] = v

        self.cache_parameters = {}
        self.updateCacheParameters(params)

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_CacheParameters' \
                + '?manage_tabs_message=Parameters updated'
            REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(ManagePortlets, 'manage_resetCacheParameters')
    def manage_resetCacheParameters(self, REQUEST=None):
        """Reset cache parameters.
        """
        self.resetCacheParameters()

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_CacheParameters' \
                + '?manage_tabs_message=Cache parameters reset'
            REQUEST.RESPONSE.redirect(redirect_url)

    ######################################################################
    ######################################################################

    #
    # Cache management
    #

    security.declarePrivate('notify_event')
    def notify_event(self, event_type, object, infos):
        """Standard event hook
        """
        if self.ignore_events:
            return

        # Invalidate the portlet lookup cache at every portlet modification
        if event_type in ('portlet_create',
                          'portlet_delete',
                          'portlet_duplicate',
                          'portlet_move',
                          'portlet_insert',
                          ) or (
            getattr(aq_base(object), 'meta_type', '') == 'CPS Portlet'):
            self._invalidatePortletLookupCache()

        # we skip the events that do not inform about the object's path
        if not infos.has_key('rpath'):
            return

        object_path = '/' + infos['rpath']
        portal_type = getattr(object.aq_inner.aq_explicit, 'portal_type', None)

        # expire the portlets interested in the event
        # ZEO-aware invalidation.
        for portlet in self.listPortletsInterestedInEvent(
            event_id=event_type, folder_path=object_path,
            portal_type=portal_type):
            portlet.expireCache()

        # remove all cache entries of a user who logs out.
        if event_type == 'user_logout':
            if object is not None:
                user = object.getId()
                self.invalidateCacheEntriesByUser(user)

    def listPortletsInterestedInEvent(self, event_id, folder_path, portal_type):
        """Return the list of all portlets interested in an event given its
        event_id
        """
        returned = []
        portlets = self.listAllPortlets(event_ids=[event_id])

        # Here the portlets are already filtered by events right.
        for portlet in portlets:
            try:
                # XXX event_id is given as parameter but is useless.
                interested = portlet.isInterestedInEvent(
                    event_id=event_id, folder_path=folder_path,
                    portal_type=portal_type)
            except AttributeError:
                # Not a portlet even if it claimed to be one in its FTI
                continue
            else:
                if interested:
                    returned.append(portlet)
        return returned

InitializeClass(PortletsTool)
