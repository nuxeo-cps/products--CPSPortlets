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

""" Widgets related to portlets.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass

from Products.CPSSchemas.BasicWidgets import CPSStringWidget, \
     CPSStringWidgetType, \
     renderHtmlTag
from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry

class PortletDummyWidget(CPSStringWidget):
    """Dummy Portlet widget
    """

    meta_type = "CPS Portlet Dummy Widget"

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure
        """
        return "<h1>Dummy portlet</h1>"

InitializeClass(PortletDummyWidget)

class PortletDummyWidgetType(CPSStringWidgetType):
    """Dummy Portlet Widget Type
    """
    meta_type = "CPS Portlet Dummy Widget Type"
    cls = PortletDummyWidget

InitializeClass(PortletDummyWidgetType)

WidgetTypeRegistry.register(PortletDummyWidgetType,
                            PortletDummyWidget)

