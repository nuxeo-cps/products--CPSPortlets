import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSPortletsTestCase

from Products.CMFCore.utils import getToolByName

class TestFixtures(CPSPortletsTestCase.CPSPortletsTestCase):
    def afterSetUp(self):
        self.login('manager')

    def beforeTearDown(self):
        self.logout()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFixtures))
    return suite
