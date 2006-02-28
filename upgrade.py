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

from Products.CMFCore.utils import getToolByName

def upgrade_335_336_portlets_catalog(context):
    """Migrates the CPS Portlets indexes to portal_cpsportlets
    """
    ptool = getToolByName(context, 'portal_cpsportlets')
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

    tmtool = getToolByName(context, 'portal_themes')
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
    cache_params = ptool.getCacheParameters()
    bc_params = cache_params['Breadcrumbs Portlet']
    if 'request:breadcrumb_set' not in bc_params:
        bc_params.append('request:breadcrumb_set')
        ptool.updateCacheParameters(cache_params)
    return "Cache parameters updated"

def check_upgrade_338_340_portlets_cache(portal):
    ptool = getToolByName(portal, 'portal_cpsportlets')
    return ('request:breadcrumb_set' not in
            ptool.getCacheParametersFor('Breadcrumbs Portlet'))

def upgrade_338_340_portlets_cache_bug_1470(context):
    ptool = getToolByName(context, 'portal_cpsportlets')
    old_params = ptool.getCacheParametersFor('Content Portlet')
    new_params = []
    upgrade = False
    for param in old_params:
        if param.startswith('event_ids:'):
            values = param.split(':')[1].split(',')
            if 'workflow_accept' not in values:
                values.append('workflow_accept')
            if 'workflow_reject' not in values:
                values.append('workflow_reject')
            new_params.append('event_ids:' + ','.join(values))
            upgrade = True
        else:
            new_params.append(param)
    if upgrade:
        ptool.updateCacheParameters({'Content Portlet': new_params})
    return "Cache parameters updated"

def check_upgrade_338_340_portlets_cache_bug_1470(portal):
    ptool = getToolByName(portal, 'portal_cpsportlets')
    params = ptool.getCacheParametersFor('Content Portlet')
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
