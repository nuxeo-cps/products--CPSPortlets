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
from Acquisition import aq_base

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

    security.declarePublic('getPortletSlots')
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

        return allportlets

    ######################################################################

    security.declareProtected(ManagePortlets, 'createPortlet')
    def createPortlet(self, ptype_id, isglobal=1):
        """Create a new portlet

        Check where it has to be created globally within the tool or locally
        within the PortletsTool

        returns the id of the new portlet within portal_portlets or Portlet
        Container or None if something happend
        """

        # Check if the ptype_id is valid
        if ptype_id not in self.listPortletTypes():
            return None

        # Check where we gonna create the portlet
        destination = self

        # TODO cope with local portlets
        if not isglobal:
            return None

        return destination._createPortlet(ptype_id)

    security.declareProtected(ManagePortlets, 'deletePortlet')
    def deletePortlet(self, portlet_id, isglobal=1):
        """Delete portlet id

        Possible to warn event service for action
        """

        destination = self

        # TODO cope with local portlets
        if not isglobal:
            pass

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
                    obj = aq_base(obj)
                    if not hasattr(obj, 'isCPSPortlet'):
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
