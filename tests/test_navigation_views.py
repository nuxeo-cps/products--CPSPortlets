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
from Products.CPSPortlets.browser.navigation import HierarchicalSimpleView

def rpaths_to_items(*rpaths):
    return [dict(rpath=p) for p in rpaths]

def tree_to_rpaths(tree):
    res = []
    for item in tree:
        produced = {}
        if item['children']:
            produced['children'] = tree_to_rpaths(item['children'])
        produced['rpath'] = item['rpath']

        res.append(produced)
    return res

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

    def test_listToTree(self):
        self.view.here_rpath = 'a/x/z'
        tree = self.view.listToTree(rpaths_to_items(
                'a', 'a/b', 'a/b/b1', 'a/x', 'a/x/a', 'a/x/z', 'a/y'))

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
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a/b/b1'),
                dict(rpath='a/x', children=[
                        dict(rpath='a/x/a'),
                        dict(rpath='a/x/z')]),
                dict(rpath='a/y')])


        # another border case : climbing 2 steps up
        tree = self.view.listToTree(rpaths_to_items(
                'a/b', 'a/b/b1', 'd', 'a/x', 'a/x/a', 'a/x/z', 'c'))
        self.assertEquals(tree_to_rpaths(tree), [
                dict(rpath='a/b'),
                dict(rpath='d'),
                dict(rpath='a/x', children=[
                        dict(rpath='a/x/a'),
                        dict(rpath='a/x/z')]),
                dict(rpath='c')])


def test_suite():
    return unittest.makeSuite(HierarchicalSimpleViewTest)
