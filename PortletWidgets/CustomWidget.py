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

__author__ = "Jean-Marc Orliaguet <mailto:jmo@ita.chalmers.se>"

""" Custom Portlet.
"""

from Globals import InitializeClass

from Products.CPSSchemas.BasicWidgets import CPSStringWidget
from Products.CPSSchemas.Widget import widgetRegistry

class PortletCustomWidget(CPSStringWidget):
    """Custom Portlet widget
    """
    meta_type = 'CPS Portlet Custom Widget'

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        meth = getattr(self, self.render_method, None)
        if meth is None:
            # Real need of CPSAsciiStringField here
            # render_method is acquired from portlet obj (yuck)
            msg = "Unknown render method <cite>%s</cite>." % str(self.render_method)
            return msg
        if not callable(meth):
            msg = "<cite>%s</cite> is not a callable object." \
                  % self.render_method
            return msg
        return meth(**kw)

InitializeClass(PortletCustomWidget)

widgetRegistry.register(PortletCustomWidget)
