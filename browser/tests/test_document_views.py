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
from Products.CMFCore.utils import getToolByName
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSPortlets.browser.documentportlet import DocumentPortletView


class DocumentPortletIntegration(CPSTestCase):

    def createPortlet(self, **fields):
        self.login('manager')
        ptltool = getToolByName(self.portal, 'portal_cpsportlets')
        ptl_id = ptltool.createPortlet('Document Portlet', **fields)
        self.portlet = ptltool[ptl_id]

    def test_whole_integration(self):
        """We use the bundled title_descr render page to test the whole loop."""
        self.createPortlet(render_view_name='title_descr')
        rendered = self.portlet.render_headers(
            self.app.REQUEST,
            context_obj=self.portal.workspaces)[0].strip()
        self.assertFalse('widget__' in rendered,
                         msg="Rendering wend through layouts")
        # if template changes a lot, we might use a special custom rendering for
        # tests
        self.assertTrue('<h1>Workspaces</h1>' in rendered)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentPortletIntegration))
    return suite

