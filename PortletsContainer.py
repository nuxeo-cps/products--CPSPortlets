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

"""Portlets Container

Will be used to define local boxes
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder
from Products.CMFCore.utils import getToolByName

class PortletsContainer(CMFBTreeFolder):
    """ Portlets Container
    """

    meta_type = 'CPS Placeful Portlets Container'
    portal_type = meta_type

    security = ClassSecurityInfo()

    def __init__(self, id=None):
        """
        """
        if id is None:
            id = self.id
        CMFBTreeFolder.__init__(self, id)

    ####################################################################

    def getPortletById(self, id):
        """Return a portlet object given an id
        """
        return self.get(id)

    def listPortlets(self):
        """Return the list of portlet objects
        """

        portlets = []
        ids = self.listPortletIds()
        for id in ids:
            portlets.append(self.getPortletById(id))
        return portlets

    def listPortletIds(self):
        """Return the list of all portlet ids contained within the tool
        """
        ids = []
        for k, v in self.items():
            portlet = self.getPortletById(k)
            if not hasattr(aq_base(portlet), 'isCPSPortlet'):
                continue
            if not portlet.isCPSPortlet():
                continue
            ids.append(k)
        return ids

    ####################################################################

    def _createPortlet(self, ptype_id, **kw):
        """Create a new portlet given its portal_type

        Check the identifier that the user might have given.  If it aleady
        exists then don't create the portlet and log it The reason is that the
        update will be wrong after if cerate it in this situation

        If it's a portlet created through CPSSkins then use the internal
        id as identifier
        """

        ptltool = getToolByName(self, 'portal_cpsportlets')

        ok = 0

        if kw.has_key('identifier'):
            ok = ptltool.checkIdentifier(kw.get('identifier'))
        else:
            while not ok:
                new_id = self.generateId(prefix='portlet_',
                                         suffix='',
                                         rand_ceiling=999999999)
                ok = ptltool.checkIdentifier(new_id)
            kw['identifier'] = new_id

        if ok:
            new_id = kw.get('identifier')
            cache_params_dict = self.getCPSPortletCacheParams()
            if cache_params_dict.has_key(ptype_id):
                cache_params = cache_params_dict[ptype_id]
                kw.update({'cache_params': cache_params})
            self.invokeFactory(ptype_id, new_id)
            new_portlet = getattr(self, new_id)
            new_portlet.edit(kw)
            return new_id
        return None

    def _deletePortlet(self, portlet_id):
        """Delete a portlet given its id
        """
        if portlet_id in self.listPortletIds():
            self._delObject(portlet_id)
            return 0
        return 1

    #####################################################################

    def listPortletSlots(self):
        """Return all the portlets slots
        """

        slots = []
        portlet_ids = self.listPortletIds()

        for id in portlet_ids:
            portlet = self.getPortletById(id)
            if getattr(aq_base(portlet), 'isCPSPortlet', None) is None:
                continue
            if not portlet.isCPSPortlet():
                continue
            slot = portlet.getSlot()
            if slot and slot not in slots:
                slots.append(slot)

        return slots

InitializeClass(PortletsContainer)

def addPortletsContainer(dispatcher, id='', REQUEST=None):
    """Add a CPS Portlets Container.
    """
    if not id:
        id = dispatcher.portal_cpsportlets.getPortletContainerId()
    ob = PortletsContainer(id)
    container = dispatcher.Destination()
    container._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
