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

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'
SKINS = {'cpsportlets_widgets':
         'Products/CPSPortlets/skins/cpsportlets_widgets'}

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
        self.verifyWidgets(self.portal.getPortletWidgets())
        self.finalize()
        self.log("End of Install/Update : CPSPortlets Product")


###############################################
# __call__
###############################################

def install(self):
    """Installation is done here.
    """
    installer = CPSPortletsInstaller(self)
    installer.install()
    return installer.logResult()
