# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology
#                    <http://www.chalmers.se>
# Author : Jean-Marc Orliaguet  <mailto:jmo@ita.chalmers.se>

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

__author__ = "Jean-Marc Orliaguet <mailto:jmo@ita.chalmers.se>"

""" Breadcrumbs widget
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass

from Products.CPSSchemas.Widget import CPSWidget, CPSWidgetType

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry

class CPSBreadcrumbsWidget(CPSWidget):
    """CPS Breadcrumbs widget
    """

    meta_type = "CPS Breadcrumbs Widget"

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        pass

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure
        """
        render_method = 'widget_portlet_breadcrumbs'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure)

InitializeClass(CPSBreadcrumbsWidget)

class CPSBreadcrumbsWidgetType(CPSWidgetType):
    """CPS Breadcrumbs Widget Type
    """
    meta_type = "CPS Breadcrumbs Widget Type"
    cls = CPSBreadcrumbsWidget

InitializeClass(CPSBreadcrumbsWidgetType)

WidgetTypeRegistry.register(CPSBreadcrumbsWidgetType,
                            CPSBreadcrumbsWidget)
