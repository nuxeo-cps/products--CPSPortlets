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

""" Generic Portlet widget
"""

from Globals import InitializeClass

from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSSchemas.Widget import widgetRegistry

class CPSPortletWidget(CPSWidget):
    """Generic Portlet Widget."""

    meta_type = 'Generic Portlet Widget'

    _properties = CPSWidget._properties + (
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'the zpt or py script method'},
        {'id': 'field_types', 'type': 'lines', 'mode': 'w',
         'label': 'Field types'},)

    field_types = ('CPS String Field',)
    render_method = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        if len(self.fields):
            datastructure[self.getWidgetId()] = datamodel[self.fields[0]]
        else:
            datastructure[self.getWidgetId()] = None

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        err = 0
        v = datastructure[widget_id]
        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            if len(self.fields):
                datamodel[self.fields[0]] = v

        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        meth = getattr(self, self.render_method, None)
        if meth is None:
            msg = "Unknown Render Method %s for widget type %s. " \
            + "Please set or change the 'render_method' attribute on " \
            + "your widget declaration."
            raise RuntimeError(msg % (self.render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure, **kw)

InitializeClass(CPSPortletWidget)

widgetRegistry.register(CPSPortletWidget)
