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

class TestPortletsAsRoot(TestPortlets):
    login_id = 'root'

    def test_createPortlet(self):
        ptltool = self.ptltool
        self.assert_(len(ptltool.items()) == 0)
        ptltool.createPortlet(ptype_id='Dummy Portlet')
        self.assert_(len(ptltool.items()) == 1)

    def test_isCPSPortlet(self):
        ptltool = self.ptltool
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet')
        portlet = getattr(aq_base(ptltool), portlet_id)
        self.assert_(aq_base(portlet).isCPSPortlet())

    def test_createPortlet_with_slot(self):
        ptltool = self.ptltool
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           slot='any slot')
        portlet = getattr(aq_base(ptltool), portlet_id)
        self.assert_(portlet.slot == 'any slot')

    def test_createPortlet_with_order(self):
        ptltool = self.ptltool
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           order=1)
        portlet = getattr(aq_base(ptltool), portlet_id)
        self.assert_(portlet.order == 1)

    def test_getSlot(self):
        ptltool = self.ptltool
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           slot='any slot')
        portlet = getattr(aq_base(ptltool), portlet_id)
        self.assert_(portlet.getSlot() == 'any slot')

    def test_getOrder(self):
        ptltool = self.ptltool
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           order=3)
        portlet = getattr(aq_base(ptltool), portlet_id)
        self.assert_(portlet.getOrder() == 3)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletsAsRoot))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

