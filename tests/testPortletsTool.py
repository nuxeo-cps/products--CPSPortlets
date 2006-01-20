import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import Unauthorized

from Products.CMFCore.tests.base.utils import has_path

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

        self.ws = self.portal.workspaces
        self.ws.invokeFactory('Workspace', 'subws')

    def beforeTearDown(self):
        self.logout()

    def loginAsWsManager(self):
        # for some tests, we need an user with WorkspaceManager role
        mdir = self.portal.portal_directories['members']
        mdir._createEntry({'id' : 'wsman', 
                           'sn' : 'wsman',
                           'passwd' : 'secret',
                           'roles' : ['Member', 'WorkspaceManager',],
                           }
                          )

        # Now login as the Workspace Manager
        uf = self.portal.acl_users
        user = uf.getUserById('wsman').__of__(uf)        
        newSecurityManager(None, user)

    def test_listPortletSlots_global(self):
        ptltool = self.ptltool
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot1')
        slots = ptltool.listPortletSlots()
        self.assertEquals(slots, ['slot1'])
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot2')
        slots = ptltool.listPortletSlots()
        self.assertEquals(slots, ['slot1', 'slot2'])

    def test_listPortletSlots_local(self):
        ptltool = self.ptltool
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot1',
                              context=self.portal.workspaces)
        slots = ptltool.listPortletSlots()
        self.assertEquals(slots, ['slot1'])
        ptltool.createPortlet(ptype_id='Dummy Portlet',
                              slot='slot2',
                              context=self.portal.sections)
        slots = ptltool.listPortletSlots()
        self.assertEquals(slots, ['slot1', 'slot2'])

    def test_listPortletTypes(self):
        ptltool = self.ptltool
        types = ptltool.listPortletTypes()
        # XXX the complete list of types is not known a priori.
        self.assert_('Dummy Portlet' in types)

    def test_getPortletContainerId(self):
        ptltool = self.ptltool
        container_id = ptltool.getPortletContainerId()
        self.assertEquals(container_id, PORTLET_CONTAINER_ID)

    def test_getPortlets_in_workspaces(self):
        ptltool = self.ptltool
        portlet1_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=self.portal.workspaces)
        portlet2_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=self.portal.workspaces)
        ws_portlets = ptltool.getPortlets(context=self.portal.workspaces)
        ws_portlets_ids = [p.getId() for p in ws_portlets]
        self.assertEquals(ws_portlets_ids, [portlet1_id, portlet2_id])
        s_portlets = ptltool.getPortlets(context=self.portal.sections)
        self.assertEquals(s_portlets, [])

    def test_getPortlets_in_sub_workspaces(self):
        ptltool = self.ptltool
        portlet1_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=self.ws)
        portlet2_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                            context=self.ws.subws)
        ws_portlets = ptltool.getPortlets(context=self.ws)
        ws_portlets_ids = [p.getId() for p in ws_portlets]
        self.assertEquals(ws_portlets_ids, [portlet1_id])

        subws_portlets = ptltool.getPortlets(context=self.ws.subws)
        subws_portlets_ids = [p.getId() for p in subws_portlets]
        self.assertEquals(subws_portlets_ids, [portlet1_id, portlet2_id])

    def test_copyPortletPerm(self):
        # create a portlet at root of portal
        ptltool = self.ptltool
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=self.ws)

        self.loginAsWsManager()
        
        # try to copy it 
        cont = ptltool.getPortletContainer(context=self.ws)
        orig = cont.getPortletById(portlet_id)
        copy = ptltool.movePortlet(orig, self.ws.subws, leave=1)
        ws_cont = ptltool.getPortletContainer(context=self.ws.subws)
        self.assertNotEqual(getattr(ws_cont, copy.getId(), None), None)
        self.assertNotEqual(getattr(cont, orig.getId(), None), None)

    def test_movePortletPerm(self):
        # create a portlet at root of portal
        ptltool = self.ptltool
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           context=self.portal)

        self.loginAsWsManager()
        
        # should not be able to move it 
        cont = ptltool.getPortletContainer(context=self.portal)
        orig = cont.getPortletById(portlet_id)
        self.failUnlessRaises(Unauthorized, ptltool.movePortlet, orig,
                              self.portal.workspaces, leave=0)

    def test_notify_event(self):
        ptltool = self.ptltool
        # XXX
        # To be sure the tests will be updated when the implementation will be
        # done
        self.assertEquals(ptltool.notify_event('fake_event', None, {}), None)

    def test_listPortletsInterestedInEvent(self):
        ptltool = self.ptltool

        # No portlets found already
        portlets = ptltool.listPortletsInterestedInEvent('fake_event', '', '')
        self.assertEquals(portlets, [])

        new_id = ptltool.createPortlet('Dummy Portlet')
        self.assertNotEqual(new_id, None)

        nportlet = ptltool.getPortletById(new_id)
        self.assertNotEqual(nportlet, None)

        res = nportlet.addEvent('fake_event')
        self.assertEquals(res, 0)

        # No way to add two time the same event
        res = nportlet.addEvent('fake_event')
        self.assertEquals(res, 1)

        events = nportlet.listEvents()
        self.assertEquals(events, (('fake_event', (), ()),) )

        # XXX to be implemented
        self.assertEquals(nportlet.sendEvent(event_id='fake_event', folder_path='', portal_type=''), 0)
        self.assertEquals(nportlet.sendEvent(event_id='fake_eventXXX', folder_path='', portal_type=''), 1)

    def test_FindCacheEntriesByUser(self):
        user = self.login_id
        ptltool = self.ptltool
        context = self.portal.workspaces
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet',
                                           slot='slot1',
                                           context=context)
        portlets_container = ptltool.getPortletContainer(context=context)
        portlet = portlets_container.getPortletById(portlet_id)
        self.assertEquals(ptltool.findCacheEntriesByUser(user), [])
        # clean the cache
        cache = ptltool.getPortletCache()
        cache.invalidate()
        # render the portlet
        portlet.render_cache()
        entries = ptltool.findCacheEntriesByUser(user)
        self.assertEquals(entries, 
                          [(portlet.getPhysicalPath(), 'user_%s' % user)])

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
        self.assertEquals(ptltool.findCacheEntriesByUser(user), [])
        # render the portlet
        portlet.render_cache()
        entries = ptltool.findCacheEntriesByUser(user)
        self.assertEquals(entries, [(portlet_path, 'user_%s' % user)])
        # invalidate the entry for another user
        ptltool.invalidateCacheEntriesByUser('dummy user')
        self.assert_(ptltool.findCacheEntriesByUser(user) != [])
        # invalidate the entry for this user
        ptltool.invalidateCacheEntriesByUser(user)
        self.assertEquals(ptltool.findCacheEntriesByUser(user), [])

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
        self.assertEquals(len(cache.getEntries()), 0)

    def test_renderIcon(self):
        ptltool = self.ptltool
        ttool = self.portal.portal_types
        # first rendering: storing the result in the cache
        res = ptltool.renderIcon('Dummy Portlet', '/cps/', 'dummy portlet')
        expected = '<img src="/cps/portlet_icon.png" width="16" height="16" alt="dummy portlet" />'
        self.assertEquals(res, expected)
        # fetching the entry from the cache
        res = ptltool.renderIcon('Dummy Portlet', '/cps/', 'dummy portlet')
        self.assertEquals(res, expected)
        # default parameters
        res = ptltool.renderIcon('Dummy Portlet')
        expected = '<img src="portlet_icon.png" width="16" height="16" alt="" />'
        self.assertEquals(res, expected)
        # unknown type
        res = ptltool.renderIcon('Unknown type for testing', '/', '')
        self.assertEquals(res, None)

    def test_portlet_eventIds_indexes(self):
        ptltool = self.ptltool
        cat = self.portal.portal_cpsportlets_catalog

        # Index is setup
        self.assert_('eventIds' in cat.indexes())

        # No portlet shows up
        self.assertEquals(
            len(ptltool.listAllPortlets(event_ids=['fake_event'])), 0)

        # Create a portlet interested about one (1) event
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet')
        portlet = ptltool.getPortletById(portlet_id)
        portlet.addEvent(event_ids=('fake_event',))
        self.assertEquals(['fake_event'], portlet.eventIds())

        # record within the catalog
        self.assert_(has_path(cat, "/portal/portal_cpsportlets/%s"%portlet_id))
        rid = cat._catalog.uids['/portal/portal_cpsportlets/%s'%portlet_id]
        self.assert_(['fake_event'] in cat._catalog.data[rid])

        # Test the queries
        self.assertEquals(len(ptltool.listAllPortlets()), 1)

        brains = cat(portal_type=ptltool.listPortletTypes())
        self.assertEquals(len(brains), 1)

        brains = cat(portal_type=ptltool.listPortletTypes(),
                     eventIds=['fake_event'])
        self.assertEquals(len(brains), 1)

        # Test queries from the portlets tool API
        self.assertEquals(
            len(ptltool.listAllPortlets(event_ids=['fake_event'])), 1)
        self.assertEquals(
            len(ptltool.listAllPortlets()), 1)
        self.assertEquals(len(ptltool.listAllPortlets(event_ids=['xxx'])), 0)

        # Add another event on the portlet.
        portlet.addEvent(event_ids=('fake_event2',))
        self.assertEquals(['fake_event', 'fake_event2'], portlet.eventIds())

        # Test the queries
        self.assertEquals(len(ptltool.listAllPortlets()), 1)

        brains = cat(portal_type=ptltool.listPortletTypes())
        self.assertEquals(len(brains), 1)

        brains = cat(portal_type=ptltool.listPortletTypes(),
                     eventIds=['fake_event'])
        self.assertEquals(len(brains), 1)

        brains = cat(portal_type=ptltool.listPortletTypes(),
                     eventIds=['fake_event2'])
        self.assertEquals(len(brains), 1)

        brains = cat(portal_type=ptltool.listPortletTypes(),
                     eventIds=['fake_event', 'fake_event2'])
        self.assertEquals(len(brains), 1)

        brains = cat(portal_type=ptltool.listPortletTypes(),
                     eventIds=['fake_event2', 'fake_event'])
        self.assertEquals(len(brains), 1)

        # Test queries from the portlets tool API
        self.assertEquals(
            len(ptltool.listAllPortlets(event_ids=['fake_event'])), 1)
        self.assertEquals(
            len(ptltool.listAllPortlets(event_ids=['fake_event2'])), 1)
        self.assertEquals(
            len(ptltool.listAllPortlets(
            event_ids=['fake_event', 'fake_event2'])), 1)
        self.assertEquals(
            len(ptltool.listAllPortlets()), 1)
        self.assertEquals(len(ptltool.listAllPortlets(event_ids=['xxx'])), 0)
        self.assertEquals(len(ptltool.listAllPortlets(event_ids=['fake_'])), 0)
        self.assertEquals(len(ptltool.listAllPortlets(event_ids=['_event'])), 0)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortletsTool))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
