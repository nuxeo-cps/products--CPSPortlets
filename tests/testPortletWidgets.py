import unittest
from Testing import ZopeTestCase

import os, sys
import re

from Acquisition import aq_base

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSSchemas.tests.testWidgets import FakeDataModel
from Products.CPSSchemas.tests.testWidgets import FakeDataStructure

from Products.CPSSchemas.widgets.select import CPSSelectWidget
from Products.CPSPortlets.widgets.generic import CPSDispatcherPortletWidget
from Products.CPSPortlets.CPSPortlet import CPSPortlet

class TestPortlets(CPSTestCase):
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
        len_before = len(ptltool.items())
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), len_before+1)
        portlet = ptltool[portlet_id]
        self.update_portlet_settings(portlet)
        portlet.render(context_obj=self.portal, portlet=portlet,
                       REQUEST=self.app.REQUEST)
        self.assert_(portlet.render_js() is not None)

# portal type list
tests = []
for ptype_id in ['Dummy Portlet',
                 'Search Portlet',
                 'Internal Links Portlet',
                 'Add Item Portlet',
                 'Actions Portlet',
                 'Content Portlet',
                 'Language Portlet',
                 'Image Portlet',
                 'Rotating Image Portlet',
                 'Navigation Portlet',
                 #'RSS Portlet', will fail if portal_rss is not present
                 #'Document Portlet', fails
                 'Text Portlet',
                 'Custom Portlet',
                ]:
    class TestOnePortlet(TestPortlet):

        ptype_id = ptype_id

        def update_portlet_settings(self, portlet):
            if self.ptype_id == 'Navigation Portlet':
                portlet.render_view_name = 'folder_contents'

    tests.append(TestOnePortlet)

pattern = '<div id="\w*?">%s</div>'

class TestCustomPortletWidget(TestPortlets):

    def test_without_rendering_method(self):
        ptype_id = 'Custom Portlet'
        ptltool = self.ptltool
        len_before = len(ptltool.items())
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), len_before + 1)
        portlet = ptltool[portlet_id]
        rendering = portlet.render(context_obj=self.portal, portlet=portlet)
        rendering = rendering.strip()
        self.assertNotEqual(re.match(pattern % 'Unknown render method <cite></cite>.',
                            rendering), None)

    def test_with_rendering_method_ok(self):

        # Callable
        def meth(**kw):
            return 'RENDERING'

        ptype_id = 'Custom Portlet'
        ptltool = self.ptltool
        len_before = len(ptltool.items())
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), len_before + 1)
        portlet = ptltool[portlet_id]
        setattr(self.portal, 'portlet_meth', meth)
        portlet.render_method = 'portlet_meth'
        self.assertEquals(getattr(portlet, portlet.render_method, None), meth)
        rendering = portlet.render(context_obj=self.portal, portlet=portlet)

        self.assertNotEqual(re.findall(pattern % meth(), rendering), None)

    def test_with_rendering_method_ko(self):

        # Not a callable
        meth = 'RENDERING'

        ptype_id = 'Custom Portlet'
        ptltool = self.ptltool
        len_before = len(ptltool.items())
        portlet_id = ptltool.createPortlet(ptype_id)
        self.assertEquals(len(ptltool.items()), len_before + 1)
        portlet = ptltool[portlet_id]
        setattr(self.portal, 'portlet_meth', meth)
        portlet.render_method = 'portlet_meth'
        self.assertEquals(getattr(portlet, portlet.render_method, None), meth)
        rendering = portlet.render(context_obj=self.portal, portlet=portlet)
        content = "<cite>portlet_meth</cite> is not a callable object."
        self.assertNotEqual(re.findall(pattern % content, rendering), None)

class TestDispatcherPortletWidget(TestPortlets):

    def afterSetUp(self):
        TestPortlets.afterSetUp(self)
        portal = self.portal

        # widgets
        portal._setObject('sel', CPSSelectWidget('sel'))
        portal._setObject('disp', CPSDispatcherPortletWidget('disp'))
        self.selector = portal.sel
        self.selector.manage_changeProperties(fields=('sel',))
        self.dispatcher = portal.disp

        # a render method
        def meth(mode='', datastructure=None, **kw):
            return mode + " Foo"

        portal.dispatcher_widget_foo = meth

        # a fake portlet
        class FakePortlet(CPSPortlet):
            portal_type = 'Dispatcher Portlet'

        portal._setObject('disp_portlet', FakePortlet('disp_portlet'))
        self.portlet = portal.disp_portlet

        dm = self.dm = FakeDataModel()
        dm.proxy = self.portlet
        self.ds = FakeDataStructure(dm)

    def test_dispatching_ok(self):
        self.dispatcher.manage_changeProperties(
            selector_widget='sel',
            render_method_prefix='dispatcher_widget_')
        self.dm['sel'] = 'foo'
        ds = self.ds
        self.selector.prepare(ds)
        self.dispatcher.prepare(ds)
        rendered = self.dispatcher.render('view', ds)
        self.assertEquals(rendered, "view Foo")

    def test_dispatching_wrong_selector(self):
        self.dispatcher.manage_changeProperties(
            selector_widget='wrong',
            render_method_prefix='dispatcher_widget_')
        self.dm['sel'] = 'foo'
        ds = self.ds
        self.selector.prepare(ds)
        self.dispatcher.prepare(ds)
        self.assertRaises(ValueError, self.dispatcher.render, 'view', ds)

    def test_dispatching_wrong_method(self):
        self.dispatcher.manage_changeProperties(
            selector_widget='sel',
            render_method_prefix='dispatcher_widget_')
        self.dm['sel'] = 'wrong'
        ds = self.ds
        self.selector.prepare(ds)
        self.dispatcher.prepare(ds)
        self.assertRaises(RuntimeError, self.dispatcher.render, 'view', ds)

def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    suite.addTest(unittest.makeSuite(TestCustomPortletWidget))
    suite.addTest(unittest.makeSuite(TestDispatcherPortletWidget))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

