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

""" Base class for CPS Portlets catalog aware content items.
"""

from Globals import InitializeClass

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.utils import getToolByName

class CPSPortletCatalogAware(CMFCatalogAware):
    """Mix-in for notifying portlets specific catalog

    For performance issues, CPS portlets do have a dedicated catalog.
    """

    def _getCatalogTool(self):
        catalog = getToolByName(self, 'portal_cpsportlets_catalog', None)
        if catalog is None:
            # BBB for installer
            catalog = getToolByName(self, 'portal_catalog')
        return catalog

InitializeClass(CPSPortletCatalogAware)
