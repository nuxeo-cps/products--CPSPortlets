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

"""Portlets Tool
"""

from Globals import InitializeClass

from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder

from Products.CMFCore.utils import UniqueObject

class PortletsTool(UniqueObject, CMFBTreeFolder):
    """ Portlets Tool
    """

    id = 'portal_portlets'
    meta_type = 'Portlets Tool'

    def __init__(self):
        """
        """
        CMFBTreeFolder.__init__(self, self.id)

    ####################################################################

    def getPortletById(self, id):
        """Return a portlet object given an id
        """
        return self.get(id)

    def listPortletIds(self):
        """Return the list of all portlet ids contained within the tool
        """
        ids = []
        for k, v in self.items():
            ids.append(k)
        return ids

    ###################################################################

    def getPortletSlots(self):
        """Return all the available slots
        """
        # XXX lookup everywhere on the portal (locally too)
        return ['top',
                'left',
                'center_top',
                'center',
                'folder_view',
                'center_bottom',
                'right',
                'bottom']

InitializeClass(PortletsTool)
