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

"""Portlets Container

Will be used to define local boxes
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder

class PortletsContainer(CMFBTreeFolder):
    """ Portlets Container
    """

    meta_type = 'CPS Placeful Portlets Container'

    security = ClassSecurityInfo()

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

    ####################################################################


InitializeClass(PortletsContainer)

def addPortletsContainer(container, id, REQUEST=None, **kw):
    """Add a bare CPS Portlet.

    The object doesn't have a portal_type yet, so we have no way to know
    its schema. This simply constructs a bare instance.
    """
    ob = PortletsContainer(id, **kw)
    container._setObject(id, ob)
    if REQUEST:
        ob = container._getOb(id)
        REQUEST.RESPONSE.redirect(ob.absolute_url()+'/manage_main')
