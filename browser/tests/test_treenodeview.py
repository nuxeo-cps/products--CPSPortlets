# -*- coding: iso-8859-15 -*-
# (C) Copyright 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
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
"""tests for treenodeview

$Id$
"""
import os
import sys
import unittest

from zope.testing import doctest

from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName

from Products.CPSPortlets.tests import CPSPortletsTestCase
from Products.CPSPortlets.browser.treenodeview import TreeNodeView

class TreeNodeViewTests(CPSPortletsTestCase.CPSPortletsTestCase):
    def afterSetUp(self):
        self.login('manager')

    def beforeTearDown(self):
        self.logout()

    def testTraversalWithVirtualHost(self):
        # making sure we catch the root wheter the portal is
        # behind apache or not
        nodeview = TreeNodeView(self.portal.sections, None)
        self.assertEquals(nodeview._rootRestrictedTraverse('/sections'),
                          nodeview._rootRestrictedTraverse('/portal/sections'))

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        unittest.makeSuite(TreeNodeViewTests)
        ))

if __name__ == '__main__':
    unittest.main(default="test_suite")
