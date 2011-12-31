# (C) Copyright 2011 CPS-CMS Community <http://cps-cms.org/>
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

import unittest
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSPortlets.browser.basicportlets import BreadCrumbsPortletView

class TestBreadCrumbs(CPSTestCase):

    def test_breadcrumbs(self):
        # TODO: less dependencies on CPSDefault's configuration
        # should use it only for portlet type & schema definitions
        self.login('manager')
        ptl = self.portal['.cps_portlets'].portlet_breadcrumbs
        view = ptl.getBrowserView(self.portal.workspaces, self.app.REQUEST, {})
        self.assertEquals(view.breadcrumbs(), [
                {'url': '/portal',
                 'longtitle': 'CPSDefault Portal',
                 'rpath': '', 'id': 'portal',
                 'title': 'CPSDefault Portal'},
                {'url': '/portal/workspaces',
                 'longtitle': u'Workspaces',
                 'rpath': 'workspaces', 'id': 'workspaces',
                 'title': u'Workspaces'}])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBreadCrumbs))
    return suite

