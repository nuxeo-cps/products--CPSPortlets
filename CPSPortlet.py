# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology
#               <http://www.chalmers.se>
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

"""CPS Portlet

This is a CPSDocument child base class for portlets
"""

import time
import md5
from random import randint
from types import ListType, IntType, TupleType, StringType
from App.Common import rfc1123_date
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName, _getViewFor
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.CPSDocument.CPSDocument import CPSDocument

from CPSPortletsPermissions import ManagePortlets
from PortletGuard import PortletGuard
from cpsportlets_utils import html_slimmer

_marker = []

# Edge-Side-Includes
ESI_CODE = """
<esi:try>
  <esi:attempt>
    <esi:include src="%s/render?context_rurl=%s" onerror="continue" />
  </esi:attempt>
  <esi:except>
    <!--esi
     This spot is reserved
    -->
  </esi:except>
</esi:try>
"""

class CPSPortlet(CPSDocument):
    """ CPS Portlet
    This is a CPSPortlet child base class for portlets
    """

    meta_type = 'CPS Portlet'
    portal_type = meta_type

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    isPrincipiaFolderish = 0

    _interesting_events = ()

    guard = None

    security.declarePublic('getGuard')
    def getGuard(self):
        return self.guard

    security.declarePublic('getTempGuard')
    def getTempGuard(self):
        """Used only by the time of using guard management form."""
        return PortletGuard().__of__(self)  # Create a temporary guard.

    security.declareProtected(ManagePortlets, 'setGuardProperties')
    def setGuardProperties(self, props={}, REQUEST=None):
        """Postprocess guard values."""
        if REQUEST is not None:
            # XXX Using REQUEST itself should work.
            # but update is complaining it is not a dictionary
            props.update(REQUEST.form)

        # XXX found we must create a new instance every time.
        # not that much resource friendly...
        self.guard = PortletGuard()
        self.guard.changeFromProperties(props)

        if REQUEST is not None:
            return self.manage_guardForm(REQUEST,
                management_view='Guard',
                manage_tabs_message='Guard setting changed.')

    security.declarePublic('SearchableText')
    def SearchableText(self):
        """ We don't index CPS Portlets

        No Searchable Text on here
        """
        return ""

    security.declarePublic('isCPSPortlet')
    def isCPSPortlet(self):
        """Return true if this is a CPS Portlet.
        """
        return 1

    security.declareProtected(View, 'edit_form')
    def edit_form(self, **kw):
        """
        Call the edit action.
        """

        action = _getViewFor(self, view='edit')
        if action and callable(action):
            return apply(action, (), kw)
        return None

    #################################################################
    # RAM Cache
    #################################################################
    security.declarePublic('getCustomCacheParams')
    def getCustomCacheParams(self):
        """Returns the custom cache parameters.
        """

        params = []
        # i18n
        if self.isI18n():
            params.append('lang')

        # explicit custom cache parameters
        if getattr(aq_base(self), 'custom_cache_params', None) is not None:
            params.extend(self.custom_cache_params)

        return params

    security.declareProtected(ManagePortlets, 'setCustomCacheParams')
    def setCustomCacheParams(self, params=[]):
        """Set custom cache parameters
        """
        if getattr(aq_base(self), 'custom_cache_params', None) is not None:
            if isinstance(params, ListType):
                self.custom_cache_params = params

    security.declarePublic('getCacheParams')
    def getCacheParams(self):
        """Get the cache parameters that will be used to compute the
           cache index.
        """
        return self.cache_params[:]

    security.declarePrivate('_setCacheParams')
    def _setCacheParams(self, cache_params=[]):
        """Set the cache parameters
        """
        if isinstance(cache_params, ListType):
            if self.cache_params != cache_params:
                self.cache_params = cache_params

    security.declarePrivate('_setJavaScript')
    def _setJavaScript(self, javascript=''):
        """Set the javascript method.
        """
        if isinstance(javascript, StringType):
            if self.javascript != javascript:
                self.javascript = javascript

    security.declareProtected(ManagePortlets, 'expireCache')
    def expireCache(self):
        """Expires the cache for this Portlet.
           In a ZEO environment, the information will propagate
           between all ZEO instances as long as the portlet has not been
           removed.
        """
        self.cache_cleanup_date = time.time()

    security.declarePublic('getCacheObjects')
    def getCacheObjects(self, REQUEST=None, **kw):
        """Returns the list of cache objects.
        """

        context = kw.get('context_obj')

        params = self.getCacheParams()
        custom_params = self.getCustomCacheParams()
        params.extend(custom_params)

        def getOptions(p):
            """extract cache parameter options
            """
            res = []
            for o in p.split(':')[1].split(','):
                if o[0] == '(' and o[-1] == ')':
                    o = getattr(self, o[1:-1], None)
                    if o is None:
                        continue
                    if isinstance(o, ListType) or\
                       isinstance(o, TupleType):
                        res.extend(o)
                        continue
                res.append(str(o))
            return res

        objects = []
        for param in params:
            if param.startswith('objects:'):
                opts = getOptions(param)
                for opt in opts:

                    # relative path objects
                    if opt == 'relative_path':
                        objs = self.getRelativeContentObjects(context)
                        if len(objs) > 0:
                            objects.extend(objs)

                    # context
                    elif opt == 'context':
                        objects.append(context.getPhysicalPath())

                    # list of paths
                    else:
                        objects.append(tuple(opt.split('/')))

        return objects

    security.declarePublic('getCacheIndex')
    def getCacheIndex(self, REQUEST=None, **kw):
        """Returns the RAM cache index as a tuple (var1, var2, ...)
        """

        if REQUEST is None:
            REQUEST = self.REQUEST

        context = kw.get('context_obj')

        params = self.getCacheParams()
        custom_params = self.getCustomCacheParams()
        params.extend(custom_params)

        def getOptions(p):
            """extract cache parameter options
            """
            res = []
            for o in p.split(':')[1].split(','):
                if o[0] == '(' and o[-1] == ')':
                    o = getattr(self, o[1:-1], None)
                    if o is None:
                        continue
                    if isinstance(o, ListType) or\
                       isinstance(o, TupleType):
                        res.extend(o)
                        continue
                res.append(str(o))
            return res

        index = ()
        data = {}
        for param in params:
            index_string = ''
            prefix = param

            # not cacheable
            if param == 'no-cache':
                return None, data

            # random integer
            elif param.startswith('random:'):
                opts = getOptions(param)
                index_string = ''
                prefix = 'random'
                for opt in opts:
                    value = opt
                    if value is None:
                        continue
                    value = int(value)
                    if value <= 1:
                        continue
                    random_int = randint(0, value-1)
                    index_string += str(random_int)
                    data['random_int'] = random_int

            # request variable
            elif param.startswith('request:'):
                opts = getOptions(param)
                index_string = ''
                prefix = 'request'
                for opt in opts:
                    index_string += '_' + opt + ':'
                    value = REQUEST.get(opt)
                    if value is None:
                        continue
                    index_string += str(value)

            # current user
            elif param == 'user':
                index_string = str(REQUEST.get('AUTHENTICATED_USER'))

            # XXX CPSSkins dependency
            # current language
            elif param == 'current_lang':
                index_string = REQUEST.get('cpsskins_language', 'en')

            # XXX CPSSkins dependency
            # current url
            elif param == 'url':
                index_string = REQUEST.get('cpsskins_url')

            # XXX CPSSkins dependency
            # CMF Actions
            elif param == 'actions':
                cmf_actions = REQUEST.get('cpsskins_cmfactions')
                if cmf_actions:
                    index_string = md5.new(str(cmf_actions)).hexdigest()

            elif param.startswith('actions:'):
                prefix = 'actions'
                cmf_actions = REQUEST.get('cpsskins_cmfactions')
                if cmf_actions:
                    categories = getOptions(param)
                    actions = [cmf_actions[x] for x in categories \
                               if cmf_actions.has_key(x)]
                    index_string = md5.new(str(actions)).hexdigest()

            # XXX CPSSkins dependency
            # Workflow actions
            elif param == 'wf_actions':
                cmf_actions = REQUEST.get('cpsskins_cmfactions')
                wf_actions = cmf_actions.get('workflow', None)
                if wf_actions is not None:
                    index_string = md5.new(str(wf_actions)).hexdigest()

            # current object
            elif param.startswith('object:'):
                opts = getOptions(param)
                index_string = ''
                prefix = 'object'
                for opt in opts:
                    # object's published path
                    # including the method used to access the object
                    index_string += '_' + opt + ':'
                    if opt == 'published_path':
                        index_string += REQUEST.get('PATH_TRANSLATED')

                    # object's physical path
                    if opt == 'path':
                        index_string += '/'.join(context.getPhysicalPath())

                    # object's languages
                    if opt == 'langs':
                        if getattr(aq_base(context), 'getLanguageRevisions',
                                   _marker) is not _marker:
                            revs = context.getLanguageRevisions()
                            index_string += str(revs.keys())

                    # object's default language
                    if opt == 'lang':
                        if getattr(aq_base(context), 'getDefaultLanguage',
                                   _marker) is not _marker:
                            index_string += context.getDefaultLanguage()

            # portal type
            elif param == 'portal_type':
                ti = context.getTypeInfo()
                if ti is not None:
                    index_string = ti.getId()

            # Workflow actions
            elif param == 'wf_create':
                wf_tool = getToolByName(self, 'portal_workflow')
                getAllowedTypes = getattr(wf_tool,
                                          'getAllowedContentTypes', None)
                if getAllowedTypes is not None:
                    types_allowed_by_wf = getAllowedTypes(context)
                    index_string = md5.new(str(types_allowed_by_wf)).hexdigest()
            if index_string:
                index += (prefix + '_' + index_string,)

        return index, data

    security.declarePublic('render_cache')
    def render_cache(self, REQUEST=None, **kw):
        """Renders the cached version of the portlet.
        """

        cache_index, data = self.getCacheIndex(**kw)
        kw.update(data)
        # the portlet is not cacheable.
        if cache_index is None:
            return self.render(**kw)

        now = time.time()
        portlet_path = self.getPhysicalPath()
        index = (portlet_path, ) + cache_index
        ptltool = getToolByName(self, 'portal_cpsportlets')
        cache = ptltool.getPortletCache()
        # last_cleanup: the date when all the cache entries associated to the
        # portlet were last removed from the cache
        last_cleanup = cache.getLastCleanup(id=portlet_path)
        # cleanup_date: the portlet's cleanup date (ZEO-aware).
        cleanup_date = self.getCacheCleanupDate()
        # cache timeout
        timeout = self.getCacheTimeout()

        # remove all cache entries associated to this portlet.
        # This will occur on all ZEO instances (lazily).
        if cleanup_date > last_cleanup:
            cache.delEntries(portlet_path)

        if last_cleanup is not None:
            # cache timeout
            if timeout > 0:
                if now > last_cleanup + timeout:
                    cache.delEntries(portlet_path)

        cache_entry = cache.getEntry(index)
        # compare the cache entry creation date with the modification date
        # of cached objects. The cache entry is considered invalid if any one
        # of the cache objects were modified after the cache entry creation
        # date.
        if cache_entry is not None:
            creation_date = cache_entry['date']
            for obj_path in cache_entry['objects']:
                obj = self.unrestrictedTraverse(obj_path, default=None)
                if obj is not None:
                    mtime = getattr(obj, '_p_mtime', None)
                    if mtime is not None and mtime < creation_date:
                        continue
                # the entry is not longer valid
                cache_entry = None
                break

        # create / recreate the cache entry
        if cache_entry is None:
            rendered = html_slimmer(self.render(**kw))
            now = time.time()

            if REQUEST is None:
                REQUEST = self.REQUEST
            RESPONSE = REQUEST.RESPONSE

            # set the HTTP headers to inform proxy caches (Apache, Squid, ...)
            # that the page has expired.
            RESPONSE.setHeader('Expires', rfc1123_date(now))
            RESPONSE.setHeader('Last-Modified', rfc1123_date(now))
            # XXX more headers?

            # current user if the cache entry is user-dependent
            if 'user' in self.getCacheParams():
                user = REQUEST.get('AUTHENTICATED_USER')
            else:
                user = ''

            # get the list of cache objects.
            cache_objects = self.getCacheObjects(**kw)

            # set the new cache entry
            cache.setEntry(index, {'rendered': rendered,
                                   'user': user,
                                   'date': now,
                                   'objects': cache_objects,
                                  })
        # use the existing cache entry
        else:
            rendered = cache_entry['rendered']

        return rendered

    security.declarePublic('render_js')
    def render_js(self, **kw):
        """Render the javascript code used by the portlet.
        """

        rendered = ''
        js_meth = self.getJavaScript()
        if js_meth:
            meth = getattr(self, js_meth, None)
            if meth and callable(meth):
                rendered = apply(meth, (), kw)
        return rendered

    security.declarePublic('render_esi')
    def render_esi(self, **kw):
        """Render the ESI fragment code."""

        utool = getToolByName(self, 'portal_url')
        context_obj = kw.get('context_obj')
        context_rurl = utool.getRelativeUrl(context_obj)
        return ESI_CODE % (self.absolute_url(), context_rurl)

    ##################################################################

    security.declarePublic('getCreator')
    def getCreator(self):
        """Return the name of the portlet's creator.
        """
        return self.Creator

    ##################################################################

    security.declarePublic('getURL')
    def getURL(self):
        """Return the url of the portlet.
        """
        return self.absolute_url()

    security.declarePublic('getRelativeUrl')
    def getRelativeUrl(self):
        """Return the url of the portlet relative to the portal.
        """
        utool = getToolByName(self, 'portal_url')
        return utool.getRelativeUrl(self)

    security.declarePublic('getRelativePath')
    def getRelativePath(self):
        """Return the url of the portlet relative to the portal.
        """
        utool = getToolByName(self, 'portal_url')
        return utool.getRelativeContentPath(self)

    security.declarePublic('getPath')
    def getPath(self):
        """Return the physical path of the portlet.
        """
        return self.getPhysicalPath()

    security.declarePublic('isLocal')
    def isLocal(self):
        """Return true if the portlet is a local portlet.
        """
        rurl = self.getRelativeUrl()
        if rurl is not None and rurl.startswith('portal_cpsportlets'):
            return 0
        return 1

    security.declarePublic('isGlobal')
    def isGlobal(self):
        """Return true if the portlet is a global portlet.
        """

        return not self.isLocal()

    security.declarePublic('getLocalFolder')
    def getLocalFolder(self):
        """Return the local folder (workspace, section ...)
           inside which the portlet will be displayed.
        """

        if self.isGlobal():
            return None
        container = aq_parent(aq_inner(self))
        return aq_parent(aq_inner(container))

    security.declarePublic('getCacheCleanupDate')
    def getCacheCleanupDate(self):
        """Return the last cleanup date for this portlet"""

        return self.cache_cleanup_date

    security.declarePublic('getCacheTimeout')
    def getCacheTimeout(self):
        """Return the cache timeout"""

        return self.cache_timeout

    security.declarePublic('getPortletType')
    def getPortletType(self):
        """Return the portlet's type"""

        ti = self.getTypeInfo()
        if ti is not None:
            return ti.getId()
        return None

    #################################################################

    security.declarePublic('getDepth')
    def getDepth(self):
        """Return the portlet's relative depth.
        """

        return len(self.getRelativePath()) - 2

    security.declarePublic('getVisibilityRange')
    def getVisibilityRange(self):
        """Visibility range for this portlet
        """
        return self.visibility_range[:]

    security.declareProtected(ManagePortlets, 'setVisibilityRange')
    def setVisibilityRange(self, range):
        """Set the visiblity range

        The validation is a little bit stronger in here.
        We need integer values.
        """
        if (isinstance(range, ListType) and
            len(range) == 2 and
            isinstance(range[0], IntType) and
            isinstance(range[1], IntType)):
            try:
                self.edit(visibility_range=range)
                return 0
            except ValueError:
                pass
        return 1

    #################################################################

    security.declarePublic('getJavaScript')
    def getJavaScript(self):
        """Return the javascript method name.
        """

        # custom javascript method
        custom_js_meth = getattr(aq_base(self), 'js_render_method', None)
        if custom_js_meth:
            return custom_js_meth

        return self.javascript

    #################################################################

    security.declarePublic('getSlot')
    def getSlot(self):
        """Return the portlet's slot.
        """
        return self.slot

    security.declareProtected(ManagePortlets, 'setSlot')
    def setSlot(self, slot_name=''):
        """Set the slot value
        """
        if slot_name:
            self.edit(slot=slot_name)
            return 0
        return 1

    #################################################################
    security.declarePublic('iI18n')
    def isI18n(self):
        """Return True if the portlet's content ought to be translated.
        """
        return self.i18n

    #################################################################

    security.declarePublic('getOrder')
    def getOrder(self):
        """Return the portlet's order.
        """
        return self.order

    security.declareProtected(ManagePortlets, 'setOrder')
    def setOrder(self, order=0):
        """Set order

        0 is the default value
        """
        self.edit(order=order)

    #################################################################

    security.declarePublic('getTitle')
    def getTitle(self):
        """Return the portlet's title (or id)
        """
        return self.title_or_id()

    #################################################################

    security.declarePublic('getState')
    def getState(self):
        """Return the portlet's state
           (minimized, maximized, closed ...)
           default is 'maximized'
        """
        state = self.state
        if not state:
            state = 'maximized'
        return state

    security.declareProtected(ManagePortlets, 'setState')
    def setState(self, state=''):
        """Set the portlet's state
        """
        self.edit(state=state)

    #################################################################
    # Cache / Events
    #################################################################

    security.declareProtected(ModifyPortalContent, 'addEvent')
    def addEvent(self, event_ids=(), folder_paths=(), portal_types=()):
        """Add an event to the list of interesting events
        """

        # Check the existence cause it's not on the schema
        if not getattr(aq_base(self), '_interesting_events', 0):
            self.clearEvents()

        # Add the event if not already here
        if (event_ids, folder_paths, portal_types) not in self.listEvents():
            self._interesting_events += ((event_ids,
                                          folder_paths,
                                          portal_types), )
            return 0
        return 1

    security.declareProtected(ModifyPortalContent, 'clearEvents')
    def clearEvents(self):
        """Clear the list of interesting events
        """

        self._interesting_events = ()

    security.declareProtected(View, 'listEvents')
    def listEvents(self):
        """List all events the portlets is interested about
        """
        return self._interesting_events

    security.declareProtected(View, 'isInterestedInEvent')
    def isInterestedInEvent(self, event_id='', folder_path='', portal_type=''):
        """Check whether the portlet is interested in an event
        """

        interested = 0
        for event in self.listEvents():
            ids = event[0]
            paths = event[1]
            ptypes = event[2]

            if len(ids) > 0:
                if event_id and event_id not in ids:
                    continue

            if len(paths) > 0:
                if folder_path:
                    found = 0
                    for path in paths:
                        if folder_path.startswith(path):
                            found = 1
                            break
                    if not found:
                        continue

            if len(ptypes) > 0:
                if portal_type and portal_type not in ptypes:
                    continue

            interested = 1
            break
        return interested

    security.declarePrivate('sendEvent')
    def sendEvent(self, **kw):
        """Subscriber send an event to the portlet.

        The portlet is gonna check if whether or not he reacts.
        """
        if self.isInterestedInEvent(**kw):
            # XXX
            return 0
        return 1

    #
    # Cache objects
    #
    security.declarePrivate('getRelativeContentObjects')
    def getRelativeContentObjects(self, obj=None):
        """Return the relative content objects from the current object to
           the portal object.
        """

        if obj is None:
            return []

        utool = getToolByName(self, 'portal_url')
        portal = utool.getPortalObject()

        objs = []
        while 1:
            objs.append(obj.getPhysicalPath())
            if obj == portal:
                break
            try:
                obj = aq_parent(aq_inner(obj))
            except AttributeError:
                break
        return objs

    #################################################################
    # Private
    #################################################################

    security.declarePrivate('_rebuild')
    def _rebuild(self):
        """Rebuilds the portlet.
        """

        # rebuild properties
        stool = getToolByName(self, 'portal_schemas')
        existing_schemas = stool.objectIds()
        ti = self.getTypeInfo()
        for type_schema in ti._listSchemas():
            schema_id = type_schema.getId()
            if schema_id not in existing_schemas:
                continue
            schema = stool[schema_id]
            for field in schema.objectValues():
                field_id = field.getFieldId()
                # the attribute exists
                if getattr(aq_base(self), field_id, _marker) is not _marker:
                    continue
                default_value = field.getDefault()
                setattr(self, field_id, default_value)

        ptype_id = ti.getId()
        # reset cache parameters
        cache_params_dict = self.getCPSPortletCacheParams()
        if cache_params_dict.has_key(ptype_id):
            self._setCacheParams(cache_params_dict[ptype_id])
        # reset the javascript methods
        javascript_dict = self.getCPSPortletJavaScript()
        if javascript_dict.has_key(ptype_id):
            self._setJavaScript(javascript_dict[ptype_id])

        self.resetInterestingEvents(ptype_id)

    security.declareProtected(ManagePortlets, 'resetInterestingEvents')
    def resetInterestingEvents(self, ptype_id=None):
        """ Reset the list of interesting events
            based on the portlet's settings
        """

        if ptype_id is None:
            return
        cache_params_dict = self.getCPSPortletCacheParams()
        if not cache_params_dict.has_key(ptype_id):
            return

        def getOptions(p):
            """extract cache parameter options
            """
            res = []
            for o in p.split(':')[1].split(','):
                if not o:
                    continue
                if o[0] == '(' and o[-1] == ')':
                    o = getattr(self, o[1:-1], None)
                    if o is None:
                        continue
                    if isinstance(o, ListType) or\
                       isinstance(o, TupleType):
                        res.extend(o)
                        continue
                res.append(str(o))
            return res

        event_ids = ()
        folder_paths = ()
        portal_types = ()
        for param in cache_params_dict[ptype_id]:
            # event ids
            if param.startswith('event_ids:'):
                event_ids = getOptions(param)

            # folders in which the event occurs
            if param.startswith('event_in_folders:'):
                folder_paths = getOptions(param)

            # portal types on which the event occurs
            if param.startswith('event_on_types:'):
                portal_types = getOptions(param)

        self.clearEvents()
        self.addEvent(event_ids=event_ids,
                      folder_paths=folder_paths,
                      portal_types=portal_types)

    #################################################################
    # ZMI
    #################################################################

    security.declareProtected(ManagePortlets, 'manage_guardForm')
    manage_guardForm = DTMLFile('zmi/manage_guardForm', globals())

    manage_options = (CPSDocument.manage_options +
                      ({'label': 'Guard', 'action': 'manage_guardForm'},)
                     )

InitializeClass(CPSPortlet)

def addCPSPortlet(container, id, REQUEST=None, **kw):
    """Add a bare CPS Portlet.

    The object doesn't have a portal_type yet, so we have no way to know
    its schema. This simply constructs a bare instance.
    """
    ob = CPSPortlet(id, **kw)
    container._setObject(id, ob)
    if REQUEST:
        ob = container._getOb(id)
        REQUEST.RESPONSE.redirect(ob.absolute_url()+'/manage_main')
