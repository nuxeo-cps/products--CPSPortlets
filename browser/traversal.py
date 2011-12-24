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
        # attribute and special traversals, but only directly on portlet
        if req_trav is None:
            if bhasattr(portlet, name): # regular attribute
                return getattr(portlet, name)

            # now special cases. TODO: in CPSCore, provide a generic traverser
            # and subclass it with soft dependency.
            elif name == KEYWORD_DOWNLOAD_FILE:
                return FileDownloader(portlet, portlet).__of__(portlet)
            elif name == KEYWORD_SIZED_IMAGE:
                return ImageDownloader(portlet, portlet).__of__(portlet)

        # view lookup attempt either directly or after keyword for view
        view = portlet.getBrowserView(request_context_obj(portlet, request),
                                      request, {}, view_name=name)
        if view is not None:
            view.whole_response = True
            return view

        return getattr(portlet, name) # default to acquisition
