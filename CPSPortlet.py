# Copyright (c) 2004-2007 Nuxeo SAS <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology
#               <http://www.chalmers.se>
# Authors:
# Julien Anguenot <ja@nuxeo.com>
# Jean-Marc Orliaguet <jmo@ita.chalmers.se>
# M.-A. Darche <madarche@nuxeo.com>
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

"""CPS Portlet

This is a CPSDocument child base class for portlets
"""

import logging
import sys
import time
import md5
from copy import deepcopy
from cgi import escape
from random import randint

from zope.interface import Interface
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserView

from App.Common import rfc1123_date
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo

logger = logging.getLogger('Products.CPSPortlets.CPSPortlet')


from zope.tales.tales import CompilerError
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CPSUtil.conflictresolvers import IncreasingDateTime
from Products.CPSUtil.resourceregistry import JSGlobalMethodResource
from Products.CPSUtil.resourceregistry import require_resource
from Products.CPSUtil.crashshield import shield_apply
from Products.CPSUtil.crashshield import CrashShieldException
from Products.CPSCore.utils import bhasattr
from Products.CPSCore.ProxyBase import FileDownloader
from Products.CPSDocument.CPSDocument import CPSDocument

from CPSPortletsPermissions import ManagePortlets
from PortletGuard import PortletGuard
from CPSPortletCatalogAware import CPSPortletCatalogAware
from cpsportlets_utils import html_slimmer

from zope.interface import implements
from Products.CPSPortlets.interfaces import ICPSPortlet
from browser.traversal import request_context_obj

PORTLET_RESOURCE_CATEGORY = 'portlet'

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

MINIMAL_ESI_CODE = """
<esi:include src="%s/render?context_rurl=%s" onerror="continue" />
"""

VISIBILITY_VOC = 'cpsportlets_visibility_range_voc'
KEYWORD_DOWNLOAD_FILE = 'downloadFile'
REQUEST_TRAVERSAL_KEY = '_portlet_traversal'

def noadapter(datamodel, request):
    """An adapter factory used as a kind of base of adaptation of datamodel
    and request."""

    return

class CPSPortlet(CPSPortletCatalogAware, CPSDocument):
    """ CPS Portlet
    This is a CPSPortlet child base class for portlets
    """

    implements(ICPSPortlet)

    meta_type = 'CPS Portlet'
    portal_type = meta_type

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    isPrincipiaFolderish = 0

    _interesting_events = ()

    guard = None

    slot = ''

    _properties = ({'id': 'slot', 'mode': 'w', 'type': 'string',
                    'label': 'Slot'},
                   {'id': 'order', 'mode': 'w', 'type': 'string',
                    'label': 'Order in the slot'},
                   )

    security.declarePublic('getGuard')
    def getGuard(self):
        return self.guard

    security.declarePublic('getTempGuard')
    def getTempGuard(self):
        """Used only by the time of using guard management form."""
        return PortletGuard().__of__(self)  # Create a temporary guard.

    security.declarePublic('renderGuardForm')
    def renderGuardForm(self):
        """Render the guard form"""
        guard = self.getGuard() or self.getTempGuard()
        if guard is not None:
            return guard.guardForm()
        return ''

    security.declarePublic('guardExprDocs')
    def guardExprDocs(self):
        """Render the guard expression documentation"""
        return self.cpsportlet_guard_tales_help()

    security.declareProtected(ManagePortlets, 'setGuardProperties')
    def setGuardProperties(self, props=None, from_portlet_editor=True,
                           REQUEST=None):
        """Postprocess guard values.

        from_portlet_editor is to specify if this method is called from the
        portlet editor or the ZMI, which will be used for the returned page.
        """
        if REQUEST is not None:
            # XXX Using REQUEST itself should work.
            # but update is complaining it is not a dictionary
            if props is None:
                props = {}
            props.update(REQUEST.form)

        # XXX found we must create a new instance every time.
        # not that much resource friendly...
        self.guard = PortletGuard()

        psm = err = ''
        try:
            self.guard.changeFromProperties(props)
        except CompilerError, e:
            logger.warn('setGuardProperties \"%s\" => %s: %s',
                        props, sys.exc_info()[0], e)
            psm = 'cpsportlet_psm_guard_error'
            err = e

        if REQUEST is not None:
            if from_portlet_editor:
                psm = psm or 'cpsportlet_psm_settings_updated'
                return self.cpsportlet_guard(REQUEST,
                                             portal_status_message=psm, err=err)
            else:
                psm = 'Guard setting changed.'
                return self.manage_guardForm(REQUEST,
                                             management_view='Guard',
                                             manage_tabs_message=psm)

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

    #################################################################
    # RAM Cache
    #################################################################
    security.declarePublic('getCustomCacheParams')
    def getCustomCacheParams(self):
        """Returns the custom cache parameters.
        """

        if getattr(aq_base(self), 'custom_cache_params', None) is not None:
            return self.custom_cache_params
        return []

    security.declareProtected(ManagePortlets, 'setCustomCacheParams')
    def setCustomCacheParams(self, params=[]):
        """Set custom cache parameters
        """
        if getattr(aq_base(self), 'custom_cache_params', None) is not None:
            if isinstance(params, list):
                self.custom_cache_params = params

    security.declarePublic('getCacheParams')
    def getCacheParams(self):
        """Get the cache parameters that will be used to compute the
           cache index.
        """
        ptltool = getToolByName(self, 'portal_cpsportlets')
        params = ptltool.getCacheParametersFor(ptype_id=self.portal_type)
        # parameters set on the fly: i18n
        if getattr(self, 'i18n', 0):
            params.append('current_lang')
        params.extend(self.getCustomCacheParams())
        return params

    security.declareProtected(ManagePortlets, 'resetCacheTimeout')
    def resetCacheTimeout(self):
        """Reset cache cache timeout
        """
        self._setCacheTimeout(self.getCacheParams())

    security.declarePrivate('_setCacheTimeout')
    def _setCacheTimeout(self, cache_params=[]):
        """Set the cache parameters
        """
        # set the cache timeout value based on cache paramaters

        timeout = None
        for param in cache_params:
            if not param.startswith('timeout:'):
                continue
            idx, value = param.split(':')
            try:
                timeout = int(value)
            except ValueError:
                pass

        if timeout is None:
            return
        if timeout >= 0 and self.cache_timeout != timeout:
            self.cache_timeout = timeout

    security.declarePrivate('_setJavaScript')
    def _setJavaScript(self, javascript=''):
        """Set the javascript method.
        """
        if isinstance(javascript, str):
            if self.javascript != javascript:
                self.javascript = javascript

    security.declareProtected(ManagePortlets, 'expireCache')
    def expireCache(self):
        """Expires the cache for this Portlet.
           In a ZEO environment, the information will propagate
           between all ZEO instances as long as the portlet has not been
           removed.
        """
        self.getCacheCleanupDate().set(time.time())

    security.declarePublic('getCacheObjects')
    def getCacheObjects(self, **kw):
        """Returns the list of cache objects.
        """

        context = kw.get('context_obj')
        params = self.getCacheParams()

        def getOptions(p):
            """Extract cache parameter options
            """
            res = []
            for o in p.split(':')[1].split(','):
                if o[0] == '(' and o[-1] == ')':
                    o = getattr(self, o[1:-1], None)
                    if o is None:
                        continue
                    if isinstance(o, (list, tuple)):
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

        def getOptions(p):
            """extract cache parameter options
            """
            res = []
            for o in p.split(':')[1].split(','):
                if o[0] == '(' and o[-1] == ')':
                    o = getattr(aq_base(self), o[1:-1], None)
                    if o is None:
                        continue
                    if isinstance(o, (list, tuple)):
                        res.extend(o)
                        continue
                    if isinstance(o, int):
                        res.append(o)
                        continue
                res.append(str(o))
            return res

        index = ()
        data = {}
        for param in params:
            index_string = ''
            prefix = param

            # Not cacheable
            if param == 'no-cache':
                return None, data

            # Disable the cache is a field value is True
            elif param.startswith('no-cache:'):
                opts = getOptions(param)
                for opt in opts:
                    if opt:
                        return None, data

            # Random integer
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

            # Request variable
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

            # Current user
            elif param == 'user':
                index_string = str(REQUEST.get('AUTHENTICATED_USER', ''))

            # Current language
            elif param == 'current_lang':
                index_string = REQUEST.get('cpsskins_language', 'en')

            # Current URL
            # Examples:
            # "http://mysite.net", "http://localhost:8080/cps"
            elif param == 'url':
                index_string = REQUEST.get('cpsskins_url')

            # Server URL
            # Examples:
            # http://localhost:8080
            # http://mymachinename:8080
            # http://mysite.net
            # https://mysite.net
            elif param == 'server_url':
                index_string = REQUEST.get('SERVER_URL', '')

            # Current baseurl, that is the absolute path to the base or root
            # of the portal as seen from the client.
            # The baseurl name is misleading, it isn't in any way an URL.
            # Examples: "/" or "/cps"
            elif param == 'baseurl':
                index_string = REQUEST.get('cps_base_url')

            # Protocol
            # Deprecated in favor or server_url
            elif param == 'protocol':
                url = REQUEST.get('SERVER_URL', '')
                pos = url.find('://')
                if pos > 0:
                    index_string = url[:pos]

            # CMF Actions by categories
            elif param.startswith('actions:'):
                prefix = 'actions'
                cmf_actions = REQUEST.get('cpsskins_cmfactions')
                if cmf_actions:
                    ac_list = []
                    ac_list_extend = ac_list.extend
                    for cat in getOptions(param):
                        if not cmf_actions.has_key(cat):
                            continue
                        for ac in cmf_actions[cat]:
                             ac_list_extend([ac.get('name'), ac.get('url')])
                    index_string = md5.new(str(ac_list)).hexdigest()

            # Current object
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

            # Portal type
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

        index += (kw.get('view_name', ''),)
        return index, data

    def getBrowserView(self, context_obj, request, render_kwargs=None,
                       view_name=''):
        """Lookup a browser view and prepare it.

        context_obj is passed explicitely although it's usually
        in render_kwargs for the sake of expliciteness and possible later
        refactors
        """
        if render_kwargs is None:
            render_kwargs = {}
        # store before resolution for cache params
        render_kwargs['requested_view_name'] = view_name
        dm = self.getDataModel(context=context_obj)
        if not view_name:
            view_name = dm['render_view_name']
        view = queryMultiAdapter((dm, request), Interface, name=view_name)

        # There might be non-view adapters for datamodel
        # One gets one of these usually if there's no proper defined view
        # because views adapt to Interface and therefore must be queried to
        # Interface, and that is quite broad.
        # We try to be protected from that by the baseline browser.no_view
        # adapter factory (returns None), but one never knows.
        if view is None or not IBrowserView.providedBy(view):
            return
        render_kwargs.setdefault('context_obj', context_obj)
        view.render_kwargs = render_kwargs
        return view

    security.declarePublic('render')
    def render(self, REQUEST=None, layout_mode='view', **kw):
        """Place holder to keep tests happy.

        This could be removed if tests called the now proper render_headers()
        for the main rendering, and render() would become the CPSDocument
        method again (TODO)
        """
        if layout_mode == 'view':
            return self.render_headers(REQUEST, **kw)[0]
        return super(CPSPortlet, self).render(REQUEST=REQUEST,
                                              layout_mode=layout_mode, **kw)

    security.declarePublic('render_headers')
    def render_headers(self, request, layout_mode='view',
                       view_name='', view=None, whole_response=False, **kw):
        """Render and set headers through a Z3 view or CPSDocument machinery

        The view name is read in the 'render_view_name' field.
        Return rendered, headers
        """

        if 'portlet' not in kw:
            # cf #2078, CPSSkins puts it in kw, CPSDesignerThemes won't
            kw['portlet'] = self
        self.registerRequireJavaScript()

        context_obj = kw.get('context_obj')
        if context_obj is None:
            context_obj = request_context_obj(self, request)
            kw['context_obj'] = context_obj

        if view is None:
            view = self.getBrowserView(context_obj, request,
                                       view_name=view_name, render_kwargs=kw)

        if view is not None:
            if whole_response:
                view.whole_response = True
            view.prepare()
            headers = None
            if whole_response:
                headers = view.responseHeaders()
                response = request.RESPONSE
                for name, value in headers.items():
                    response.setHeader(name, value)
            return view(), headers # TODO method views ?

        # defaulting to CPSDocument machinery
        return super(CPSPortlet, self).render(
            layout_mode='view', REQUEST=request, **kw), None


    def render_headers_shield(self, REQUEST, **kw):
        """Render with headers and crashshield protection.

        This is for view mode renderings only (be it ZTK-style or old
        CPSDocument style)
        """
        if getToolByName(self, 'portal_cpsportlets').shield_disabled:
            return self.render_headers(REQUEST, **kw)

        try:
            __traceback_info__="portlet id: " + self.getId()
            return shield_apply(self, 'render_headers', REQUEST, **kw)
        except CrashShieldException:
            return '<blink>!!!</blink>', None

    security.declarePublic('render_cache')
    def render_cache(self, REQUEST=None, **kw):
        """Renders the cached version of the portlet.
        """

        cache_index, data = self.getCacheIndex(**kw)
        kw.update(data)

        # Non cacheable cases
        if cache_index is not None:
            ptltool = getToolByName(self, 'portal_cpsportlets')
            if ptltool.render_cache_disabled:
                cache_index = None

        if REQUEST is None:
            REQUEST = self.REQUEST

        if cache_index is None:
            return self.render_headers_shield(REQUEST, **kw)[0]

        portlet_path = self.getPhysicalPath()
        index = (portlet_path, ) + cache_index
        cache = ptltool.getPortletCache()

        # Time-based invalidations.
        # Theres a flat timeout. Also We compare latest cleanup times :
        # ZEO client local (from RAM) vs global accross ZEO cluster (from ZODB)
        # global > local means that another client has invalidated. So must we.
        now = time.time()
        timeout = self.getCacheTimeout()
        client_cleanup_time = cache.getLastCleanup(id=portlet_path)
        global_cleanup_time = self.getCacheCleanupDate().value

        if (client_cleanup_time is None or
            global_cleanup_time is None or
            global_cleanup_time > client_cleanup_time or
            (timeout > 0 and now > client_cleanup_time + timeout)):
            # This also sets client cleanup date
            cache.delEntries(portlet_path)
            cache_entry = None
        else:
            cache_entry = cache.getEntry(index)

        # The cache entry is considered invalid if any cached objects has been
        # modified after the cache entry creation date.
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

        if cache_entry is not None:
            headers = cache_entry['headers']
            if headers is not None:
                response = REQUEST.RESPONSE
                for name, value in headers.items():
                    response.setHeader(name, value)
            return cache_entry['rendered']

        # From now, this is a cache miss: render and set in cache

        logger.debug("Cache miss for portlet %s (type=%s)",
                     self, self.portal_type)
        rendered, headers = self.render_headers_shield(REQUEST, **kw)

        # TODO provide Last-Modified and Expires if not already set

        # we'll associate to current user if the cache entry is user-dependent
        if 'user' in self.getCacheParams():
            user = str(REQUEST.get('AUTHENTICATED_USER', ''))
        else:
            user = ''

        cache.setEntry(index, {'rendered': rendered,
                               'user': user,
                               'date': now,
                               'headers': headers,
                               'objects': self.getCacheObjects(**kw)
                              })

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

    def registerRequireJavaScript(self):
        js_method = self.getJavaScript()
        if not js_method:
            return
        rid = JSGlobalMethodResource.register(str(js_method)) # avoid unicode
        require_resource(rid, category=PORTLET_RESOURCE_CATEGORY, context=self)

    security.declarePublic('render_esi')
    def render_esi(self, **kw):
        """Render the ESI fragment code."""

        utool = getToolByName(self, 'portal_url')
        context_obj = kw.get('context_obj')
        context_rurl = utool.getRelativeUrl(context_obj)
        if kw.get(esi_minimal):
            return MINIMAL_ESI_CODE % (self.absolute_url(), context_rurl)
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
        """Return the last cleanup date for this portlet.
        Create it if needed.

        BBB note: the date used to be as a float field in portlet_common
        schema, we upgrade transparently.
        """
        attr = 'cache_cleanup_date'
        idt = getattr(aq_base(self), attr, None)
        if idt is None or isinstance(idt, float):
            setattr(self, attr, IncreasingDateTime(attr))
        return getattr(self, attr) # aq_wrapped

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
        if (isinstance(range, list) and
            len(range) == 2 and
            isinstance(range[0], int) and
            isinstance(range[1], int)):
            try:
                self.edit(visibility_range=range)
                return 0
            except ValueError:
                pass
        return 1

    security.declarePublic('VisibilityRangeMsgid')
    def getVisibilityRangeMsgid(self):
        """Return the visibility range msgid for this portlet
        """

        vtool = getToolByName(self, 'portal_vocabularies')
        vrange = self.getVisibilityRange()
        vrange_keyid = '%s-%s' % (vrange[0], vrange[1])

        vrangevoc = vtool[VISIBILITY_VOC]
        return vrangevoc.getMsgid(vrange_keyid)

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
    def getState(self, REQUEST=None):
        """Return the portlet's state
        (minimized, maximized, closed ...)
        default is 'maximized'
        """
        state = 'maximized'
        if REQUEST is None:
            REQUEST = self.REQUEST
        boxid = self.getId()
        cookie_name = 'cpsportlets_box_%s' % boxid
        if REQUEST is not None:
            state = REQUEST.cookies.get(cookie_name, 'maximized')
        return state

    security.declarePublic('setState')
    def setState(self, state='', REQUEST=None):
        """Set the portlet state
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        boxid = self.getId()
        cookie_name = 'cpsportlets_box_%s' % boxid
        if state not in ('minimized', 'maximized', 'closed'):
            return
        if REQUEST is not None:
            path = self.cpsskins_getBaseUrl()
            REQUEST.RESPONSE.setCookie(cookie_name, state, path=path)

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

        # event system throws paths that always start with '/'
        folder_paths = tuple(path.startswith('/') and path or '/' + path
                             for path in folder_paths)

        # Add the event if not already here
        if (event_ids, folder_paths, portal_types) not in self.listEvents():
            self._interesting_events += ((event_ids,
                                          folder_paths,
                                          portal_types), )
            self.reindexObject()
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

                    if folder_path[0] != '/':
                        # shouldn't happen, but it did
                        folder_path = '/' + folder_path

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
    security.declareProtected(ManagePortlets, 'dictExport')
    def dictExport(self):
        """Export the portlet as a Python dictionary.
        """

        data = {}
        ti = self.getTypeInfo()
        dm = ti.getDataModel(self)

        skip_list = ('cache_cleanup_date', 'cache_params', 'Source',
                     'identifier', 'allow_discussion', 'cache_timeout',
                     'Format', 'ExpirationDate', 'Coverage', 'ModificationDate',
                     'review_state', 'portlet', 'EffectiveDate', 'Rights',
                     'Language', 'Contributors', 'Creator', 'Relation',
                     'CreationDate', 'Subject')

        stool = getToolByName(self, 'portal_schemas')
        existing_schemas = stool.objectIds()

        for k, v in dm.items():
            if k in skip_list:
                continue

            for type_schema in ti._listSchemas():
                schema_id = type_schema.getId()
                if schema_id not in existing_schemas:
                    continue
                schema = stool[schema_id]
                for field in schema.objectValues():
                    if field.getFieldId() != k:
                        continue
                    if v != field.getDefault():
                        if field.meta_type == 'CPS String Field':
                            v = "'%s'" % escape(v)
                        data[k] = v
                        continue

        return data.items()

    #################################################################
    # Private
    #################################################################

    security.declarePrivate('_rebuild')
    def _rebuild(self):
        """Rebuilds the portlet.
        """

        # rebuild TypeInformation stuff, notably marker interfaces
        ti = self.getTypeInfo()
        if ti is None:
            return

        # rebuild properties. GR: WTF ??
        stool = getToolByName(self, 'portal_schemas')
        existing_schemas = stool.objectIds()

        for type_schema in ti._listSchemas():
            schema_id = type_schema.getId()
            if schema_id not in existing_schemas:
                continue
            schema = stool[schema_id]
            for field in schema.objectValues():
                field_id = field.getFieldId()
                # the attribute exists or should not persist
                if field.write_ignore_storage or bhasattr(self, field_id):
                    continue
                default_value = field.getDefault()
                setattr(self, field_id, default_value)

        ptype_id = ti.getId()
        # reset cache parameters
        self.resetCacheTimeout()

        # reset the javascript methods
        try:
            javascript_dict = self.getCPSPortletJavaScript()
        except AttributeError:
            javascript_dict = {}

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
        ptltool = getToolByName(self, 'portal_cpsportlets')

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
                    if isinstance(o, (list, tuple)):
                        res.extend(o)
                        continue
                res.append(str(o))
            return res

        event_ids = ()
        folder_paths = ()
        portal_types = ()
        for param in ptltool.getCacheParametersFor(ptype_id):
            # event ids
            if param.startswith('event_ids:'):
                event_ids = getOptions(param)

            # folders in which the event occurs
            elif param.startswith('event_in_folders:'):
                folder_paths = getOptions(param)

            # portal types on which the event occurs
            elif param.startswith('event_on_types:'):
                portal_types = getOptions(param)

        self.clearEvents()
        if event_ids or folder_paths or portal_types:
            self.addEvent(
                event_ids=event_ids,
                folder_paths=folder_paths,
                portal_types=portal_types)

    #################################################################
    # ZMI
    #################################################################

    security.declareProtected(ManagePortlets, 'manage_export')
    manage_export = DTMLFile('zmi/manage_exportForm', globals())

    security.declareProtected(ManagePortlets, 'manage_guardForm')
    manage_guardForm = DTMLFile('zmi/manage_guardForm', globals())

    manage_options = (CPSDocument.manage_options + (
                      {'label': 'Export',
                       'action': 'manage_genericSetupExport.html'},
                      {'label': 'Guard',
                       'action': 'manage_guardForm'},
                      {'label': 'Properties',
                       'action': 'manage_propertiesForm'},
                      )
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
