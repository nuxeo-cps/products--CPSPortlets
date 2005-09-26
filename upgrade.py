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
    return "Obsolete CPSPortlets skins removed."
