# (C) Copyright 2011 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <gracinet@cps-cms.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Traversers for CPSPortlets."""

from zope.interface import Interface
from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound

from Acquisition import aq_parent, aq_inner

from Products.CPSCore.utils import bhasattr
from Products.CPSCore.ProxyBase import FileDownloader
from Products.CPSCore.ProxyBase import ImageDownloader
from Products.CPSCore.utils import KEYWORD_DOWNLOAD_FILE
from Products.CPSCore.utils import KEYWORD_SIZED_IMAGE

REQUEST_TRAVERSAL_KEY = '_portlet_traversal'
REQUEST_TRAVERSAL_FINISHED = '_portlet_traversal_finished'
KEYWORD_CONTEXT_OBJ_TRAVERSAL = '.context'
KEYWORD_VIEW_TRAVERSAL = '.view'

def parent(obj):
    """For readability."""
    return aq_parent(aq_inner(obj))

def request_context_obj(portlet, request):
    """Use request to traverse to context_obj from portlet's definition folder.
    """
    definition_folder = parent(parent(portlet))
    req_trav = getattr(request, REQUEST_TRAVERSAL_KEY, None)
    if req_trav is None:
        return definition_folder
    rpath = '/'.join(req_trav)
    try:
        context_obj = definition_folder.restrictedTraverse(rpath)
    except (KeyError, AttributeError):
        raise NotFound('/'.join((
                    definition_folder.absolute_url_path() + rpath)))

    return context_obj

class CacheRenderer(object):
    """An object to return from traversal to trigger cache-aware rendering.

    Can either keep a reference to an already looked up view or just its name,
    to avoid double lookups downstream.
    """

    def __init__(self, portlet, request, context=None,
                 view_name='', view=None):
        """view_name is the *requested* view name, before actual resolution.
        """
        self.portlet = portlet
        self.request = request
        self.view_name = view_name
        self.view = view
        self.further_path = []

    def __getitem__(self, item):
        self.further_path.append(item)
        return self

    def __call__(self):
        """Called after traversal"""
        request = self.request
        portlet = self.portlet
        return portlet.render_cache(
            REQUEST=request, view_name=self.view_name, view=self.view,
            whole_response=True,
            context_obj=request_context_obj(portlet, request))

class PortletTraverser(object):
    """Will be looked up and called for each path segment.

    If the adapter lookup becomes a performance bottleneck (currently really
    not the case), we could factor this logic out to implement IPublishTraverse
    also in CPSPortlet class. With the current (Zope 2.10) version of
    BaseRequest, this is indeed checked and used before any adapter lookup.
    """

    implements(IPublishTraverse)

    def __init__(self, portlet, request):
        self.portlet = portlet

    def publishTraverse(self, request, name):
        req_trav = getattr(request, REQUEST_TRAVERSAL_KEY, None)
        portlet = self.portlet
        if req_trav is None and name == KEYWORD_CONTEXT_OBJ_TRAVERSAL:
            # initiate deferred context obj traversal
            setattr(request, REQUEST_TRAVERSAL_KEY, [])
            setattr(request, REQUEST_TRAVERSAL_FINISHED, False)
            return portlet

        if req_trav is not None and not getattr(request,
                                                REQUEST_TRAVERSAL_FINISHED):
           if name == KEYWORD_VIEW_TRAVERSAL:
               setattr(request, REQUEST_TRAVERSAL_FINISHED, True)
           else: # store for deferred traversal
               req_trav.append(name)
           return portlet

        portlet = self.portlet

        # regular attribute
        # must work even after processing the context part of traversal:
        # if no view is specified, name == 'render', and
        # we'll call otherwise getBrowserView from here, and then from
        # portlet.render(), which means building the datamodel twice
        # (not negligible for fast portlets)
        if bhasattr(portlet, name):
            return getattr(portlet, name)

        # special traversals, but only directly on portlet
        if req_trav is None:
            # now special cases. TODO: in CPSCore, provide a generic traverser
            # and subclass it with soft dependency.
            if name == KEYWORD_DOWNLOAD_FILE:
                return FileDownloader(portlet, portlet).__of__(portlet)
            elif name == KEYWORD_SIZED_IMAGE:
                return ImageDownloader(portlet, portlet).__of__(portlet)


        if getattr(request, REQUEST_TRAVERSAL_FINISHED, False):
            # we are 100% sure that this is a view-based rendering.
            # Transmit to cache system, it'll either render without a lookup
            # or call the non-cached rendering (does the lookup)
            return CacheRenderer(portlet, request, view_name=name)

        # view lookup attempt
        view = portlet.getBrowserView(request_context_obj(portlet, request),
                                      request, {}, view_name=name)

        if view is not None:
            # this is afterall a view. CacheRenderer can use it
            return CacheRenderer(portlet, request, view=view)

        return getattr(portlet, name) # default to acquisition

    def viewAbsoluteUrlPath(self, view_name, context_obj=None):
        """Return relative URI w/ absolute path for named view on context.

        This is some kind of anti-traversal. Alternate traversers should
        also implement this method. This way, encoding/decoding of URLs stay
        close to each other in the code.

        context should be None only if the rendering is expected to be
        independent of context (useful for HTTP caching).
        """
        portlet = self.portlet
        segments = [portlet.absolute_url_path(), KEYWORD_CONTEXT_OBJ_TRAVERSAL]

        if context_obj is not None:
            definition_folder = parent(parent(portlet))
            definition_path = definition_folder.getPhysicalPath()
            context_path = context_obj.getPhysicalPath()
            while definition_path:
                if not context_path[0] == definition_path[0]:
                    raise RuntimeError((
                        "Rendering context %r should be below definition "
                        "folder %r") % (context_obj, definiton_folder))
                definition_path = definition_path[1:]
                context_path = context_path[1:]
            segments.extend(context_path)

        segments.extend((KEYWORD_VIEW_TRAVERSAL, view_name))
        return '/'.join(segments)
