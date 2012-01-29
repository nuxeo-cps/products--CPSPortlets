import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Acquisition import aq_base

from Testing import ZopeTestCase

from Products.CPSDefault.tests import CPSDefaultTestCase

from Products.CMFCore.utils import getToolByName

class TestPortlets(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)

        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets
        # Remove the default portlets installation
        if '.cps_portlets' in self.portal.objectIds():
            self.portal.manage_delObjects(['.cps_portlets'])

    def beforeTearDown(self):
        self.logout()

class TestLocalPortletsAsRoot(TestPortlets):
    login_id = 'manager'

    def test_createPortlet(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        container_id = ptltool.getPortletContainerId()
        len_portlet_before = len(ptltool.items())
        portlets = ptltool.getPortlets(context=working_context)
        len_before = len(portlets) 
        ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        self.assert_(len(ptltool.items()) == len_portlet_before)
        portlets = ptltool.getPortlets(context=working_context)
        self.assertEqual(len(portlets), len_before + 1)
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

    def test_view_links(self):
        ptltool = self.ptltool
        definition_folder = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=definition_folder)
        portlets_container = ptltool.getPortletContainer(
            context=definition_folder)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)

        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.invokeFactoryFor(definition_folder, 'Workspace', 'subw')
        subw = definition_folder.subw

        def assert_path(view_name, context_obj, pattern):
            """Generate path and check against pattern.
            in pattern, %s will be replaced by portlet id
            """
            res = portlet.viewAbsoluteUrlPath(view_name,
                                              context_obj=context_obj)
            self.assertEquals(res, pattern % portlet_id)

        assert_path('rss_2_0', subw, '/portal/workspaces/.cps_portlets/%s'
                    '/.context/subw/.view/rss_2_0')
        assert_path('rss_2_0', None, '/portal/workspaces/.cps_portlets/%s'
                    '/.context/.view/rss_2_0')
        assert_path('rss_2_0', definition_folder,
                    '/portal/workspaces/.cps_portlets/%s'
                    '/.context/.view/rss_2_0')


    def test_render_shield(self):
        ptltool = self.ptltool
        # create a portlet with broken render()
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context)
        container = ptltool.getPortletContainer(context=working_context)
        portlet = container.getPortletById(portlet_id)
        def render(**kw):
            raise RuntimeError('testshield')
        portlet.render = render


        # Shield on by default
        del ptltool.shield_disabled # CPSTestCase sets to True
        try:
            portlet.render_cache()
        except RuntimeError, e:
            if str(e) == 'testshield':
                self.fail("Shield did not catch exception")
            else:
                raise

        # Shield on, explicit
        ptltool.shield_disabled = False
        try:
            portlet.render_cache()
        except RuntimeError, e:
            if str(e) == 'testshield':
                self.fail("Shield did not catch exception")
            else:
                raise

        # Shield lifted
        ptltool.shield_disabled = True
        try:
            portlet.render_cache()
        except RuntimeError, e:
            self.assertEquals(str(e), 'testshield')

    def test_getPortletContext(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assert_(ptltool.getPortletContext(portlet) == working_context)

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

    def test_isLocal(self):
        ptltool = self.ptltool
        working_context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assert_(portlet.isLocal())
        self.assert_(not portlet.isGlobal())

class TestLocalPortletsAsMember(CPSDefaultTestCase.CPSDefaultTestCase):
    login_id = 'member'

    def afterSetUp(self):
        #create cps test user
        for u in ('member',):
            self.portal.acl_users._doAddUser(name=u, password=u, confirm=u,
                roles=('Member',), domains=None)

        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()

        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets
        # Remove the default portlets installation
        if '.cps_portlets' in self.portal.objectIds():
            self.portal.manage_delObjects(['.cps_portlets'])

    def beforeTearDown(self):
        self.logout()

    def test_createPortlet(self):
        ptltool = self.ptltool
        working_context = self.portal.members.member
        container_id = ptltool.getPortletContainerId()
        len_before = len(ptltool.items())
        portlets = ptltool.getPortlets(context=working_context)
        len_portlet_before = len(portlets)
        ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        self.assert_(len(ptltool.items()) == len_before)
        portlets = ptltool.getPortlets(context=working_context)
        self.assertEqual(len(portlets), len_portlet_before + 1)
        self.assertEqual(container_id in working_context.objectIds(), 1)

    def test_render(self):
        ptltool = self.ptltool
        working_context = self.portal.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(portlet.render())

    def test_isCPSPortlet(self):
        ptltool = self.ptltool
        working_context = self.portal.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        self.assert_(aq_base(portlet).isCPSPortlet())

    def test_createPortlet_with_slot(self):
        ptltool = self.ptltool
        working_context = self.portal.members.member
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
        working_context = self.portal.members.member
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
        working_context = self.portal.members.member
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
        working_context = self.portal.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet', context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        portlet.setSlot('any slot')
        self.assert_(portlet.slot == 'any slot')

    def test_getOrder(self):
        ptltool = self.ptltool
        working_context = self.portal.members.member
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
        working_context = self.portal.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        self.assertEqual(portlets_container in working_context.objectValues(), 1)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertNotEqual(portlet, None)
        portlet.setOrder(4)
        self.assert_(portlet.order == 4)

    def test_isLocal(self):
        ptltool = self.ptltool
        working_context = self.portal.members.member
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=working_context)
        portlets_container = ptltool.getPortletContainer(context=working_context)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assert_(portlet.isLocal())
        self.assert_(not portlet.isGlobal())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLocalPortletsAsRoot))
    suite.addTest(unittest.makeSuite(TestLocalPortletsAsMember))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
