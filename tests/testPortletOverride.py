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

        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets

    def beforeTearDown(self):
        self.logout()

def createTestPortlet(self, context, slot):
    portlet_id = self.ptltool.createPortlet(
        ptype_id='Dummy Portlet',
        context=context,
        slot=slot)
    portlet_container = self.ptltool.getPortletContainer(context=context)
    return portlet_container.getPortletById(portlet_id)

class TestPortletOverride(TestPortlets):
    login_id = 'manager'

    def test_same_folder_same_slot(self):
        context = self.portal.workspaces
        slot = 'any slot'
        portlet1 = createTestPortlet(self, context=context, slot=slot)
        portlet2 = createTestPortlet(self, context=context, slot=slot)
        portlet1.slot_override = 0
        portlet2.slot_override = 1
        portlet1.disable_override = 0
        portlets_in_slot = self.ptltool.getPortlets(context=context, slot=slot)
        self.assert_(portlet2 in portlets_in_slot)
        # portlet2 does not override portlet1 since they are in the same context
        self.assert_(portlet1 in portlets_in_slot)

    def test_different_folders_same_slot(self):
        ptltool = self.ptltool
        context1 = self.portal.workspaces
        context2 = self.portal.workspaces.members
        slot = 'any slot'
        portlet1 = createTestPortlet(self, context=context1, slot=slot)
        portlet2 = createTestPortlet(self, context=context2, slot=slot)
        portlet1.slot_override = 0
        portlet2.slot_override = 1
        portlet1.disable_override = 0
        portlets_in_context1 = ptltool.getPortlets(context=context1, slot=slot)
        portlets_in_context2 = ptltool.getPortlets(context=context2, slot=slot)
        self.assert_(portlet1 in portlets_in_context1)
        self.assert_(portlet2 in portlets_in_context2)
        # portlet2 overrides portlet1
        self.assert_(portlet1 not in portlets_in_context2)

    def test_different_folders_different_slots(self):
        ptltool = self.ptltool
        context1 = self.portal.workspaces
        context2 = self.portal.workspaces.members
        slot1 = 'any slot'
        slot2 = 'another slot'
        portlet1 = createTestPortlet(self, context=context1, slot=slot1)
        portlet2 = createTestPortlet(self, context=context2, slot=slot2)
        portlet1.slot_override = 0
        portlet2.slot_override = 1
        portlet1.disable_override = 0
        portlets_in_context1_slot1 = ptltool.getPortlets(context=context1, slot=slot1)
        portlets_in_context2_slot2 = ptltool.getPortlets(context=context2, slot=slot2)
        portlets_in_context2_slot1 = ptltool.getPortlets(context=context2, slot=slot1)
        self.assert_(portlet1 in portlets_in_context1_slot1)
        self.assert_(portlet2 in portlets_in_context2_slot2)
        # portlet2 does not override portlet1 since they are not in the same slot
        self.assert_(portlet1 in portlets_in_context2_slot1)

    def test_disable_override(self):
        ptltool = self.ptltool
        context1 = self.portal.workspaces
        context2 = self.portal.workspaces.members
        slot = 'any slot'
        portlet1 = createTestPortlet(self, context=context1, slot=slot)
        portlet2 = createTestPortlet(self, context=context2, slot=slot)
        portlet1.slot_override = 0
        portlet2.slot_override = 1
        portlet1.disable_override = 1
        portlets_in_context1 = ptltool.getPortlets(context=context1, slot=slot)
        portlets_in_context2 = ptltool.getPortlets(context=context2, slot=slot)
        self.assert_(portlet1 in portlets_in_context1)
        self.assert_(portlet2 in portlets_in_context2)
        # portlet2 does not override portlet1 because portlet1 cannot be overridden
        self.assert_(portlet1 in portlets_in_context2)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletOverride))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
