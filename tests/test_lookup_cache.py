 # (C) Copyright 2010-2011 CPS-CMS Community <http://cps-cms.org/>
 # Authors:
 #     G. Racinet <gracinet@cps-cms.org>
 #
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 2 of the License, or
 # (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This test case referts to the internal Lookup Cache API.

It may therefore be irrelevant for refactors changing drastically this API.
In that case, ignore it first, then adapt or destroy it.
"""

import unittest
from Testing import ZopeTestCase

from DateTime import DateTime
from Products.CPSUtil.conflictresolvers import IncreasingDateTime
from Products.CMFCore.utils import getToolByName
from Products.CPSDefault.tests.CPSDefaultTestCase import CPSDefaultTestCase
from Products.CPSPortlets.PortletsTool import LOOKUP_CACHE_DATE_GLOBAL_ID

class TestLookupCache(CPSDefaultTestCase):

    def afterSetUp(self):
        self.login_id = 'manager'
        self.login(self.login_id)
        portal = self.portal

        self.tool = tool = getToolByName(portal, 'portal_cpsportlets')

        # create a portlet with slot 'test_slot' in sections
        self.ptl_context = context = portal.sections
        self.portlet_id = portlet_id = tool.createPortlet(
            ptype_id='Dummy Portlet', context=context)
        container = tool.getPortletContainer(context=context)
        portlet = self.portlet = container.getPortletById(portlet_id)
        self.tool.insertPortlet(portlet=portlet, slot='test_slot')
        self.portlet = portlet

    def test_setup(self):
        portlet = self.portlet
        self.failIf(portlet is None)
        self.assertEquals(portlet.portal_type, 'Dummy Portlet')
        self.assertEquals(
            self.tool.getPortlets(slot='test_slot', context=self.ptl_context),
            [portlet])

    def do_test_invalidation(self, with_prior_invalidation=False):
        tool = self.tool
        context = self.ptl_context

        # first, invalidate and fill the lookup cache
        if with_prior_invalidation:
            tool.lookupCacheInvalidate()
        tool.getPortlets(slot='test_slot', context=context)

        cache_args = ['test_slot', ('sections',), True, True]
        cached = tool._lookupCacheGet(*cache_args)
        self.failIf(cached is None)
        self.assertEquals(len(cached), 1)

        # Another ZEO client deletes the portlet, so we don't get events
        # but it sets the global date
        tool.ignore_events = True
        tool.deletePortlet(self.portlet_id, context=context)
        tool.ignore_events = False

        future = DateTime() + 3.0/86400 # +3 secs to be sure it's later
        tool._getGlobalLookupCacheDate().set(future)
        # Invalidation is propagated: the cache returns nothing for these keys
        cached = tool._lookupCacheGet(*cache_args)
        self.assertEquals(cached, None)

    def test_upgrade_2482(self):
        # test auto upgrade to conflictresolver timestamp
        tool = self.tool
        setattr(tool, LOOKUP_CACHE_DATE_GLOBAL_ID, DateTime('2011/10/19'))
        tool.lookupCacheInvalidate() # used to break already
        self.assertTrue(isinstance(getattr(tool, LOOKUP_CACHE_DATE_GLOBAL_ID),
                                   IncreasingDateTime))

    def test_invalidation(self):
        self.do_test_invalidation(with_prior_invalidation=False)

    def test_invalidation2(self):
        self.do_test_invalidation(with_prior_invalidation=True)

    def test_ghosts(self):
        # Unless there's a bug, ghosts can still happen if machine clocks
        # are out of sync
        tool = self.tool
        context = self.ptl_context

        # first, invalidate and fill the lookup cache
        tool._invalidatePortletLookupCache()
        tool.getPortlets(slot='test_slot', context=context)
        # let's turn off cache invalidation and destroy the portlet
        tool.ignore_events = True
        tool.deletePortlet(self.portlet_id, context=context)
        tool.ignore_events = False

        # this used to break
        tool.getPortlets(slot='test_slot', context=context)

    def beforeTearDown(self):
        self.logout()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLookupCache))
    return suite
