# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Julien Anguenot <ja@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

""" CPSPortlets Installer
"""

from zLOG import LOG, INFO, DEBUG

from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View
from Products.CPSInstaller.CPSInstaller import CPSInstaller

from Products.CPSPortlets.CPSPortletsPermissions import ManagePortlets

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'
SKINS = {'cpsportlets_widgets':
         'Products/CPSPortlets/skins/cpsportlets_widgets',
# CPS3 specific ---------------------------------------------
         'cpsportlets_widgets_cps3':
         'Products/CPSPortlets/skins/cpsportlets_widgets_cps3',
# -----------------------------------------------------------

# Plone2 specific ---------------------------------------------
#         'cpsportlets_widgets_plone2':
#         'Products/CPSPortlets/skins/cpsportlets_widgets_plone2',
# -----------------------------------------------------------
         'cpsportlets_default':
         'Products/CPSPortlets/skins/cpsportlets_default',
         'cpsportlets_schemas':
         'Products/CPSPortlets/skins/cpsportlets_schemas',
         'cpsportlets_types':
         'Products/CPSPortlets/skins/cpsportlets_vocabularies',
         'cpsportlets_vocabularies':
         'Products/CPSPortlets/skins/cpsportlets_types',
         'cpsportlets_layouts':
         'Products/CPSPortlets/skins/cpsportlets_layouts',
         }

class CPSPortletsInstaller(CPSInstaller):
    """ Installer class for CPS Portlets component
    """

    product_name = 'CPSPortlets'

    def install(self):
        """ Installs the compulsory elements.
        """

        self.log("Install/Update : CPSPortlets Product")
        self.verifyTool('portal_cpsportlets', 'CPSPortlets',
                         'CPS Portlets Tool')
        self.verifySkins(SKINS)
        self.resetSkinCache()
        self.setupSpecificPermissions()
        self.verifyWidgets(self.portal.getPortletWidgets())
        self.installPortletVocabularies()
        self.installPortletSchemas()
        self.installPortletLayouts()
        self.installFlexibleTypes()
        self.setupTranslations()
        self.rebuildPortlets()
        self.doSubscribeToEventServiceTool()
        self.finalize()
        self.log("End of Install/Update : CPSPortlets Product")


    def setupSpecificPermissions(self):
        """Setup specific permissions
        """

        # Globally
        # Necessarly ?
        self.setupPortalPermissions({
            ManagePortlets : ['Manager',
                              'Owner'],})

        # Workspace
        ws_perms = {
            ManagePortlets : ['Manager',
                              'Owner',
                              'WorkspaceManager',],
            }

        if self.portalHas(WORKSPACES_ID):
            for perm, roles in ws_perms.items():
                self.portal[WORKSPACES_ID].manage_permission(perm, roles, 0)


        # Sections
        se_perms = {
            ManagePortlets : ['Manager',
                              'Owner',
                              'SectionManager',],
            }

        if self.portalHas(SECTIONS_ID):
            for perm, roles in se_perms.items():
                self.portal[SECTIONS_ID].manage_permission(perm, roles, 0)

    def installPortletVocabularies(self):
        """Install all portlet specific vocabularies."""

        define_vocabularies = (self.portal.getPortletDisplayVocabulary(),
                              )

        all_vocabularies = {}
        for vocabulary in define_vocabularies:
            all_vocabularies.update(vocabulary)

        self.verifyVocabularies(all_vocabularies)

    def installPortletSchemas(self):
        """Install all portlet specific schemas."""

        define_schemas = (self.portal.getPortletCommonSchema(),
                          self.portal.getSearchPortletSchema(),
                          self.portal.getInternalLinksPortletSchema(),
                          self.portal.getAddItemPortletSchema(),
                          self.portal.getBreadcrumbsPortletSchema(),
                          self.portal.getDummyPortletSchema(),
                         )

        all_schemas = {}
        for schema in define_schemas:
            all_schemas.update(schema)

        self.verifySchemas(all_schemas)

    def installPortletLayouts(self):
        """Install all portlet specific layouts."""

        define_layouts = (self.portal.getPortletCommonLayout(),
                          self.portal.getDummyPortletLayout(),
                          self.portal.getSearchPortletLayout(),
                          self.portal.getInternalLinksPortletLayout(),
                          self.portal.getAddItemPortletLayout(),
                          self.portal.getBreadcrumbsPortletLayout(),
                         )

        all_layouts = {}
        for layout in define_layouts:
            all_layouts.update(layout)

        self.verifyLayouts(all_layouts)

    def installFlexibleTypes(self):
        """Install all portlet specific types."""

        define_types = (self.portal.getDummyPortletType(),
                        self.portal.getSearchPortletType(),
                        self.portal.getInternalLinksPortletType(),
                        self.portal.getAddItemPortletType(),
                        self.portal.getBreadcrumbsPortletType(),
                       )

        all_ptypes = {}
        for ptype in define_types:
            all_ptypes.update(ptype)

        self.verifyFlexibleTypes(all_ptypes)


    def rebuildPortlets(self):
        """Rebuild all portlets to make sure that their schema
           definitions is up-to-date"""

        self.log("Rebuilding all portlets...")
        ptltool = getToolByName(self.portal, 'portal_cpsportlets')
        ptltool.rebuild_portlets(REQUEST=None)

    def doSubscribeToEventServiceTool(self):
        """Subscribe to the event service tool
        """

        # Try to get the event service tool from CPS3
        evtool = getToolByName(self.portal,
                               'portal_eventservice',
                               None)

        # If found subscribe
        if evtool is not None:
            objs = evtool.objectValues()
            subscribers = []
            for obj in objs:
                subscribers.append(obj.subscriber)
            if 'portal_cpsportlets' not in subscribers:
                self.log("Adding CPS Portlets Tool as subscriber of Event service tool")
                evtool.manage_addSubscriber(
                    subscriber='portal_cpsportlets',
                    action='event',
                    meta_type='*',
                    event_type='*',
                    notification_type='synchronous')
            self.log("Portlal CPS Portlets :: already subscriber")

        self.log('Event service tool not found')

###############################################
# __call__
###############################################

def install(self):
    """Installation is done here.
    """
    installer = CPSPortletsInstaller(self)
    installer.install()
    return installer.logResult()
