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

""" Search widget
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass

from Products.CPSSchemas.Widget import CPSWidget, CPSWidgetType

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry

class CPSSearchWidget(CPSWidget):
    """CPS Search widget
    """

    meta_type = "CPS Search Widget"

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        pass

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure
        """
        render_method = 'widget_portlet_search'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure)

InitializeClass(CPSSearchWidget)

class CPSSearchWidgetType(CPSWidgetType):
    """CPS Search Widget Type
    """
    meta_type = "CPS Search Widget Type"
    cls = CPSSearchWidget

InitializeClass(CPSSearchWidgetType)

WidgetTypeRegistry.register(CPSSearchWidgetType,
                            CPSSearchWidget)
