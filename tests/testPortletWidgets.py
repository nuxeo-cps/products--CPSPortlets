import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Acquisition import aq_base

from Testing import ZopeTestCase

from Products.CPSDefault.tests import CPSDefaultTestCase

class TestPortlets(CPSDefaultTestCase.CPSDefaultTestCase):
    def afterSetUp(self):
        self.login('manager')
        self.portal.REQUEST.SESSION = {}
        self.ptltool = self.portal.portal_cpsportlets
        # Remove the default portlets installation
        if '.cps_portlets' in self.portal.objectIds():
            self.portal.manage_delObjects(['.cps_portlets'])

    def beforeTearDown(self):
        self.logout()

class TestPortlet(TestPortlets):
    ptype_id = None
    def testPortlet(self):
        ptype_id = self.ptype_id
        ptltool = self.ptltool
        self.assertEquals(len(ptltool.items()), 0)
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), 1)
        portlet = ptltool[portlet_id]
        portlet.render(context_obj=self.portal, portlet=portlet)
        self.assert_(portlet.render_js() is not None)

# portal type list
tests = []
for ptype_id in ['Dummy Portlet',
                 'Search Portlet',
                 'Internal Links Portlet',
                 'Add Item Portlet',
                 'Breadcrumbs Portlet',
                 'Actions Portlet',
                 'Content Portlet',
                 'Language Portlet',
                 'Image Portlet',
                 'Rotating Image Portlet',
                 'Navigation Portlet',
                 'RSS Portlet',
                 #'Document Portlet', fails
                 'Text Portlet',
                 'Custom Portlet',
                ]:
    class TestOnePortlet(TestPortlet):
        ptype_id = ptype_id
    tests.append(TestOnePortlet)

class TestCustomPortletWidget(TestPortlets):

    def test_without_rendering_method(self):
        ptype_id = 'Custom Portlet'
        ptltool = self.ptltool
        self.assertEquals(len(ptltool.items()), 0)
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), 1)
        portlet = ptltool[portlet_id]
        rendering = portlet.render(context_obj=self.portal, portlet=portlet)
        self.assertEquals('Unknown render method <cite></cite>.',
                         rendering)

    def test_with_rendering_method_ok(self):

        # Callable
        def meth(**kw):
            return 'RENDERING'

        ptype_id = 'Custom Portlet'
        ptltool = self.ptltool
        self.assertEquals(len(ptltool.items()), 0)
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), 1)
        portlet = ptltool[portlet_id]
        setattr(self.portal, 'portlet_meth', meth)
        portlet.render_method = 'portlet_meth'
        self.assertEquals(getattr(portlet, portlet.render_method, None), meth)
        rendering = portlet.render(context_obj=self.portal, portlet=portlet)
        self.assertEquals(meth(), rendering)

    def test_with_rendering_method_ko(self):

        # Not a callable
        meth = 'RENDERING'

        ptype_id = 'Custom Portlet'
        ptltool = self.ptltool
        self.assertEquals(len(ptltool.items()), 0)
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), 1)
        portlet = ptltool[portlet_id]
        setattr(self.portal, 'portlet_meth', meth)
        portlet.render_method = 'portlet_meth'
        self.assertEquals(getattr(portlet, portlet.render_method, None), meth)
        rendering = portlet.render(context_obj=self.portal, portlet=portlet)
        self.assertEquals(
            rendering,
            "<cite>portlet_meth</cite> is not a callable object.")

def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    suite.addTest(unittest.makeSuite(TestCustomPortletWidget))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

