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

"""Portlets Tool
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner

from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.CPSPortlets.PortletsContainer import PortletsContainer
from Products.CPSPortlets.CPSPortletsPermissions import ManagePortlets


PORTLET_CONTAINER_ID = '.cps_portlets'

class PortletsTool(UniqueObject, PortletsContainer):
    """ Portlets Tool
    """

    id = 'portal_cpsportlets'
    meta_type = 'CPS Portlets Tool'

    security = ClassSecurityInfo()

    security.declarePublic('listPortletSlots')
    def listPortletSlots(self):
        """Return all the available slots
        """

        # Slots defined within portlets defined within the tool
        slots = PortletsContainer.listPortletSlots(self)

        # Cope with local portlets containers
        catalog = getToolByName(self, 'portal_catalog')
        portal_types = self.listPortletTypes()

        # Lookup through catalog to get the potlets
        # We ask the tool to know all the portal_types
        portlets = catalog.searchResults({'portal_type':portal_types})
        for portlet in portlets:
            local_slot = portlet.getObject().getSlot()
            if local_slot and local_slot not in slots:
                slots.append(local_slot)

        return slots

    security.declarePublic('listPortletTypes')
    def listPortletTypes(self):
        """Return the list of all defined portal_types which are portlets

        It means having the 'CPS Portlet' flag
        """
        ttool = getToolByName(self, 'portal_types')
        returned = []
        for id in ttool.objectIds():
            fti = getattr(ttool, id)
            if getattr(fti, 'cps_is_portlet', 0) == 1:
                returned.append(id)
        return returned

    security.declarePublic('getPortletContainerId')
    def getPortletContainerId(self):
        """Return the id of the portlet container.
        """
        return PORTLET_CONTAINER_ID

    #######################################################################

    security.declarePublic('getPortlets')
    def getPortlets(self, context=None, slot=None):
        """Return a list of portlets.
        """

        if context is None:
            return []

        # Find bottom-most folder:
        obj = context
        bmf = None
        while 1:
            if obj.isPrincipiaFolderish:
                bmf = obj
                break
            parent = aq_parent(aq_inner(obj))
            if not obj or parent == obj:
                break
            obj = parent
        if bmf is None:
            bmf = context

        # get portlets from the root to current path
        # XXX no security check is done yet.

        portal_url = getToolByName(self, 'portal_url')
        rpath = portal_url.getRelativeContentPath(bmf)
        obj = portal_url.getPortalObject()
        allportlets = []
        for elem in ('',) + rpath:
            if elem:
                obj = getattr(obj, elem)
            allportlets.extend(self._getFolderPortlets(folder=obj, slot=slot))

        # sort the portlets
        def cmporder(a, b):
            return int(a.order) - int(b.order)
        allportlets.sort(cmporder)

        return allportlets

    ######################################################################

    security.declareProtected(ManagePortlets, 'createPortlet')
    def createPortlet(self, ptype_id, context=None, **kw):
        """Create a new portlet

        Check where it has to be created globally within the tool or locally
        within the PortletsTool. It's done byt checking the context. If context
        is None then it's global otherweise we gonne look at the context to get
        the portal ocontainer

        returns the id of the new portlet within portal_portlets or Portlet
        Container or None if something happend
        """

        # Check if the ptype_id is valid
        if ptype_id not in self.listPortletTypes():
            return None

        # Check where we gonna create the portlet
        if context is None:
            # Here it's within the tool
            destination = self
        else:
            container_id = self.getPortletContainerId()

            # We create the portlets container if it doesn't already exist
            if container_id not in context.objectIds():
                context.manage_addProduct['CPSPortlets'].addPortletsContainer(
                    id=container_id)

            # Get the portlets container from the context
            destination = getattr(context, container_id)

        return destination._createPortlet(ptype_id, **kw)

    security.declareProtected(ManagePortlets, 'deletePortlet')
    def deletePortlet(self, portlet_id, context=None):
        """Delete portlet id

        Possible to warn event service for action
        """

        if context is None:
            destination = self
        else:
            container_id = self.getPortletContainerId()
            destination = getattr(context, container_id)

        return destination._deletePortlet(portlet_id)

    #
    # Private
    #

    security.declarePrivate('_getFolderPortlets')
    def _getFolderPortlets(self, folder=None, slot=None):
        """Load all portlets in a .cps_portlets folder.
           The slot name can be used as a filter.
        """

        portlets = []
        if folder is not None:
            idpc = self.getPortletContainerId()
            if idpc in folder.objectIds():
                for obj in getattr(folder, idpc).objectValues():
                    if not hasattr(aq_base(obj), 'isCPSPortlet'):
                       continue
                    if not obj.isCPSPortlet():
                       continue
                    if slot is not None:
                       portlet_slot = getattr(obj, 'slot', '')
                       if portlet_slot != slot:
                           continue
                    portlets.append(obj)
        return portlets

InitializeClass(PortletsTool)
