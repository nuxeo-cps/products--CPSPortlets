# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology
#               <http://www.chalmers.se>
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

"""CPS Portlet

This is a CPSDocument child base class for portlets
"""

from Globals import InitializeClass
from Acquisition import aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName

from Products.CPSDocument.CPSDocument import CPSDocument


class CPSPortlet(CPSDocument):
    """ CPS Portlet

    This is a CPSPortlet child base class for portlets
    """

    meta_type = 'CPS Portlet'
    portal_type = meta_type

    def SearchableText(self):
        """ We don't index CPS Portlets

        No Searchable Text on here
        """
        return ""

    def isCPSPortlet(self):
        """Return true if this is a CPS Portlet.
        """
        return 1

    ##################################################################

    def getURL(self):
        """Return the url of the portlet.
        """
        return self.absolute_url()

    def getRelativeUrl(self):
        """Return the url of the portlet relative to the portal.
        """
        utool = getToolByName(self, 'portal_url')
        return utool.getRelativeUrl(self)

    def getPath(self):
        """Return the physical path of the portlet.
        """
        return self.getPhysicalPath()

    def getLocalFolder(self):
        """Return the local folder (workspace, section ...)
           inside which the portlet will be displayed.
        """

        container = aq_parent(aq_inner(self))
        return aq_parent(aq_inner(container))

    #################################################################

    def getSlot(self):
        """Return the portlet's slot.
        """
        return self.slot

    def setSlot(self, slot_name=''):
        """Set the slot value
        """
        if slot_name:
            self.edit(slot=slot_name)
            return 0
        return 1

    #################################################################

    def getOrder(self):
        """Return the portlet's order.
        """
        return self.order

    def setOrder(self, order=0):
        """Set order

        0 is the default value
        """
        self.edit(order=order)

InitializeClass(CPSPortlet)

def addCPSPortlet(container, id, REQUEST=None, **kw):
    """Add a bare CPS Portlet.

    The object doesn't have a portal_type yet, so we have no way to know
    its schema. This simply constructs a bare instance.
    """
    ob = CPSPortlet(id, **kw)
    container._setObject(id, ob)
    if REQUEST:
        ob = container._getOb(id)
        REQUEST.RESPONSE.redirect(ob.absolute_url()+'/manage_main')

