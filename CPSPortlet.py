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

from types import ListType, IntType

from Globals import InitializeClass, DTMLFile
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName, _getViewFor
from Products.CMFCore.CMFCorePermissions import View

from Products.CPSDocument.CPSDocument import CPSDocument

from CPSPortletsPermissions import ManagePortlets
from PortletGuard import PortletGuard

_marker = []

class CPSPortlet(CPSDocument):
    """ CPS Portlet
    This is a CPSPortlet child base class for portlets
    """

    meta_type = 'CPS Portlet'
    portal_type = meta_type

    security = ClassSecurityInfo()
    security.declareObjectPublic()

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

        return params

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
        if type(cache_params) == type([]):
            if self.cache_params != cache_params:
                self.cache_params = cache_params

    security.declarePrivate('_setJavaScript')
    def _setJavaScript(self, javascript=''):
        """Set the javascript method.
        """
        if type(javascript) == type(''):
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

        index = ()
        for param in params:
            index_string = ''

            # current user
            if param == 'user':
                index_string = str(REQUEST.get('AUTHENTICATED_USER'))

            # XXX CPSSkins dependency
            # current language
            elif param == 'lang':
                index_string = REQUEST.get('cpsskins_language', 'en')

            # XXX CPSSkins dependency
            # current url
            elif param == 'url':
                index_string = REQUEST.get('cpsskins_url')

            # XXX CPSSkins dependency
            # CMF Actions
            elif param == 'actions':
                cmf_actions = REQUEST.get('cpsskins_cmfactions')
                index_string = md5.new(str(cmf_actions)).hexdigest()

            # XXX CPSSkins dependency
            # Workflow actions
            elif param == 'wf_actions':
                cmf_actions = REQUEST.get('cpsskins_cmfactions')
                wf_actions = cmf_actions.get('workflow', None)
                if wf_actions is not None:
                    index_string = md5.new(str(wf_actions)).hexdigest()

            # current folder
            elif param == 'folder':
                context = kw.get('context_obj')
                index_string = context.absolute_url(1)

            # portal type
            elif param == 'portal type':
                ti = context.getTypeInfo()
                if ti is not None:
                    index_string = ti.getId()

            # Workflow actions
            elif param == 'wf_create':
                wf_tool = getToolByName(self, 'portal_workflow')
                types_allowed_by_wf = wf_tool.getAllowedContentTypes(context)
                index_string = md5.new(str(types_allowed_by_wf)).hexdigest()

            if index_string:
                index += (param + '_' + index_string,)

        return index

    security.declarePublic('render_cache')
    def render_cache(self, REQUEST=None, **kw):
        """Renders the cached version of the portlet.
        """

        now = time.time()
        portlet_path = self.getPhysicalPath()
        index = (portlet_path, ) + self.getCacheIndex(**kw)
        ptltool = getToolByName(self, 'portal_cpsportlets')
        cache = ptltool.getPortletCache()
        last_cleanup = cache.getLastCleanup(id=portlet_path)
        cleanup_date = self.getCacheCleanupDate()

        # ZEO
        if last_cleanup and cleanup_date > last_cleanup:
            cache.delEntries(portlet_path)

        cache_entry = cache.getEntry(index)
        if cache_entry is None:
            rendered = self.render(**kw)
            if REQUEST is None:
                REQUEST = self.REQUEST
            user = REQUEST.get('AUTHENTICATED_USER')
            cache.setEntry(index, {'rendered': rendered,
                                   'user': user})
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

    security.declarePublic('getLocalFolder')
    def getLocalFolder(self):
        """Return the local folder (workspace, section ...)
           inside which the portlet will be displayed.
        """
        container = aq_parent(aq_inner(self))
        return aq_parent(aq_inner(container))

    security.declarePublic('getCacheCleanupDate')
    def getCacheCleanupDate(self):
        """Return the last cleanup date for this portlet"""

        return self.cache_cleanup_date

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
