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
         'cpsportlets_default':
         'Products/CPSPortlets/skins/cpsportlets_default',
         'cpsportlets_schemas':
         'Products/CPSPortlets/skins/cpsportlets_schemas',
         'cpsportlets_types':
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
        self.installPortletSchemas()
        self.installPortletLayouts()
        self.installFlexibleTypes()
        self.setupTranslations()
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

        for perm, roles in ws_perms.items():
            self.portal[WORKSPACES_ID].manage_permission(perm, roles, 0)


        # Sections
        se_perms = {
            ManagePortlets : ['Manager',
                              'Owner',
                              'SectionManager',],
            }

        for perm, roles in se_perms.items():
            self.portal[SECTIONS_ID].manage_permission(perm, roles, 0)

    def installPortletSchemas(self):
        """Install all portlet specific schemas."""

        define_schemas = (self.portal.getPortletCommonSchema(),
                          self.portal.getSearchPortletSchema(),
                          self.portal.getInternalLinksPortletSchema(),
                          self.portal.getDummyPortletSchema(),
                         )

        all_schemas = {}
        for schema in define_schemas:
            all_schemas.update(schema)

        self.verifySchemas(all_schemas)

    def installPortletLayouts(self):
        """Install all portlet specific layouts."""

        define_layouts = (self.portal.getDummyPortletLayout(),
                          self.portal.getInternalLinksPortletLayout(),
                          self.portal.getSearchPortletLayout(),
                         )

        all_layouts = {}
        for layout in define_layouts:
            all_layouts.update(layout)

        self.verifyLayouts(all_layouts)

    def installFlexibleTypes(self):
        """Install all portlet specific types."""

        define_types = (self.portal.getDummyPortletType(),
                        self.portal.getInternalLinksPortletType(),
                        self.portal.getSearchPortletType(),
                       )

        all_ptypes = {}
        for ptype in define_types:
            all_ptypes.update(ptype)

        self.verifyFlexibleTypes(all_ptypes)


###############################################
# __call__
###############################################

def install(self):
    """Installation is done here.
    """
    installer = CPSPortletsInstaller(self)
    installer.install()
    return installer.logResult()
