import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

from Testing import ZopeTestCase

from Products.CPSDefault.tests import CPSDefaultTestCase

PORTLET_CONTAINER_ID = '.cps_portlets'

class TestPortletsTool(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login('root')
        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets

    def beforeTearDown(self):
        self.logout()

    def test_listPortletSlots_global(self):
        ptltool = self.ptltool
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot1')
        slots = ptltool.listPortletSlots()
        self.assert_(slots == ['slot1'])
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot2')
        slots = ptltool.listPortletSlots()
        self.assert_(slots == ['slot1', 'slot2'])

    def test_listPortletSlots_local(self):
        ptltool = self.ptltool
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot1',
                              context=self.portal.workspaces)
        slots = ptltool.listPortletSlots()
        self.assert_(slots == ['slot1'])
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot2',
                              context=self.portal.sections)
        slots = ptltool.listPortletSlots()
        self.assert_(slots == ['slot1', 'slot2'])

    def test_listPortletTypes(self):
        ptltool = self.ptltool
        types = ptltool.listPortletTypes()
        # XXX the complete list of types is not known a priori.
        self.assert_('Dummy Portlet' in types)

    def test_getPortletContainerId(self):
        ptltool = self.ptltool
        container_id = ptltool.getPortletContainerId()
        self.assert_(container_id == PORTLET_CONTAINER_ID) 

    def test_getPortlets_in_workspaces(self):
        ptltool = self.ptltool
        portlet1_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=self.portal.workspaces)
        portlet2_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=self.portal.workspaces)
        ws_portlets = ptltool.getPortlets(context=self.portal.workspaces)
        ws_portlets_ids = [p.getId() for p in ws_portlets]
        self.assert_(ws_portlets_ids == [portlet1_id, portlet2_id]) 
        s_portlets = ptltool.getPortlets(context=self.portal.sections)
        self.assert_(s_portlets == []) 

    def test_getPortlets_in_workspaces_members(self):
        ptltool = self.ptltool
        members_folder = self.portal.workspaces.members
        portlet1_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=self.portal.workspaces)
        portlet2_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=members_folder)
        ws_portlets = ptltool.getPortlets(context=self.portal.workspaces)
        ws_portlets_ids = [p.getId() for p in ws_portlets]
        self.assert_(ws_portlets_ids == [portlet1_id]) 
        members_portlets = ptltool.getPortlets(context=members_folder)
        members_portlets_ids = [p.getId() for p in members_portlets]
        self.assert_(members_portlets_ids == [portlet1_id, portlet2_id]) 

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletsTool))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

