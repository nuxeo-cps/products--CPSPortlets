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

from Products.CMFCore.utils import getToolByName
from Products.CPSPortlets.browser.navigation import HierarchicalSimpleView
from Products.CPSPortlets.browser.navigation import JsonNavigation
from Products.CPSPortlets.browser.navigation import DynaTreeNavigation
from Products.CPSPortlets.browser.navigation import lstartswith
from Products.CPSPortlets.browser.navigation import tree_to_rpaths
from Products.CPSPortlets.CPSPortlet import REQUEST_TRAVERSAL_KEY

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

    def test_listToTree_forest(self):
        # can produce actual forests, here with two trees
        tree = self.view.listToTree(rpaths_to_items(
                'a', 'a/b', 'a/b/b1', 'a/x', 'a/x/a', 'a/x/z', 'a/y',
                'tree2'), unfold_to='a/x/z')

        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a', children=[
                        dict(rpath='a/b'),
                        dict(rpath='a/x', children=[
                                dict(rpath='a/x/a'),
                                dict(rpath='a/x/z')]),
                        dict(rpath='a/y')]
                     ),
                dict(rpath='tree2')])

    def test_listToTree_unfold_level1(self):
        tree = self.view.listToTree(rpaths_to_items(
                'a', 'a/b', 'a/b/b1',
                'a/x', 'a/x/a', 'a/x/z', 'a/x/z/t',
                'a/y',), unfold_to='a', unfold_level=1)

        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a', children=[
                        dict(rpath='a/b'),
                        dict(rpath='a/x'),
                        dict(rpath='a/y')]
                     ),])

    def test_listToTree_unfold_level2(self):
        tree = self.view.listToTree(rpaths_to_items(
                'a', 'a/b', 'a/b/b1',
                'a/x', 'a/x/a', 'a/x/z', 'a/x/z/t',
                'a/y'), unfold_to='a', unfold_level=2)

        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a', children=[
                        dict(rpath='a/b', children=[
                                dict(rpath='a/b/b1')]),
                        dict(rpath='a/x', children=[
                                dict(rpath='a/x/a'),
                                dict(rpath='a/x/z')]),
                        dict(rpath='a/y')]
                     ),
                ])

    def test_under(self):
        forest = [dict(rpath='a', children=[
                    dict(rpath='a/b', children=[
                            dict(rpath='a/b/b1')]),
                    dict(rpath='a/x', children=[
                            dict(rpath='a/x/a'),
                            dict(rpath='a/x/z')]),
                        dict(rpath='a/y')]
                       ),
                  ]
        self.assertEquals(self.view.under(forest, 'a/x'),
                    dict(rpath='a/x', children=[
                            dict(rpath='a/x/a'),
                            dict(rpath='a/x/z')]))

    def test_listToTree_unfold_level3(self):
        tree = self.view.listToTree(rpaths_to_items(
                'a', 'a/b', 'a/b/b1',
                'a/x', 'a/x/a', 'a/x/z', 'a/x/z/t',
                'a/y',), unfold_to='a', unfold_level=3)

        self.assertConsistency(tree)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a', children=[
                        dict(rpath='a/b', children=[
                                dict(rpath='a/b/b1')]),
                        dict(rpath='a/x', children=[
                                dict(rpath='a/x/a'),
                                dict(rpath='a/x/z', children=[
                                        dict(rpath='a/x/z/t')
                                        ])
                                ]),
                        dict(rpath='a/y')]
                     ),
                ])

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

class CommonFixture:

    TEST_USER = 'nav_view_user'

    def setRequestContextObj(self, rpath):
        self.request[REQUEST_TRAVERSAL_KEY] = rpath.split('/')

    def rebuildTree(self):
        # could get slow
        getToolByName(self.portal, 'portal_trees')['workspaces'].rebuild()

    def createStructure(self):
        self.login('manager')
        user = self.TEST_USER

        aclu = getToolByName(self.portal, 'acl_users')
        aclu._doAddUser(user, '', ('Member',), ())
        self.assertFalse(aclu.getUser(user) is None)

        self.wftool = wftool = getToolByName(self.portal, 'portal_workflow')
        self.pmtool = pmtool = getToolByName(self.portal, 'portal_membership')

        ws = self.portal.workspaces
        pmtool.setLocalRoles(obj=ws, member_ids=[user],
                             member_role='WorkspaceReader')

        wftool.invokeFactoryFor(ws, 'Workspace', 'subw')
        subw = ws.subw

        wftool.invokeFactoryFor(subw, 'Workspace', 'subsubw')
        subsubw = subw.subsubw
        pmtool.blockLocalRoles(subsubw)

        wftool.invokeFactoryFor(subw, 'File', 'doc')
        wftool.invokeFactoryFor(subsubw, 'FAQ', 'faq')
        self.rebuildTree()

    def createPortlet(self):
        self.login('manager')
        ptltool = getToolByName(self.portal, 'portal_cpsportlets')
        ptl_id = ptltool.createPortlet('Navigation Portlet',
                                       root_uids=('workspaces',), show_docs=1)
        self.portlet = ptltool[ptl_id]


class HierarchicalSimpleViewIntegrationTest(CommonFixture, CPSTestCase):

    def afterSetUp(self):
        # we'll feed the needed context/request if needed
        self.request = self.app.REQUEST
        view = self.view = HierarchicalSimpleView(self.portal, self.request)
        view.datamodel = dict(start_depth=0, end_depth=0,
                              root_uids=['workspaces'])
        self.createStructure()

    def test_getTree(self):
        view = self.view
        view.here_rpath = 'workspaces'
        tree = view.getTree()
        self.assertEquals(tree[0]['rpath'], 'workspaces')

    def test_getTree_end_depth(self):
        # see #2534
        view = self.view
        view.datamodel['end_depth'] = 1
        view.here_rpath = 'workspaces'
        tree = view.getTree()
        self.assertEquals(tree[0]['rpath'], 'workspaces')

    def test_getTree_hidden_folder(self):
        view = self.view
        view.here_rpath = 'workspaces/subw'
        view.datamodel['display_hidden_folders'] = False
        self.wftool.invokeFactoryFor(self.portal.workspaces.subw, 'Workspace',
                                     'hidden-ws', hidden_folder=True)
        self.rebuildTree()

        tree = view.getTree()
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces', children=[
                        dict(rpath='workspaces/subw', children=[
                                dict(rpath='workspaces/subw/subsubw'),
                                ])
                        ])
                ])

    def test_getTree_hidden_folder_True(self):
        view = self.view
        view.here_rpath = 'workspaces/subw'
        view.datamodel['display_hidden_folders'] = True
        self.wftool.invokeFactoryFor(self.portal.workspaces.subw, 'Workspace',
                                     'hidden-ws', hidden_folder=True)
        self.rebuildTree()

        tree = view.getTree()
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces', children=[
                        dict(rpath='workspaces/subw', children=[
                                dict(rpath='workspaces/subw/subsubw'),
                                dict(rpath='workspaces/subw/hidden-ws'),
                                ])
                        ])
                ])

    def test_getTreeWithDocs(self):
        view = self.view
        view.datamodel['show_docs'] = True
        view.here_rpath = 'workspaces/subw'
        tree = view.getTree()
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces', children=[
                        dict(rpath='workspaces/subw', children=[
                                dict(rpath='workspaces/subw/subsubw'),
                                dict(rpath='workspaces/subw/doc'),
                                ])
                        ])
                ])


    def test_getTreeWithDocs_terminal(self):
        # we check that docs are not added to terminal nodes,
        # ie those that are at maximal depth of unfolding under here_rpath
        # test is actually about the second terminal node under subw :
        # it should not display its document
        wftool = getToolByName(self.portal, 'portal_workflow')
        subw = self.portal.workspaces.subw
        wftool.invokeFactoryFor(subw, 'Workspace', 'subsubw2')
        wftool.invokeFactoryFor(subw.subsubw2, 'File', 'doc2')
        self.portal.portal_trees['workspaces'].rebuild() # could get slow

        view = self.view
        view.datamodel['show_docs'] = True
        view.here_rpath = 'workspaces/subw'
        tree = view.getTree()
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces', children=[
                        dict(rpath='workspaces/subw', children=[
                                dict(rpath='workspaces/subw/subsubw'),
                                dict(rpath='workspaces/subw/subsubw2'),
                                dict(rpath='workspaces/subw/doc'),
                                ])
                        ])
                ])

    def test_getTreeWithDocs2(self):
        view = self.view
        view.datamodel['show_docs'] = True
        view.here_rpath = 'workspaces/subw/subsubw'
        tree = view.getTree()
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces', children=[
                        dict(rpath='workspaces/subw', children=[
                            dict(rpath='workspaces/subw/subsubw', children=[
                                dict(rpath='workspaces/subw/subsubw/faq')])
                            ])
                        ])
                ])

    def test_getTreeWithDocs_subw_blocked(self):
        # we used to have an error in addDocs because of the jump in
        # rpaths if an intermediate node is missing (permissions)
        user = self.TEST_USER
        # we really need to add one level and block at subsubw to reproduce
        # the difficulty. At subw, the recursion would start too deep in the
        # tree already.
        subsubw = self.portal.workspaces.subw.subsubw
        self.wftool.invokeFactoryFor(subsubw, 'Workspace', 'sub3w')
        sub3w = subsubw.sub3w
        self.pmtool.setLocalRoles(obj=sub3w, member_ids=[user],
                                  member_role='WorkspaceReader')
        self.rebuildTree()

        self.login(user)
        view = self.view
        view.datamodel['show_docs'] = True
        view.here_rpath = 'workspaces/subw'

        tree = view.getTree()
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces', children=[
                        dict(rpath='workspaces/subw', children=[
                                dict(rpath='workspaces/subw/subsubw/sub3w'),
                                dict(rpath='workspaces/subw/doc'),
                                ])
                            ])
                        ])

    def test_nodeSubTree(self):
        view = self.view
        view.here_rpath = 'workspaces'
        tree = view.nodeSubTree(inclusive=True)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces', children=[
                        dict(rpath='workspaces/subw')])
                ])

        tree = view.nodeSubTree(inclusive=False)
        self.assertEquals(tree[0]['rpath'], 'workspaces/subw')
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces/subw')])

    def test_nodeSubTreeFromDeeper(self):
        view = self.view
        view.here_rpath = 'workspaces/subw'
        tree = view.nodeSubTree(inclusive=True)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces/subw', children=[
                        dict(rpath='workspaces/subw/subsubw')])
                ])

        tree = view.nodeSubTree(inclusive=False)
        self.assertEquals(tree_to_rpaths(tree),
                          [dict(rpath='workspaces/subw/subsubw')])

    def test_nodeSubTreeWithDocsEmpty(self):
        # in this case we must not get a LookupError
        view = self.view
        view.datamodel['show_docs'] = True
        view.here_rpath = 'workspaces/khhhuhu'
        tree = view.nodeSubTree(inclusive=False)
        self.assertEquals(tree, [])

    def test_nodeSubTreeLevel2(self):
        view = self.view
        view.datamodel['subtree_depth'] = 2
        view.here_rpath = 'workspaces'
        tree = view.nodeSubTree(inclusive=False)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces/subw', children=[
                        dict(rpath='workspaces/subw/subsubw')])
                ])

    def test_nodeSubTreeWithDocs(self):
        view = self.view
        view.datamodel['subtree_depth'] = 2
        view.here_rpath = 'workspaces'
        tree = view.nodeSubTree(inclusive=False)
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='workspaces/subw', children=[
                        dict(rpath='workspaces/subw/subsubw')])
                ])

def forest_extract_method(view):
    """Extractor to test JsonNavigation base class, similar to tree_to_rpaths.
    """
    def extract(forest):
        res = []
        for tree in forest:
            node = dict(rpath=tree['rpath'])
            children = tree.get('children')
            if children:
                node['children'] = view.extract(tree['children'])
            res.append(node)
        return res
    return extract

class JsonNavigationIntegrationTest(CommonFixture, CPSTestCase):

    def afterSetUp(self):
        # we'll feed the needed context/request if needed
        self.request = self.app.REQUEST
        self.createPortlet()

        view = self.view = JsonNavigation(self.portlet, self.request)
        view.extract = forest_extract_method(view)
        self.createStructure()

    def setRequestContextObj(self, rpath):
        self.request[REQUEST_TRAVERSAL_KEY] = rpath.split('/')

    def testNodeUnfoldNoLevel(self):
        # subtree_depth=0 means to unfold to the end
        self.setRequestContextObj('workspaces/subw')
        self.portlet.edit(subtree_depth=0)
        self.assertEquals(self.portlet.getDataModel()['subtree_depth'], 0)
        self.assertEquals(self.view.nodeUnfold(),
                          u'[{"rpath": "workspaces/subw/subsubw", '
                          '"children": '
                          '[{"rpath": "workspaces/subw/subsubw/faq"}]}, '
                          '{"rpath": "workspaces/subw/doc"}]')

    def testNodeUnfoldLevel1(self):
        self.setRequestContextObj('workspaces/subw')
        self.portlet.edit(subtree_depth=1)
        self.assertEquals(self.portlet.getDataModel()['subtree_depth'], 1)
        self.assertEquals(self.view.nodeUnfold(),
                          u'[{"rpath": "workspaces/subw/subsubw"}, '
                          '{"rpath": "workspaces/subw/doc"}]')

class DynaTreeNavigationIntegrationTest(CommonFixture, CPSTestCase):

    def afterSetUp(self):
        # we'll feed the needed context/request if needed
        self.request = self.app.REQUEST
        self.createPortlet()

        view = self.view = DynaTreeNavigation(self.portlet, self.request)
        self.createStructure()

    def testNodeUnfold(self):
        self.setRequestContextObj('workspaces/subw')
        self.portlet.edit(subtree_depth=0)
        self.assertEquals(self.portlet.getDataModel()['subtree_depth'], 0)
        self.assertEquals(self.view.nodeUnfold(),
                          u'[{"isLazy": true, '
                          '"href": "/portal/workspaces/subw/subsubw", '
                          '"isFolder": true, '
                          '"children": '
                          '[{"isLazy": true, '
                          '"href": "/portal/workspaces/subw/subsubw/faq", '
                          '"isFolder": true, "children": [], "title": "faq"}], '
                          '"title": ""}, '
                          '{"href": "/portal/workspaces/subw/doc", '
                          '"isFolder": false, "title": "doc"}]')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(HierarchicalSimpleViewTest),
        unittest.makeSuite(HierarchicalSimpleViewIntegrationTest),
        unittest.makeSuite(JsonNavigationIntegrationTest),
        unittest.makeSuite(DynaTreeNavigationIntegrationTest),
        ))
