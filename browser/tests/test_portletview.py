# -*- coding: iso-8859-15 -*-
# (C) Copyright 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziad� <tz@nuxeo.com>
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
# $Id:$

import os
import sys
import unittest

from zope.testing import doctest
from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase
from Products.CPSPortlets.tests import CPSPortletsTestCase
from Products.CPSPortlets.browser.portletview import PortletView

class PortletViewTests(CPSPortletsTestCase.CPSPortletsTestCase):
    def afterSetUp(self):
        self.login('manager')

    def beforeTearDown(self):
        self.logout()

    def testPortletRendering(self):
        # XXX need to check portlet_language behavior
        not_tested = ('portlet_language',)
        portlets = getToolByName(self.portal, 'portal_cpsportlets')

        for portlet_id in portlets.objectIds():
            if portlet_id in not_tested:
                continue
            portletviewer = PortletView(self.portal.sections, None)
            result = portletviewer.render(portlet_id)
            if result.strip() == '':
                continue
            self.assert_(result.startswith('<div id="%s">' % portlet_id))

    def testValidXHTML(self):
        htmlpage = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

        <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
          <head>
            <title>My Portlet, alone</title>
          </head>
          <body>
          %s
          </body>
        </html>
        """

        # XXX portlets to be checked (img tag issue)
        not_tested = ('portlet_language', 'portlet_text_about_cps',
                      'portlet_text_cps', 'portlet_text_start_cps',
                      'portlet_text_welcome3')

        portlets = getToolByName(self.portal, 'portal_cpsportlets')

        fakepage = ''
        for portlet_id in portlets.objectIds():
            if portlet_id in not_tested:
                continue
            portletviewer = PortletView(self.portal, None)
            result = portletviewer.render(portlet_id)
            if result.strip() == '':
                continue
            fakepage += '\n<div>**** portlet %s ****</div>\n%s\n\n' \
                        % (portlet_id, result)

        self.assertValidXHTML(htmlpage % fakepage)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PortletViewTests)
        ))

if __name__ == '__main__':
    unittest.main(default="test_suite")
