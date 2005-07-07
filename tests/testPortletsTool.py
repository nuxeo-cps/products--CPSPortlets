import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

from Testing import ZopeTestCase

from Products.CPSDefault.tests import CPSDefaultTestCase

PORTLET_CONTAINER_ID = '.cps_portlets'

class TestPortletsTool(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login_id = 'manager'
        self.login(self.login_id)
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST['AUTHENTICATED_USER'] = self.login_id
        self.ptltool = self.portal.portal_cpsportlets
        # Remove the default portlets installation
        if '.cps_portlets' in self.portal.objectIds():
            self.portal.manage_delObjects(['.cps_portlets'])

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

    def test_notify_event(self):
        ptltool = self.ptltool
        # XXX
        # To be sure the tests will be updated when the implementation will be
        # done
        self.assertEqual(ptltool.notify_event('fake_event', None, {}), None)

    def test_listPortletsInterestedInEvent(self):
        ptltool = self.ptltool

        # No portlets found already
        portlets = ptltool.listPortletsInterestedInEvent('fake_event', '', '')
        self.assertEqual(portlets, [])

        new_id = ptltool.createPortlet('Dummy Portlet')
        self.assertNotEqual(new_id, None)

        nportlet = ptltool.getPortletById(new_id)
        self.assertNotEqual(nportlet, None)

        res = nportlet.addEvent('fake_event')
        self.assertEqual(res, 0)

        # No way to add two time the same event
        res = nportlet.addEvent('fake_event')
        self.assertEqual(res, 1)

        events = nportlet.listEvents()
        self.assertEqual(events, (('fake_event', (), ()),) )

        # XXX to be implemented
        self.assertEqual(nportlet.sendEvent(event_id='fake_event', folder_path='', portal_type=''), 0)
        self.assertEqual(nportlet.sendEvent(event_id='fake_eventXXX', folder_path='', portal_type=''), 1)

    def test_FindCacheEntriesByUser(self):
        user = self.login_id
        ptltool = self.ptltool
        context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           slot='slot1',
                                           context=context)
        portlets_container = ptltool.getPortletContainer(context=context)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assert_(ptltool.findCacheEntriesByUser(user) == [])
        # clean the cache
        cache = ptltool.getPortletCache()
        cache.invalidate()
        # render the portlet
        portlet.render_cache()
        entries = ptltool.findCacheEntriesByUser(user)
        self.assert_(entries == [(portlet.getPhysicalPath(), 'user_%s' % user)])

    def test_invalidateCacheEntriesByUser(self):
        user = self.login_id
        ptltool = self.ptltool
        context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           slot='slot1',
                                           context=context)
        portlets_container = ptltool.getPortletContainer(context=context)
        portlet = portlets_container.getPortletById(portlet_id)
        portlet_path = portlet.getPhysicalPath()
        # clean the cache
        cache = ptltool.getPortletCache()
        cache.invalidate()
        self.assert_(ptltool.findCacheEntriesByUser(user) == [])
        # render the portlet
        portlet.render_cache()
        entries = ptltool.findCacheEntriesByUser(user)
        self.assert_(entries == [(portlet_path, 'user_%s' % user)])
        # invalidate the entry for another user
        ptltool.invalidateCacheEntriesByUser('dummy user')
        self.assert_(ptltool.findCacheEntriesByUser(user) != [])
        # invalidate the entry for this user
        ptltool.invalidateCacheEntriesByUser(user)
        self.assert_(ptltool.findCacheEntriesByUser(user) == [])

    def test_invalidateCacheEntriesById(self):
        user = self.login_id
        ptltool = self.ptltool
        context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           slot='slot1',
                                           context=context)
        portlets_container = ptltool.getPortletContainer(context=context)
        portlet = portlets_container.getPortletById(portlet_id)
        portlet_path = portlet.getPhysicalPath()
        # clean the cache
        cache = ptltool.getPortletCache()
        cache.invalidate()
        # render the portlet
        portlet.render_cache()
        self.assert_(len(cache.getEntries()) > 0)
        # invalidate the entry
        ptltool.invalidateCacheEntriesById(portlet_path)
        self.assert_(len(cache.getEntries()) == 0)

    def test_renderIcon(self):
        ptltool = self.ptltool
        ttool = self.portal.portal_types
        # first rendering: storing the result in the cache
        res = ptltool.renderIcon('Dummy Portlet', '/cps/', 'dummy portlet')
        expected = '<img src="/cps/portlet_icon.png" width="16" height="16" alt="dummy portlet" />'
        self.assert_(res == expected)
        # fetching the entry from the cache
        res = ptltool.renderIcon('Dummy Portlet', '/cps/', 'dummy portlet')
        self.assert_(res == expected)
        # default parameters
        res = ptltool.renderIcon('Dummy Portlet')
        expected = '<img src="portlet_icon.png" width="16" height="16" alt="" />'
        self.assert_(res == expected)
        # unknown type
        res = ptltool.renderIcon('Unknown type for testing', '/', '')
        self.assert_(res == None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletsTool))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
