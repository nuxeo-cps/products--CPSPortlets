import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Acquisition import aq_base

from Testing import ZopeTestCase

from Products.CPSDefault.tests import CPSDefaultTestCase

class TestPortlets(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()

        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets

    def beforeTearDown(self):
        self.logout()

class TestPortletWidgetsAsRoot(TestPortlets):
    login_id = 'root'

    def test_DummyPortlet(self):
        ptltool = self.ptltool
        self.assert_(len(ptltool.items()) == 0)
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet')
        self.assert_(len(ptltool.items()) == 1)
        portlet = ptltool.getPortletById(portlet_id)
        self.assert_(portlet.render())

    def test_SearchPortlet(self):
        ptltool = self.ptltool
        self.assert_(len(ptltool.items()) == 0)
        portlet_id = ptltool.createPortlet(ptype_id='Search Portlet')
        self.assert_(len(ptltool.items()) == 1)
        portlet = ptltool.getPortletById(portlet_id)
        self.assert_(portlet.render())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletWidgetsAsRoot))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

