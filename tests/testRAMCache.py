import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase

from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI

from Products.CPSDefault.tests import CPSDefaultTestCase

class TestRAMCache(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login_id = 'root'
        self.login(self.login_id)
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST['AUTHENTICATED_USER'] = self.login_id

        # create a global portlet
        ptltool = self.portal.portal_cpsportlets
        portlet_id = ptltool.createPortlet(ptype_id='Dummy Portlet')
        self.portlet = ptltool[portlet_id]

        # Cross-platform test FTI derived from CMFCore.PortalFolder
        types_tool = self.portal.portal_types
        types_tool._setObject('CPSPortlets Test Folder',
                              FTI(id='CPSPortlets Test Folder',
                                  title='',
                                  meta_type='CPSPortlets Test Folder',
                                  product='CMFCore',
                                  factory='manage_addPortalFolder',
                                  filter_content_types=0,
                                  )
                             )
        self.portal.invokeFactory('CPSPortlets Test Folder',
                                  'cpsportlets_test_folder')
        self.working_context = self.portal.cpsportlets_test_folder

        # default context
        self.default_kw = {'context_obj': self.working_context,
                          }

    def beforeTearDown(self):
        self.logout()

    def test_getCacheIndex_portal_type(self):
        portlet = self.portlet
        portlet._setCacheParams(['portal_type'])
        kw = self.default_kw
        cache_index = portlet.getCacheIndex(**kw)
        expected_index = ('portal_type_CPSPortlets Test Folder',)
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_object_path(self):
        portlet = self.portlet
        portlet._setCacheParams(['object:path'])
        kw = self.default_kw
        cache_index = portlet.getCacheIndex(**kw)
        expected_index = ('object__path:/portal/cpsportlets_test_folder',)
        self.assert_(cache_index == expected_index)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRAMCache))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
