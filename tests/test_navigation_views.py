# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#   Georges Racinet <georges@racinet.fr>
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

import unittest
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

from Products.CPSPortlets.browser.navigation import HierarchicalSimpleView
from Products.CPSPortlets.browser.navigation import lstartswith
from Products.CPSPortlets.browser.navigation import tree_to_rpaths

def simplify_tree_list(tlist):
    """Convert a real life tree list to one more readable/debuggable."""
    for node in tlist:
        for k in node.keys():
            if k not in ['rpath', 'children']:
                del node[k]
        children = node.get('children')
        if children:
            simplify_tree_list(children)

def rpaths_to_items(*rpaths):
    return [dict(rpath=p) for p in rpaths]

class FakePortal:

    def absolute_url_path(self):
        return '/deep/inside'

PORTAL = FakePortal()

class FakeUrlTool:

    def getPortalObject(self):
        return PORTAL

PORTAL.portal_url = FakeUrlTool()

class HierarchicalSimpleViewTest(unittest.TestCase):

    def setUp(self):
        # we'll feed the needed context/request if needed
        self.view = HierarchicalSimpleView(PORTAL, None)

    def assertConsistency(self, children, node=None):
        """Check that children are always actually children."""
        if node is not None:
            rpathl = node['rpath'].split('/')
        for child in children:
            if node is not None:
                crpathl = child['rpath'].split('/')
                if not lstartswith(crpathl, rpathl):
                    self.fail('%s not under %s' % (child['rpath'],
                                                   node['rpath']))
            self.assertConsistency(child.get('children'), node=child)

    def test_listToTree(self):
        self.view.here_rpath = 'a/x/z'
        tree = self.view.listToTree(rpaths_to_items(
                'a', 'a/b', 'a/b/b1', 'a/x', 'a/x/a', 'a/x/z', 'a/y'))

        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a', children=[
                        dict(rpath='a/b'),
                        dict(rpath='a/x', children=[
                                dict(rpath='a/x/a'),
                                dict(rpath='a/x/z')]),
                        dict(rpath='a/y')]
                     )])

    def test_listToTree_deeper(self):
        # Test that a first-level visible folder inside a non-visible one
        # that's not in the currently unfolder path gets nevertheless displayed
        self.view.here_rpath = 'a/x/z'

        tree = self.view.listToTree(rpaths_to_items(
                'a', 'a/b/b1', 'a/x', 'a/x/a', 'a/x/z', 'a/y'))
        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a', children=[
                        dict(rpath='a/b/b1'),
                        dict(rpath='a/x', children=[
                                dict(rpath='a/x/a'),
                                dict(rpath='a/x/z')]),
                        dict(rpath='a/y')]
                     )])

        # border case
        tree = self.view.listToTree(rpaths_to_items(
                'a/b/b1', 'a/x', 'a/x/a', 'a/x/z', 'a/y'))
        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a/b/b1'),
                dict(rpath='a/x', children=[
                        dict(rpath='a/x/a'),
                        dict(rpath='a/x/z')]),
                dict(rpath='a/y')])


        # another border case : climbing 2 steps up
        tree = self.view.listToTree(rpaths_to_items(
                'a/b', 'a/b/b1', 'd', 'a/x', 'a/x/a', 'a/x/z', 'c'))
        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a/b'),
                dict(rpath='d'),
                dict(rpath='a/x', children=[
                        dict(rpath='a/x/a'),
                        dict(rpath='a/x/z')]),
                dict(rpath='c')])

    def test_listToTree_buggy1(self):
        tlist = [
            {'rpath': 'a/b/c'},
            {'rpath': 'a/b/c/ca'},
            {'rpath': 'a/b/c/ca/ca1'},
            {'rpath': 'a/b/e'},
            {'rpath': 'a/b/co'},
            ]

        self.view.here_rpath = 'a/b/c/ca'
        tree = self.view.listToTree(tlist)
        rpaths = tree_to_rpaths(tree)
        self.assertConsistency(tree) # before fix, gave infinite loop
        self.assertEquals(rpaths, [
                {'rpath': 'a/b/c',
                 'children': [
                        {'rpath': 'a/b/c/ca',
                         'children': [{'rpath': 'a/b/c/ca/ca1'}],
                         }],
                 },
                {'rpath': 'a/b/e'},
                {'rpath': 'a/b/co'}
                ])

class HierarchicalSimpleViewIntegrationTest(CPSTestCase):

    def afterSetUp(self):
        # we'll feed the needed context/request if needed
        self.request = self.app.REQUEST
        view = self.view = HierarchicalSimpleView(self.portal, self.request)
        view.datamodel = dict(start_depth=0, end_depth=0,
                              root_uids=['sections'])
        self.login('manager')
        self.portal.portal_workflow.invokeFactoryFor(
            self.portal.sections, 'Section', 'subs')

    def test_getTree(self):
        view = self.view
        view.here_rpath = 'sections'
        tree = view.getTree()
        self.assertEquals(tree[0]['rpath'], 'sections')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(HierarchicalSimpleViewTest),
        unittest.makeSuite(HierarchicalSimpleViewIntegrationTest),
        ))
