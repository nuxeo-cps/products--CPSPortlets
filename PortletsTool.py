# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology <http://www.chalmers.se>
# Authors : Julien Anguenot <ja@nuxeo.com>
#           Jean-Marc Orliaguet <jmo@ita.chalmers.se>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# $Id$

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

"""Portlets Tool
"""

from zLOG import LOG, DEBUG

from Globals import InitializeClass
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from Acquisition import aq_base, aq_parent, aq_inner

from Products.CMFCore.utils import UniqueObject, getToolByName, _checkPermission
from Products.CMFCore.CMFCorePermissions import View

# XXX Remove dependency on CPSSkins
from Products.CPSSkins.RAMCache import RAMCache

from Products.CPSPortlets.PortletsContainer import PortletsContainer
from Products.CPSPortlets.CPSPortletsPermissions import ManagePortlets

PORTLET_CONTAINER_ID = '.cps_portlets'
PORTLET_RAMCACHE_ID = 'portlets'

class PortletsTool(UniqueObject, PortletsContainer):
    """ Portlets Tool
    """

    id = 'portal_cpsportlets'
    meta_type = 'CPS Portlets Tool'

    security = ClassSecurityInfo()

    # RAM Cache
    caches = {}

    security.declarePublic('listAllPortlets')
    def listAllPortlets(self):
        """List all the portlets over the portal

        Use the catalog.
        """

        # Use the catalog to get all the portlets and their identifiers
        catalog = getToolByName(self, 'portal_catalog')
        portal_types = self.listPortletTypes()

        # Lookup through catalog to get the potlets
        # We ask the tool to know all the portal_types
        portlets = catalog.searchResults({'portal_type':portal_types})

        return [x.getObject() for x in portlets]

    security.declarePublic('checkIdentifier')
    def checkIdentifier(self, identifier):
        """We need to check that the given identifier (coming from the user
        is not already in use.

        It's necessarly we want to user to be able to use the CPSSkins interface
        for creating new portlets but as well from an installer too.
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
        """
        Returns a portlet by its physical path.
        """

        for portlet in self.listAllPortlets():
            if portlet.getPhysicalPath() == portlet_path:
               return portlet

    #########################################################################

    security.declarePublic('listPortletSlots')
    def listPortletSlots(self):
        """Return all the available slots
        """

        # Slots defined within portlets defined within the tool
        slots = PortletsContainer.listPortletSlots(self)

        # Get all portlets all over the portal
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
    def getPortletContainer(self, context=None):
        """Returns the portlet container within the given context if it
        exists. Otherwise return the tool
        """
        if context is not None:
            container_id = self.getPortletContainerId()
            if getattr(aq_base(context), container_id, None) is not None:
                return getattr(context, container_id)
        return getToolByName(self, 'portal_cpsportlets')

    #######################################################################

    security.declarePublic('getPortlets')
    def getPortlets(self, context=None, slot=None, sort=1):
        """Return a list of portlets.
        """

        if context is None:
            return []

        # Find bottom-most folder:
        obj = context
        bmf = None
        while 1:
            if obj.isPrincipiaFolderish:
                bmf = obj
                break
            parent = aq_parent(aq_inner(obj))
            if not obj or parent == obj:
                break
            obj = parent
        if bmf is None:
            bmf = context

        # get portlets from the root to current path
        portal_url = getToolByName(self, 'portal_url')
        rpath = portal_url.getRelativeContentPath(bmf)
        obj = portal_url.getPortalObject()
        allportlets = []
        for elem in ('',) + rpath:
            if not elem:
                continue
            obj = getattr(obj, elem)
            allportlets.extend(self._getFolderPortlets(folder=obj, slot=slot))

        # security check
        for portlet in allportlets:
            if portlet.getGuard() and \
            not portlet.getGuard().check(getSecurityManager(), portlet, context):
                continue

        # sort the portlets
        if sort:
            def cmporder(a, b):
                return int(a.order) - int(b.order)
            allportlets.sort(cmporder)

        return allportlets

    ######################################################################

    security.declareProtected(View, 'createPortlet')
    def createPortlet(self, ptype_id, context=None, **kw):
        """Create a new portlet

        Check where it has to be created globally within the tool or locally
        within the PortletsTool. It's done byt checking the context. If context
        is None then it's global otherweise we gonne look at the context to get
        the portal ocontainer

        returns the id of the new portlet within portal_portlets or Portlet
        Container or None if something happend
        """

        # XXX possible to cope with that in a better way ?
        if not _checkPermission(ManagePortlets, context):
            raise Unauthorized(
                "You are not allowed to create portlets within %s" %(
                context.absolute_url()))

        # Check if the ptype_id is valid
        if ptype_id not in self.listPortletTypes():
            return None

        # Check where we gonna create the portlet
        if context is None:
            # Here it's within the tool
            destination = self
        else:
            container_id = self.getPortletContainerId()

            # We create the portlets container if it doesn't already exist
            if container_id not in context.objectIds():
                context.manage_addProduct['CPSPortlets'].addPortletsContainer()

            # Get the portlets container from the context
            destination = getattr(context, container_id)

        return destination._createPortlet(ptype_id, **kw)

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
            container_id = self.getPortletContainerId()
            destination = getattr(context, container_id)

        return destination._deletePortlet(portlet_id)

    security.declareProtected(View, 'movePortlet')
    def movePortlet(self, portlet=None, context=None,
                    src_slot=None, src_ypos=0,
                    dest_slot=None, dest_ypos=0, **kw):
        """Move portlet
           parameters: src_slot, src_ypos, dest_slot, dest_ypos,
        """
        if not _checkPermission(ManagePortlets, context):
            raise Unauthorized(
                "You are not allowed to move portlets inside %s" %(
                context.absolute_url()))

        src_ypos = int(src_ypos)
        dest_ypos = int(dest_ypos)
        if dest_slot is None:
            return
        if portlet is None:
            return
        self._insertPortlet(portlet=portlet, slot=dest_slot, order=dest_ypos)

    security.declareProtected(View, 'insertPortlet')
    def insertPortlet(self, portlet=None, slot=None, order=0, **kw):
        """ Insert an existing portlet inside a slot at a given order.
        """
        if not _checkPermission(ManagePortlets, portlet):
            raise Unauthorized(
                "You are not allowed to modify %s" %(
                portlet.absolute_url()))

        self._insertPortlet(portlet=portlet, slot=slot, order=order)

    #
    # RAM Cache
    #
    security.declarePublic('getPortletCache')
    def getPortletCache(self, create=0):
        """Returns the Portlet RAM cache object"""

        cacheid = PORTLET_RAMCACHE_ID
        try:
            return self.caches[cacheid]
        except KeyError:
            cache = RAMCache()
            self.caches[cacheid] = cache
            return cache

    security.declareProtected(ManagePortlets, 'clearCache')
    def clearCache(self, REQUEST=None, **kw):
        """Clear the cache."""

        portletcache = self.getPortletCache()
        if portletcache is not None:
            portletcache.invalidate()

    security.declarePublic('getCacheReport')
    def getCacheReport(self):
        """
        Returns detailed statistics about the cache.
        """

        cache = self.getPortletCache()
        if cache is None:
            return  
        return cache.getReport()

    security.declarePublic('getCacheStats')
    def getCacheStats(self):
        """
        Returns statistics about the cache.
        """

        cache = self.getPortletCache()
        if cache is None:
            return

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
        """
        Returns the list of object ids that are in the cache
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
    def invalidateCacheEntriesById(self, obid=None, REQUEST=None):
        """Removes local cache entries that match a given portlet id.
           This method can be used to clean orphaned cache entries.

           In a ZEO environment only the local RAM cache entries will be erased.
           If the portlet still exists then 'portlet.expireCache()' should be used
           instead in order to propagate the information between ZEO instances.
        """

        cache = self.getPortletCache()
        if cache is None:
            return
        cache.delEntries(obid)

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
        cdepth = self._getDepthOf(context)
        vrange = portlet.getVisibilityRange()
        left = vrange[0]
        right = vrange[1]

        # [0, 0] means visible everywhere
        if (left == right == 0 or
            right == 0 and left <= cdepth or
            left <= cdepth <= right):
            return 1
        return 0

    security.declarePrivate('_getFolderPortlets')
    def _getFolderPortlets(self, folder=None, slot=None):
        """Load all portlets in a .cps_portlets folder.
           The slot name can be used as a filter.
        """

        portlets = []
        if folder is not None:
            portlet_container = self.getPortletContainer(folder)
            for id in portlet_container.listPortletIds():
                portlet = portlet_container.getPortletById(id)
                if slot is not None:
                    if portlet.getSlot() != slot:
                        continue
                portlets.append(portlet)

        # Check the visibility range of the portlet
        returned = []
        for portlet in portlets:
            if self._isPortletVisible(portlet, folder):
                returned.append(portlet)
        return returned

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

        # sort the portlets by order
        def cmporder(a, b):
            return int(a.order) - int(b.order)
        slot_portlets.sort(cmporder)

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
            slot_portlets[k].setOrder(newpos)
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
    manage_options = (
        PortletsContainer.manage_options +
        ({'label': 'Rebuild',
          'action': 'manage_rebuildPortlets'},
         {'label': 'Cache',
          'action': 'manage_RAMCache'}, )
        )

    security.declareProtected(ManagePortlets, 'rebuild_portlets')
    def rebuild_portlets(self, REQUEST=None):
        """ """

        portlets = self.listAllPortlets()
        for portlet in portlets:
            portlet._rebuild()

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_rebuildPortlets' \
                + '?manage_tabs_message=%s Portlets rebuilt.' % len(portlets)
            REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(ManagePortlets, 'manage_clearCache')
    def manage_clearCache(self, REQUEST=None):
        """Clears the local RAM cache."""

        self.clearCache()

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_RAMCache' \
                + '?manage_tabs_message=Cache cleared'
            REQUEST.RESPONSE.redirect(redirect_url)

    security.declareProtected(ManagePortlets, 'manage_clearCacheOrphans')
    def manage_clearCacheOrphans(self, REQUEST=None):
        """Removes orphaned objects from the cache."""

        orphans = self.findCacheOrphans()
        for orphan in orphans:
            self.invalidateCacheEntriesById(orphan)

        if REQUEST is not None:
            redirect_url = self.absolute_url()\
                + '/manage_RAMCache' \
                + '?manage_tabs_message=Cache orphans removed'
            REQUEST.RESPONSE.redirect(redirect_url)

    ######################################################################

    security.declarePrivate('notify_event')
    def notify_event(self, event_type, object, infos):
        """Standard event hook
        """
        LOG(":: CPS Portlets Tool :: ", DEBUG, 'notify_event()')
        LOG(":: EVENT TYPE ::", DEBUG, event_type)
        LOG(":: OBJECT ::", DEBUG, repr(object))
        LOG(":: INFOS ::", DEBUG, repr(infos))

InitializeClass(PortletsTool)
