# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Author : Julien Anguenot <ja@nuxeo.com>

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

"""CPS Portlet componnent
"""

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

# Fallback to CMF 1.4
try:
    from Products.CMFCore.permissions import AddPortalContent
except ImportError:
    from Products.CMFCore.CMFCorePermissions import AddPortalContent

import CPSPortletsPermissions
import FlexibleTypeInformationPatch
import PortletsTool
import CPSPortlet
import CPSPortletWidget
import CPSPortletVisibilityWidget
import FileDownloaderPatch
import PortletsContainer
import PortletRAMCache

# Import new widgets in here
import PortletWidgets.DummyWidget
import PortletWidgets.CustomWidget

contentClasses = (
    CPSPortlet.CPSPortlet,
    PortletsContainer.PortletsContainer,
    )

contentConstructors = (
    CPSPortlet.addCPSPortlet,
    PortletsContainer.addPortletsContainer,
    )

fti = ()

tools = (PortletsTool.PortletsTool,)


registerDirectory('skins', globals())

def initialize(registrar):
    """Initialize CPS Portlets content
    """

    # Content
    utils.ContentInit(
        'CPS Portlet Types',
        content_types=contentClasses,
        permission=AddPortalContent,
        extra_constructors=contentConstructors,
        fti=fti).initialize(registrar)

    # Tool
    utils.ToolInit(
        'CPS Portlets Tool',
        tools=tools,
        product_name='CPSPortlets',
        icon='tool.gif',).initialize(registrar)
