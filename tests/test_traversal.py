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

class PortletTraversalTestCase(CPSTestCase):

    def test_breaking_news(self):
        portlet = self.portal['.cps_portlets']['portlet_content_breaking_news']
        ptl_path = '/'.join(portlet.getPhysicalPath())

        # basic case
        response = self.zopePublish(ptl_path + '/rss_2_0/truc.rss')
        self.assertEquals(response.getStatus(), 200)
        self.assertTrue(response.getHeader('Content-Type').startswith(
                'application/rss+xml'))

        # successful traversal from portlet definiton folder
        response = self.zopePublish(
            ptl_path + '/.context/sections/.view/rss_2_0/truc.rss')
        self.assertEquals(response.getStatus(), 200)
        self.assertTrue(response.getHeader('Content-Type').startswith(
                'application/rss+xml'))

        # unsuccessful traversal from portlet definition folder
        response = self.zopePublish(
            ptl_path + '/.context/nosuch/.view/rss_2_0/truc.rss')
        self.assertEquals(response.getStatus(), 404)


def test_suite():
    return unittest.makeSuite(PortletTraversalTestCase)

