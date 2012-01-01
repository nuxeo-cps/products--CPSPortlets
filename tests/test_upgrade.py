 # (C) Copyright 2012 CPS-CMS Community <http://cps-cms.org/>
 # Authors:
 #     G. Racinet <gracinet@cps-cms.org>
 #
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 2 of the License, or
 # (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test portlet upgrades."""

import unittest
from Testing import ZopeTestCase
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

from Products.CMFCore.utils import getToolByName
from Products.CPSCore.utils import bhasattr


class TestUpgrade(CPSTestCase):

    def afterSetUp(self):
        """Create structure of sections with containers."""
        self.login('manager')
        self.wftool = wftool = getToolByName(self.portal, 'portal_workflow')
        sections = self.portal.sections
        wftool.invokeFactoryFor(sections, 'Section', 'subs')
        self.section = sections.subs
        self.ptool = ptool = getToolByName(self.portal, 'portal_cpsportlets')

    def test_upgrade_render_dispatch(self):
        # test with fresh (same as upgraded) profile
        from Products.CPSPortlets.upgrade import upgrade_render_dispatch

        ptl_id = self.ptool.createPortlet('Navigation Portlet',
                                          context=self.section)
        ptl = self.ptool.getPortletContainer(context=self.section)[ptl_id]
        ptl.display = u'folder_contents' # not a field anymore in profiles

        upgrade_render_dispatch(self.portal)
        self.assertEquals(ptl.render_view_name, 'folder_contents')
        self.assertFalse(bhasattr(ptl, 'display'))

    def test_upgrade_render_dispatch_idempotency(self):
        from Products.CPSPortlets.upgrade import \
            upgrade_container_render_dispatch

        container = self.portal['.cps_portlets']
        ptl = container['portlet_navigation_workspaces']
        ptl.display = u'hierarchical_tree'
        delattr(ptl, 'render_view_name') # there's a value in current profile

        upgrade_container_render_dispatch(container)
        self.assertEquals(ptl.render_view_name, 'hierarchical_tree')
        self.assertFalse(bhasattr(ptl, 'display'))

        # second run to check idempotency
        # (before protection, the result was '')
        upgrade_container_render_dispatch(container)
        self.assertEquals(ptl.render_view_name, 'hierarchical_tree')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUpgrade))
    return suite
