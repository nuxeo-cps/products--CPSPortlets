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
from Acquisition import aq_base

from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.CMFCore.utils import getToolByName

# Fallback to CMF 1.4
try:
    from Products.CMFCore.permissions import View
except ImportError:
    from Products.CMFCore.CMFCorePermissions import View

from Products.CPSInstaller.CPSInstaller import CPSInstaller

from Products.CPSPortlets.CPSPortletsPermissions import ManagePortlets
from Products.CPSPortlets.PortletsTool import PORTLET_MANAGE_ACTION_ID,\
                                              PORTLET_MANAGE_ACTION_CATEGORY

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'
SKINS = {'cpsportlets_widgets':
         'Products/CPSPortlets/skins/cpsportlets_widgets',
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
    """Installer class for CPS Portlets components
    """

    product_name = 'CPSPortlets'

    def install(self):
        """Installs the mandatory components.
        """

        self.log("Install/Update : CPSPortlets Product")
        self.verifyTool('portal_cpsportlets_catalog', 'CPSPortlets',
                        'CPS Portlets Catalog Tool')
        self.verifyTool('portal_cpsportlets', 'CPSPortlets',
                         'CPS Portlets Tool')
        self.verifySkins(SKINS)
        self.resetSkinCache()
        self.setupSpecificPermissions()
        self.installPortletVocabularies()
        self.installPortletSchemas()
        self.installPortletLayouts()
        self.installFlexibleTypes()

        # cache parameters are stored in the tool
        self.setupCacheParameters()

        # importing po files
        # Non CPS Installation may not have Localizer
        if self.portalHas('Localizer'):
            self.setupTranslations()

        # portlet management screen
        self.verifyAction('portal_actions',
                id=PORTLET_MANAGE_ACTION_ID,
                name='action_portlets',
                action="string:${folder_url}/portlet_manage_form",
                condition='member',
                permission=(ManagePortlets,),
                category=PORTLET_MANAGE_ACTION_CATEGORY,
                visible=1)

        self.rebuildPortlets()
        self.clearCache()
        self.doSubscribeToEventServiceTool()
        self.setupPortletsCatalog()
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
        """Install portlet specific vocabularies."""

        define_vocabularies = (self.portal.getPortletVisibilityVocabulary(),
                               self.portal.getBreadcrumbsPortletVocabulary(),
                               self.portal.getContentPortletVocabulary(),
                               self.portal.getLanguagePortletVocabulary(),
                               self.portal.getNavigationPortletVocabulary(),
                               self.portal.getRSSPortletVocabulary(),
                               self.portal.getAddItemPortletVocabulary(),
                               self.portal.getSyndicationFormatsVocabulary(),
                              )

        all_vocabularies = {}
        for vocabulary in define_vocabularies:
            all_vocabularies.update(vocabulary)

        self.verifyVocabularies(all_vocabularies)

    def installPortletSchemas(self):
        """Install portlet specific schemas."""

        define_schemas = (self.portal.getPortletCommonSchema(),
                          self.portal.getTextPortletSchema(),
                          self.portal.getImagePortletSchema(),
                          self.portal.getRotatingImagePortletSchema(),
                          self.portal.getSearchPortletSchema(),
                          self.portal.getInternalLinksPortletSchema(),
                          self.portal.getAddItemPortletSchema(),
                          self.portal.getBreadcrumbsPortletSchema(),
                          self.portal.getActionsPortletSchema(),
                          self.portal.getContentPortletSchema(),
                          self.portal.getLanguagePortletSchema(),
                          self.portal.getNavigationPortletSchema(),
                          self.portal.getDocumentPortletSchema(),
                          self.portal.getRSSPortletSchema(),
                          self.portal.getDummyPortletSchema(),
                          self.portal.getCustomPortletSchema(),
                         )

        all_schemas = {}
        for schema in define_schemas:
            all_schemas.update(schema)

        self.verifySchemas(all_schemas)

    def installPortletLayouts(self):
        """Install portlet specific layouts."""

        define_layouts = (self.portal.getPortletCommonLayout(),
                          self.portal.getTextPortletLayout(),
                          self.portal.getImagePortletLayout(),
                          self.portal.getRotatingImagePortletLayout(),
                          self.portal.getDummyPortletLayout(),
                          self.portal.getCustomPortletLayout(),
                          self.portal.getSearchPortletLayout(),
                          self.portal.getInternalLinksPortletLayout(),
                          self.portal.getAddItemPortletLayout(),
                          self.portal.getBreadcrumbsPortletLayout(),
                          self.portal.getContentPortletLayout(),
                          self.portal.getLanguagePortletLayout(),
                          self.portal.getNavigationPortletLayout(),
                          self.portal.getDocumentPortletLayout(),
                          self.portal.getRSSPortletLayout(),
                          self.portal.getActionsPortletLayout(),
                         )

        all_layouts = {}
        for layout in define_layouts:
            all_layouts.update(layout)

        self.verifyLayouts(all_layouts)

    def installFlexibleTypes(self):
        """Install portlet specific types."""

        define_types = (self.portal.getDummyPortletType(),
                        self.portal.getCustomPortletType(),
                        self.portal.getTextPortletType(),
                        self.portal.getImagePortletType(),
                        self.portal.getRotatingImagePortletType(),
                        self.portal.getSearchPortletType(),
                        self.portal.getInternalLinksPortletType(),
                        self.portal.getAddItemPortletType(),
                        self.portal.getBreadcrumbsPortletType(),
                        self.portal.getActionsPortletType(),
                        self.portal.getContentPortletType(),
                        self.portal.getLanguagePortletType(),
                        self.portal.getNavigationPortletType(),
                        self.portal.getDocumentPortletType(),
                        self.portal.getRSSPortletType(),
                       )

        all_ptypes = {}
        for ptype in define_types:
            all_ptypes.update(ptype)

        self.verifyFlexibleTypes(all_ptypes)

    def setupCacheParameters(self):
        ptltool = getToolByName(self.portal, 'portal_cpsportlets')
        cache_parameters = getattr(aq_base(ptltool), 'cache_parameters', {})

        if len(cache_parameters) == 0:
            ptltool.initializeCacheParameters()
            ptltool.resetCacheParameters()

    def rebuildPortlets(self):
        """Rebuild all portlets to make sure that their schema
           definitions is up-to-date"""

        self.log("Rebuilding all portlets...")
        ptltool = getToolByName(self.portal, 'portal_cpsportlets')
        ptltool.rebuild_portlets(REQUEST=None)

    def clearCache(self):
        """Clear the RAM cache
        """
        ptltool = getToolByName(self.portal, 'portal_cpsportlets')
        ptltool.clearCache()

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
                    activated=True,
                    notification_type='synchronous')
            self.log("Portal CPS Portlets :: already subscriber")

            # Check Status
            subscriber = evtool.getSubscriberByName('portal_cpsportlets')
            if not subscriber.activated:
                subscriber.enable()

        else:
            self.log('Event service tool not found')

    #######################################################
    # PORTLETS CATALOG
    #######################################################

    def setupPortletsCatalog(self):
        self.setupPortletIndexes()
        self.setupPortletMetadata()
            
    def setupPortletIndexes(self):
        catalog = getToolByName(self.portal, 'portal_cpsportlets_catalog')
        indexes = (
            ('eventIds', 'KeywordIndex', None),
            )
        for id, type, extra in indexes:
            if id in catalog.indexes() is not None:
                catalog.delIndex(id)
            catalog.addIndex(id, type, extra)

    def setupPortletMetadata(self):
        catalog = getToolByName(self.portal, 'portal_cpsportlets_catalog')
        metadata = (
            'eventIds',
            )
        for id in metadata:
            if not catalog._catalog.schema.has_key(id):
                catalog.addColumn(id, None)

###############################################
# __call__
###############################################

def install(self):
    """Installation is done here.
    """
    installer = CPSPortletsInstaller(self)
    installer.install()
    return installer.logResult()

