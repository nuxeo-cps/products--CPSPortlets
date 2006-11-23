# $Id$

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

        self.ptltool = self.portal.portal_cpsportlets

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
        self.ptltool.updateCacheParameters({'Dummy Portlet': []})
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ()
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_no_cache(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['no-cache']})
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = None
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_no_cache_with_fields(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters(
            {'Dummy Portlet': ['no-cache:(dummy)']})
        # no cache since 'dummy' has a true value
        portlet.dummy = 'do not cache'
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = None
        self.assertEquals(cache_index, expected_index)
        # cache since 'dummy' has a false value.
        portlet.dummy = ''
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ()
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_request(self):
        portlet = self.portlet
        kw = self.default_kw
        # one option
        self.portal.REQUEST['DUMMY'] = 'dummy'
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['request:DUMMY']})
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('request__DUMMY:dummy',)
        self.assertEquals(cache_index, expected_index)
        # several options
        self.portal.REQUEST['DUMMY1'] = 'dummy1'
        self.portal.REQUEST['DUMMY2'] = 'dummy2'
        self.ptltool.updateCacheParameters({'Dummy Portlet':
            ['request:DUMMY1,DUMMY2']})
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('request__DUMMY1:dummy1_DUMMY2:dummy2',)
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_user(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['user']})
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('user_%s' % self.login_id,)
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_protocol(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['protocol']})
        kw = self.default_kw
        #
        self.portal.REQUEST['SERVER_URL'] = 'http://some.site.org/'
        expected_index = ('protocol_http',)
        cache_index, data = portlet.getCacheIndex(**kw)
        self.assertEquals(cache_index, expected_index)
        #
        self.portal.REQUEST['SERVER_URL'] = 'https://some.secure.site.org/'
        expected_index = ('protocol_https',)
        cache_index, data = portlet.getCacheIndex(**kw)
        self.assertEquals(cache_index, expected_index)
        #
        self.portal.REQUEST['SERVER_URL'] = ''
        expected_index = ()
        cache_index, data = portlet.getCacheIndex(**kw)
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_current_lang(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['current_lang']})
        kw = self.default_kw
        self.portal.REQUEST['cpsskins_language'] = 'en'
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('current_lang_en',)
        self.assertEquals(cache_index, expected_index)
        # dummy language
        self.portal.REQUEST['cpsskins_language'] = 'dummy'
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('current_lang_dummy',)
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_portal_type(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['portal_type']})
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('portal_type_CPSPortlets Test Folder',)
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_object_path(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['object:path']})
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('object__path:/portal/cpsportlets_test_folder',)
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_object_published_path(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet':
            ['object:published_path']})
        kw = self.default_kw
        self.portal.REQUEST['PATH_TRANSLATED'] = '/dummy_path'
        cache_index, data = portlet.getCacheIndex(**kw)
        expected_index = ('object__published_path:/dummy_path',)
        self.assertEquals(cache_index, expected_index)

    def test_getCacheIndex_random(self):
        portlet = self.portlet
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['random:5']})
        kw = self.default_kw
        cache_index, data = portlet.getCacheIndex(**kw)
        randint = data['random_int']
        expected_index = ('random_%s' % str(randint),)
        self.assertEquals(cache_index, expected_index)
        self.assert_(randint < 5)

    def test_getCustomCacheParams(self):
        ptltool = self.portal.portal_cpsportlets
        portlet_id = ptltool.createPortlet(ptype_id='Custom Portlet')
        portlet = ptltool[portlet_id]
        custom_params = ['dummy1', 'dummy2']
        portlet.edit(custom_cache_params=custom_params)
        params = portlet.getCustomCacheParams()
        self.assertEquals(params, custom_params)

    def test_setCustomCacheParams(self):
        ptltool = self.portal.portal_cpsportlets
        portlet_id = ptltool.createPortlet(ptype_id='Custom Portlet')
        portlet = ptltool[portlet_id]
        custom_params = ['dummy1', 'dummy2']
        portlet.setCustomCacheParams(params=custom_params)
        self.assertEquals(portlet.custom_cache_params, custom_params)

    def test_setCacheTimeout(self):
        portlet = self.portlet
        # unique timeout parameter
        self.ptltool.updateCacheParameters({'Dummy Portlet': ['timeout:10']})
        portlet.resetCacheTimeout()
        self.assertEquals(portlet.cache_timeout, 10)
        # resolve ambiguity
        self.ptltool.updateCacheParameters({'Dummy Portlet':
            ['timeout:123', 'timeout:20']})
        portlet.resetCacheTimeout()
        self.assertEquals(portlet.cache_timeout, 20)
        # several cache parameters
        self.ptltool.updateCacheParameters({'Dummy Portlet':
            ['baseurl', 'timeout:30', 'url']})
        portlet.resetCacheTimeout()
        self.assertEquals(portlet.cache_timeout, 30)
        # incorrect timeout value
        self.ptltool.updateCacheParameters({'Dummy Portlet':
            ['timeout:abc']})
        portlet.resetCacheTimeout()
        self.assertEquals(portlet.cache_timeout, 30)
        # incorrect timeout value
        self.ptltool.updateCacheParameters({'Dummy Portlet':
            ['timeout:-10']})
        portlet.resetCacheTimeout()
        self.assertEquals(portlet.cache_timeout, 30)
        # no timeout parameters (means timeout = 0)
        self.ptltool.updateCacheParameters({'Dummy Portlet':
            ['baseurl', 'url']})
        portlet.resetCacheTimeout()
        self.assertEquals(portlet.cache_timeout, 30)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRAMCache))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
