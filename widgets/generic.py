# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology
#                    <http://www.chalmers.se>
# Authors : Jean-Marc Orliaguet  <mailto:jmo@ita.chalmers.se>
#           Georges Racinet <mailto:georges@racinet.fr>

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

"""Portlet widgets take care of the main rendering in view mode of the portlet.

Some portlets don't use them, because a standard widget does already cover
their needs (see the Image Portlet for an example).
"""

from zope.interface import implements
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.Widget import CPSWidget

from Products.CPSPortlets.interfaces import IPortletWidget

class CPSPortletWidget(CPSWidget):
    """Generic Portlet Widget."""

    implements(IPortletWidget)

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


class CPSDispatcherPortletWidget(CPSWidget):
    """Portlet widget whose rendering is dispatched on several methods.

    The dispatching is done according to the datastructure value corresponding
    to another widget, referenced in the selector_widget property.
    """

    implements(IPortletWidget)

    meta_type = 'Dispatcher Portlet Widget'

    _properties = CPSWidget._properties + (
        {'id': 'render_method_prefix', 'type': 'string', 'mode': 'w',
         'label': 'Common prefix for the zpt or py script methods'},
        {'id': 'selector_widget', 'type': 'string', 'mode': 'w',
         'label': 'Selector widget'},)

    render_method_prefix = ''
    selector_widget = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        pass

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return True

    def getPortletType(self, datastructure):
        """Return the portal_type of portlet being rendered."""
        ob = datastructure.getDataModel().getObject()
        if ob is None:
            return ''
        return ob.portal_type

    def render(self, mode, datastructure, **kw):
        """Calling the proper method, deduced from prefix and selector widget.

        This assumes that the selector widget behaves like a Select Widget,
        using its id as datastructure key."""

        prefix = self.render_method_prefix.strip()
        key = self.selector_widget.strip()
        try:
            render_method = prefix + datastructure[key].strip()
        except KeyError:
            raise ValueError(("Widget or datastructure key '%s' not found"
                              "in portlet of type '%s'") % (
                key, self.getPortletType(datastructure)))

        meth = getattr(self, render_method, None)
        if meth is None:
            rpath = getToolByName(self, 'portal_url').getRpath(self)
            msg = "Unknown Render Method %s in portlet type '%s'" \
            + "You may need to set or change the 'render_method_prefix' " \
            + "property on the Dispatcher Portlet Widget at '%s'."
            raise RuntimeError(msg % (render_method,
                                      self.getPortletType(datastructure),
                                      rpath))
        return meth(mode=mode, datastructure=datastructure, **kw)

InitializeClass(CPSDispatcherPortletWidget)

