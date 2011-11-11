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

from Products.CPSCore.utils import bhasattr
from Products.CPSCore.ProxyBase import FileDownloader
from Products.CPSCore.ProxyBase import ImageDownloader
from Products.CPSCore.utils import KEYWORD_DOWNLOAD_FILE
from Products.CPSCore.utils import KEYWORD_SIZED_IMAGE

REQUEST_TRAVERSAL_KEY = '_portlet_traversal'

class PortletTraverser(object):

    implements(IPublishTraverse)

    def __init__(self, portlet, request):
        self.portlet = portlet

    def publishTraverse(self, request, name):
        portlet = self.portlet
        if bhasattr(portlet, name): # regular attribute
            return getattr(portlet, name)
        # now special cases. TODO: in CPSCore, provide a generic traverser
        # and subclass it with soft dependency.
        elif name == KEYWORD_DOWNLOAD_FILE:
            return FileDownloader(portlet, portlet).__of__(portlet)
        elif name == KEYWORD_SIZED_IMAGE:
            return ImageDownloader(portlet, portlet).__of__(portlet)

        view = queryMultiAdapter((portlet, request), Interface, name)
        if view is not None:
            return view

        # Neither regular attribute nor a view, : store for later traversal,
        # from a view or render method to context object
        req_trav = getattr(request, REQUEST_TRAVERSAL_KEY, None)
        if req_trav is None:
            req_trav = []
            setattr(request, REQUEST_TRAVERSAL_KEY, req_trav)
        req_trav.append(name)
        return portlet
