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

    def beforeTearDown(self):
        self.logout()

class TestPortlet(TestPortlets):
    ptype_id = None
    def testPortlet(self):
        ptype_id = self.ptype_id
        ptltool = self.ptltool
        self.assert_(len(ptltool.items()) == 0)
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assert_(len(ptltool.items()) == 1)
        portlet = ptltool[portlet_id]
        portlet.render(context_obj=self.portal)
        self.assert_(portlet.render_js() is not None)

# portal type list
tests=[]
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

def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

