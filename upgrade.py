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

def upgrade_335_336_portlets(context):
    """Migrates the CPS Portlets indexes to portal_cpsportlets
    """
    ptool = getToolByName(context, 'portal_cpsportlets')
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

def upgrade_338_340_themes(context):
    """Attempts to upgrade existing themes to support the boxless setup
 
    see: http://svn.nuxeo.org/trac/pub/ticket/1161

    For each theme:
    - the script looks for the cell that contains the "Main Content Templet"
    - it adds a 'content_well' slot above it

    if a 'content_well' slot is found, nothing will be done.

    if the "Main Content Templet" is not found nothing is done.
    (the upgrade must be done manually)

    """

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
            log("  Main Content Templet found in the '%s' theme" % \
                theme.getId())

            container = templet.getContainer()
            if SLOT_ID in [slot.box_group for slot in
                             container.objectValues(SLOT_TYPE)]:
                log("  '%s' slot already present, skipping ..." % SLOT_ID)
                continue
            slot = container.addContent(type_name=SLOT_TYPE, xpos=templet.xpos,
                                        ypos=templet.getVerticalPosition()-1)
            slot.setProperty('title', 'Content well')
            slot.setProperty('box_group', SLOT_ID)
            slot.setProperty('macroless', 1)
            slot.setProperty('boxlayout', 'plain')
            log("  Added a '%s' slot." % SLOT_ID)
    return '\n'.join(logger)

def upgrade_338_340_portlets(context):
    """Attempts to update portlets to support the boxless setup

    see: http://svn.nuxeo.org/trac/pub/ticket/1161
    """

    logger = []
    log = logger.append
    log('CPSPortlets: migrating to the boxless setup: upgrading portlets.')

    # TODO
    log(' TODO ...')

    return '\n'.join(logger)

