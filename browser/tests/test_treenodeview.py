##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
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
