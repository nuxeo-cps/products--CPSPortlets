import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase

from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI

from Products.CPSDefault.tests import CPSDefaultTestCase

class TestRAMCache(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login_id = 'manager'
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

    def test_getCacheIndex_no_parameter(self):
        portlet = self.portlet
        portlet._setCacheParams([])
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ()
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_no_cache(self):
        portlet = self.portlet
        portlet._setCacheParams(['no-cache'])
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = None
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_request(self):
        portlet = self.portlet
        kw = self.default_kw
        # one option
        self.portal.REQUEST['DUMMY'] = 'dummy'
        portlet._setCacheParams(['request:DUMMY'])
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('request__DUMMY:dummy',)
        self.assert_(cache_index == expected_index)
        # several options
        self.portal.REQUEST['DUMMY1'] = 'dummy1'
        self.portal.REQUEST['DUMMY2'] = 'dummy2'
        portlet._setCacheParams(['request:DUMMY1,DUMMY2'])
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('request__DUMMY1:dummy1_DUMMY2:dummy2',)
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_user(self):
        portlet = self.portlet
        portlet._setCacheParams(['user'])
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('user_%s' % self.login_id,)
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_current_lang(self):
        portlet = self.portlet
        portlet._setCacheParams(['current_lang'])
        kw = self.default_kw
        self.portal.REQUEST['cpsskins_language'] = 'en'
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('current_lang_en',)
        self.assert_(cache_index == expected_index)
        # dummy language
        self.portal.REQUEST['cpsskins_language'] = 'dummy'
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('current_lang_dummy',)
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_portal_type(self):
        portlet = self.portlet
        portlet._setCacheParams(['portal_type'])
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('portal_type_CPSPortlets Test Folder',)
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_object_path(self):
        portlet = self.portlet
        portlet._setCacheParams(['object:path'])
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('object__path:/portal/cpsportlets_test_folder',)
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_object_published_path(self):
        portlet = self.portlet
        portlet._setCacheParams(['object:published_path'])
        kw = self.default_kw
        self.portal.REQUEST['PATH_TRANSLATED'] = '/dummy_path'
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('object__published_path:/dummy_path',)
        self.assert_(cache_index == expected_index)

    def test_getCacheIndex_random(self):
        portlet = self.portlet
        portlet._setCacheParams(['random:5'])
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        randint = data['random_int']
        expected_index = ('random_%s' % str(randint),)
        self.assert_(cache_index == expected_index)
        self.assert_(randint < 5)

    def test_getCustomCacheParams(self):
        ptltool = self.portal.portal_cpsportlets
        portlet_id = ptltool.createPortlet(ptype_id='Custom Portlet')
        portlet = ptltool[portlet_id]
        custom_params = ['dummy1', 'dummy2']
        portlet.edit(custom_cache_params=custom_params)
        params = portlet.getCustomCacheParams()
        self.assert_(params == custom_params)

    def test_setCustomCacheParams(self):
        ptltool = self.portal.portal_cpsportlets
        portlet_id = ptltool.createPortlet(ptype_id='Custom Portlet')
        portlet = ptltool[portlet_id]
        custom_params = ['dummy1', 'dummy2']
        portlet.setCustomCacheParams(params=custom_params)
        self.assert_(portlet.custom_cache_params == custom_params)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRAMCache))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
