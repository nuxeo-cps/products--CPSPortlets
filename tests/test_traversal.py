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

from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces import IPublishTraverse

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

    def test_antitraverse_breaking_news(self):
        # we actually check from the view, that calls itself the traverser
        # this test uses some specifics from Content Portlet view

        portlet_id = 'portlet_content_breaking_news'
        portlet = self.portal['.cps_portlets'][portlet_id]

        self.login('manager')
        ws = self.portal.workspaces
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.invokeFactoryFor(ws, 'Workspace', 'subw')
        subw = ws.subw

        def assert_path(view_name, context_obj, pattern):
            """Generate path and check against pattern.
            in pattern, %s will be replaced by portlet id
            """
            view = portlet.getBrowserView(context_obj, self.app.REQUEST)
            self.assertEquals(view.viewAbsoluteUrlPath(view_name),
                              pattern % portlet_id)

        # breaking_news is not contextual
        assert_path('rss_2_0', subw,
                    '/portal/.cps_portlets/%s/.context/.view/rss_2_0')
        assert_path('rss_2_0', self.portal,
                    '/portal/.cps_portlets/%s/.context/.view/rss_2_0')

        # making the portlet contextual changes the URI with passed context
        portlet.edit(search_type='related')
        assert_path('rss_2_0', subw, '/portal/.cps_portlets/%s'
                    '/.context/workspaces/subw/.view/rss_2_0')
        # Still checking for portal (same as non contextual)
        assert_path('rss_2_0', self.portal,
                    '/portal/.cps_portlets/%s/.context/.view/rss_2_0')




def test_suite():
    return unittest.makeSuite(PortletTraversalTestCase)

