import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Acquisition import aq_base

from Testing import ZopeTestCase

from Products.CPSDefault.tests import CPSDefaultTestCase

# XXX hardcoded interval
ORDER_INTERVAL = 10

class TestPortlets(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()

        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets

    def beforeTearDown(self):
        self.logout()

class TestMovePortletsAsRoot(TestPortlets):
    login_id = 'root'

    def test_insertPortlet_same_slot_1(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        working_slot = 'slot'
        portlet1_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=working_context,
                                            slot=working_slot,
                                            order=1)
        portlet2_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=working_context,
                                            slot=working_slot,
                                            order=2)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        portlet1 = portlets_container.getPortletById(portlet1_id)
        portlet2 = portlets_container.getPortletById(portlet2_id)
        # move portlet2 in the place ot portlet1
        ptltool.insertPortlet(portlet2, slot=working_slot, order=1)
        self.assert_(portlet2.order == 1)
        self.assert_(portlet1.order == 1 + ORDER_INTERVAL)

    def test_insertPortlet_same_slot_2(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        working_slot = 'slot'
        portlet1_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=working_context,
                                            slot=working_slot,
                                            order=1)
        portlet2_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=working_context,
                                            slot=working_slot,
                                            order=20)
        portlet3_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=working_context,
                                            slot=working_slot,
                                            order=30)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        portlet1 = portlets_container.getPortletById(portlet1_id)
        portlet2 = portlets_container.getPortletById(portlet2_id)
        portlet3 = portlets_container.getPortletById(portlet3_id)
        # move portlet2 in the place ot portlet1
        # portlet3 is unchanged 
        ptltool.insertPortlet(portlet2, slot=working_slot, order=1)
        self.assert_(portlet2.order == 1)
        self.assert_(portlet1.order == 1 + ORDER_INTERVAL)
        self.assert_(portlet3.order == 30)
        self.assert_(portlet1.slot == working_slot)
        self.assert_(portlet2.slot == working_slot)
        self.assert_(portlet3.slot == working_slot)

    def test_insertPortlet_different_slots_1(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        src_slot = 'src slot'
        dest_slot = 'dest slot'
        portlet1_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=working_context,
                                            slot=src_slot,
                                            order=1)
        portlet2_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=working_context,
                                            slot=dest_slot,
                                            order=1)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        portlet1 = portlets_container.getPortletById(portlet1_id)
        portlet2 = portlets_container.getPortletById(portlet2_id)
        ptltool.insertPortlet(portlet1, slot=dest_slot, order=1)
        self.assert_(portlet1.order == 1)
        self.assert_(portlet2.order == 1 + ORDER_INTERVAL)
        self.assert_(portlet1.slot == dest_slot)
        self.assert_(portlet2.slot == dest_slot)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMovePortletsAsRoot))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
