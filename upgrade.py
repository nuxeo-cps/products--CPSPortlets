# Copyright 2005 Nuxeo SARL <http://nuxeo.com>
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

import logging
import transaction
from Products.CMFCore.utils import getToolByName
from PortletsCatalogTool import reindex_portlets_catalog

def upgrade_335_336_portlets_catalog(context):
    """Migrates the CPS Portlets indexes to portal_cpsportlets
    """
    ptool = getToolByName(context, 'portal_cpsportlets', None)
    if ptool is None:
        return 
    ptcatalog = getToolByName(context, 'portal_cpsportlets_catalog', None)
    if ptcatalog is None:
        mt = 'CPS Portlets Catalog Tool'
        context.manage_addProduct['CPSPortlets'].manage_addTool(mt)
        ptcatalog = getToolByName(context, 'portal_cpsportlets_catalog')
    catalog = getToolByName(context, 'portal_catalog')
    portlets = catalog.searchResults(portal_type=ptool.listPortletTypes())
    for brain in portlets:
        portlet = brain.getObject()
        try:
            catalog.unindexObject(portlet)
        except KeyError:
            # Already removed.
            pass
        # Reindex within the dedicated catalog
        ptcatalog.indexObject(portlet)
    return "Portlet indexes migrated"

def check_upgrade_335_336_portlets_catalog(portal):
    ptool = getToolByName(portal, 'portal_cpsportlets', None)
    if ptool is None:
        return False
    ptcatalog = getToolByName(portal, 'portal_cpsportlets_catalog', None)
    if ptcatalog is None:
        return True
    return not bool(len(ptcatalog.unrestrictedSearchResults()))

def upgrade_335_336_skins(context):
    """Remove obsolete skins
    """
    SKINS_TO_REMOVE = ('cpsportlets_widgets_cps3', 'cpsportlets_widgets_plone2')
    stool = getToolByName(context, 'portal_skins')
    skins = stool.objectIds()
    for skin_id in SKINS_TO_REMOVE:
        if skin_id in skins:
            stool.manage_delObjects(skin_id)

    # Reset the skin cache
    portal = getToolByName(context, 'portal_url').getPortalObject()
    portal._v_reset_skins = 1

    return "Obsolete CPSPortlets skins removed."

def upgrade_338_340_themes(context, check=False):
    """Attempts to upgrade existing themes to support the boxless setup
 
    see: http://svn.nuxeo.org/trac/pub/ticket/1161

    For each theme:
    - the script looks for the cell that contains the "Main Content Templet"
    - it adds a 'content_well' slot above it

    if a 'content_well' slot is found, nothing will be done.

    if the "Main Content Templet" is not found nothing is done.
    (the upgrade must be done manually)

    """

    if not check:
        logger = []
        log = logger.append
        log('CPSPortlets: migrating to the boxless setup: upgrading themes.')

    SLOT_ID = 'content_well'
    SLOT_TYPE = 'Portal Box Group Templet'

    tmtool = getToolByName(context, 'portal_themes', None)
    if check:
        try:
            from Products.CPSSkins.PortalThemesTool import PortalThemesTool
        except ImportError:
            return False
        return tmtool is not None and isinstance(tmtool, PortalThemesTool)

    for theme in tmtool.getThemes():
        for templet in theme.getTemplets():
            if not templet.meta_type == 'Main Content Templet':
                continue
            if not check:
                log("  Main Content Templet found in the '%s' theme" %
                    theme.getId())

            container = templet.getContainer()
            if SLOT_ID in [slot.box_group for slot in
                             container.objectValues(SLOT_TYPE)]:
                if not check:
                    log("  '%s' slot already present, skipping ..." % SLOT_ID)
                continue
            if check:
                return True
            slot = container.addContent(type_name=SLOT_TYPE, xpos=templet.xpos,
                                        ypos=templet.getVerticalPosition()-1)
            slot.setProperty('title', 'Content well')
            slot.setProperty('box_group', SLOT_ID)
            slot.setProperty('macroless', 1)
            slot.setProperty('boxlayout', 'plain')
            log("  Added a '%s' slot." % SLOT_ID)
    if check:
        return False
    return '\n'.join(logger)

def check_upgrade_338_340_themes(portal):
    return upgrade_338_340_themes(portal, check=True)

def upgrade_338_340_portlets_cache(context):
    ptool = getToolByName(context, 'portal_cpsportlets')
    try:
        bc_params = ptool.getCacheParametersFor('Breadcrumbs Portlet')
    except AttributeError:
        ptool.initializeCacheParameters()
        ptool.resetCacheParameters()
    else:
        if 'request:breadcrumb_set' not in bc_params:
            bc_params.append('request:breadcrumb_set')
            ptool.updateCacheParameters({'Breadcrumbs Portlet': bc_params})
    return "Cache parameters for the Breadcrumbs Portlet updated"

def check_upgrade_338_340_portlets_cache(portal):
    ptool = getToolByName(portal, 'portal_cpsportlets', None)
    if ptool is None:
        return False
    try:
        bc_params = ptool.getCacheParametersFor('Breadcrumbs Portlet')
    except AttributeError:
        # ptool.cache_parameters is missing
        return True
    return ('request:breadcrumb_set' not in bc_params)

def upgrade_338_340_portlets_cache_bug_1470(context):
    ptool = getToolByName(context, 'portal_cpsportlets')
    try:
        old_params = ptool.getCacheParametersFor('Content Portlet')
    except AttributeError:
        ptool.initializeCacheParameters()
        ptool.resetCacheParameters()
    else:
        new_params = []
        upgrade = False
        for param in old_params:
            if param.startswith('event_ids:'):
                values = param.split(':')[1].split(',')
                if 'workflow_accept' not in values:
                    values.append('workflow_accept')
                    upgrade = True
                if 'workflow_reject' not in values:
                    values.append('workflow_reject')
                    upgrade = True
                new_params.append('event_ids:' + ','.join(values))
            else:
                new_params.append(param)
        if upgrade:
            ptool.updateCacheParameters({'Content Portlet': new_params})
    return "Cache parameters for the Content Portlet updated"

def check_upgrade_338_340_portlets_cache_bug_1470(portal):
    ptool = getToolByName(portal, 'portal_cpsportlets', None)
    if ptool is None:
        return False
    try:
        params = ptool.getCacheParametersFor('Content Portlet')
    except AttributeError:
        # ptool.cache_parameters is missing
        return True
    for param in params:
        if not param.startswith('event_ids:'):
            # if there is now 'event_ids' information, obviously the user has
            # changed parameters a lot. we do nothing
            continue
        if param == 'event_ids:':
            # the user has removed all values for 'event_ids:', we do nothing
            return False
        values = param.split(':')[1].split(',')
        if 'workflow_accept' not in values:
            return True
        if 'workflow_reject' not in values:
            return True
    return False

from Products.CPSDocument.upgrade import upgrade_doc_unicode
def upgrade_unicode(portal):
    """Upgrade all portlets to unicode.

    CPS String Field content will be cast to unicode, whereas
    CPS Ascii String Field content will be cast to str
    """

    logger = logging.getLogger('Products.CPSPortlets.upgrades.unicode')
    ptool = portal.portal_cpsportlets

    reindex_portlets_catalog(portal) # really need to ensure that
    logger.info("Starting upgrade of portlets")

    ptls = ptool.listAllPortlets()
    total = len(ptls)
    logger.info("Starting, found %d portlets", total)
    done = 0
    for ptl in ptls:
        if not upgrade_doc_unicode(ptl):
            logger.error("Could not upgrade portlet %s", doc)
            continue
        done += 1
    transaction.commit()
    logger.info("Upgraded %d/%d portlets.", done, total)

    reindex_portlets_catalog(portal)
