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

class TestLocalPortletsAsRoot(TestPortlets):
    login_id = 'root'

    def test_createPortlet(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        container_id = ptltool.getPortletContainerId()
        self.assert_(len(ptltool.items()) == 0)
        portlets = ptltool.getPortlets(context=working_context)
        self.assertEqual(len(portlets), 0)
        ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        self.assert_(len(ptltool.items()) == 0)
        portlets = ptltool.getPortlets(context=working_context)
        self.assertEqual(len(portlets), 1)
        self.assertEqual(container_id in working_context.objectIds(), 1)

    def test_render(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.render())

    def test_isCPSPortlet(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(aq_base(portlet).isCPSPortlet())

    def test_createPortlet_with_slot(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           slot='any slot')
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.slot == 'any slot')

    def test_createPortlet_with_order(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           order=1)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.order == 1)

    def test_getSlot(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           slot='any slot')
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.getSlot() == 'any slot')

    def test_setSlot(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        portlet.setSlot('any slot')
        self.assert_(portlet.slot == 'any slot')

    def test_getOrder(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           order=3)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.getOrder() == 3)

    def test_setOrder(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        portlet.setOrder(4)
        self.assert_(portlet.order == 4)


class TestLocalPortletsAsMember(CPSDefaultTestCase.CPSDefaultTestCase):
    login_id = 'member'

    def afterSetUp(self):
        #create cps test user
        for u in ('member',):
            self.portal.acl_users._addUser(name=u, password=u, confirm=u,
                roles=('Member',), domains=None)

        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()

        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets

    def beforeTearDown(self):
        self.logout()

    def test_createPortlet(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        container_id = ptltool.getPortletContainerId()
        self.assert_(len(ptltool.items()) == 0)
        portlets = ptltool.getPortlets(context=working_context)
        self.assertEqual(len(portlets), 0)
        ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        self.assert_(len(ptltool.items()) == 0)
        portlets = ptltool.getPortlets(context=working_context)
        self.assertEqual(len(portlets), 1)
        self.assertEqual(container_id in working_context.objectIds(), 1)

    def test_render(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.render())

    def test_isCPSPortlet(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(aq_base(portlet).isCPSPortlet())

    def test_createPortlet_with_slot(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           slot='any slot')
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.slot == 'any slot')

    def test_createPortlet_with_order(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           order=1)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.order == 1)

    def test_getSlot(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           slot='any slot')
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.getSlot() == 'any slot')

    def test_setSlot(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        portlet.setSlot('any slot')
        self.assert_(portlet.slot == 'any slot')

    def test_getOrder(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context,
                                           order=3)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.getOrder() == 3)

    def test_setOrder(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        portlet.setOrder(4)
        self.assert_(portlet.order == 4)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLocalPortletsAsRoot))
    suite.addTest(unittest.makeSuite(TestLocalPortletsAsMember))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
