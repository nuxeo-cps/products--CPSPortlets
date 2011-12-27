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

import logging

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import View
from Products.CPSCore.ProxyBase import ALL_PROXY_META_TYPES
from Products.CPSonFive.browser import AqSafeBrowserView
from Products.CPSSchemas.DataStructure import DataStructure

logger = logging.getLogger(__name__)

def lstartswith(l1, l2):
    if len(l1) < len(l2):
        return False

    for x, y in zip(l1, l2):
        if x != y:
            return False
    return True

def tree_to_rpaths(tree):
    """Keep only the rpaths in a tree.

    This utility function is useful in tests and potentially for application
    code.
    """
    res = []
    for item in tree:
        produced = {}
        if item['children']:
            produced['children'] = tree_to_rpaths(item['children'])
        produced['rpath'] = item['rpath']

        res.append(produced)
    return res

class HierarchicalSimpleView(AqSafeBrowserView):
    """This view provides a full static forest from top and node subtrees.

    This is a transitional way of rendering portlets by resolving a view
    against the portlet, while waiting for deep design decisions about the
    propert ZTK-style way of hooking CPS portlets in the rendering.

    Nonetheless, this view is better placed to correct a few messy parts
    of other navigation portlets. Namely:
      - if defined, start_depth applies from the root of the tree, without
      taking permissions into account
      - does not rely on CPSNavigation, which is too much geared toward the
      kind of popup views it's meant to produce to be easily customized.
    """

    security = ClassSecurityInfo()

    def __init__(self, context, request):
        AqSafeBrowserView.__init__(self, context, request)
        self.url_tool = getToolByName(context, 'portal_url')

    security.declarePublic('setOptions')
    def setOptions(self, options):
        """Corresponds to the 'options' as seen from the template."""
        self.options = options
        ds = self.datastructure = options['datastructure']
        self.datamodel = ds.getDataModel()

        here = options.get('context_obj')
        if here is None:
            here = self.context
        self.here_rpath = self.url_tool.getRpath(here)

    def listToTree(self, tlist, unfold_to=None, unfold_level=1):
        """Transform TreeCache.getList() output into a proper tree (forest)

        Yes, this far too complicated, but one should NEVER represent
        a tree as a list, except at outermost level of the system.

        The unfold_to argument is used for cases where the forest is to be
        shown from its root with the path to some location fully displayed,
        including siblings of intermediate nodes. In case the location is a
        folder, its children are also displayed, up to unfold_level.
        With unfold_level=1, and unfold_to the current folder,
        this is the classical need of sidebar navigation portlets.

        With unfold_to coinciding with the beginning of the extracted tree and
        arbitrary unfold_level, this produces a proper subtree, suitable for
        dynamical unfolding (e.g, AJAX portlets).
        """

        if unfold_to is None: # BBB
            here_rpath = self.here_rpath.split('/')
        else:
            here_rpath = unfold_to.split('/')

        portal_path = self.url_tool.getPortalObject().absolute_url_path()
        if portal_path == '/':
            portal_path = ''

        res_tree = []
        from_top = []
        prev_rpath = ()
        for item in tlist:
            item_rpath = item['rpath'].split('/')

            # a rise in rpath means we have to climb up
            while from_top and not lstartswith(
                item_rpath, from_top[-1]['rpath'].split('/')):
                    from_top = from_top[:-1]

            if lstartswith(item_rpath, prev_rpath):
                # deeper that previous one => prev_rpath is the apparent parent
                # keep only those whose apparent parent is an ancestor of here
                # at level unfold_level (meaning that we climb up more level in
                # parents to do the checking)
                if unfold_level > 1:
                    f_rpath = prev_rpath[:1 - unfold_level]
                else:
                    f_rpath = prev_rpath
                if not lstartswith(here_rpath, f_rpath):
                    continue
                if prev_rpath:
                    from_top.append(produced)

            if from_top:
                parent = from_top[-1]
                append_to = parent['children']
                classes = parent.get('auto_classes', '')
                if not 'unfolded' in classes:
                    parent['auto_classes'] = ' '.join(('unfolded', classes))
            else:
                append_to = res_tree

            produced = item.copy()
            append_to.append(produced)
            produced['children'] = []

            classes = [] # CSS
            if here_rpath == item_rpath:
                classes.append('selected')

            produced['url'] = portal_path + '/' + item['rpath']
            if classes:
                produced['auto_classes'] = ' '.join(classes)
            prev_rpath = item_rpath

        return res_tree

    def initTreeCache(self):
        ttool = getToolByName(self.context, 'portal_trees')
        trees = [ttool[tid] for tid in self.datamodel['root_uids']]
        if len(trees) > 1:
            logger.error("%r does not support multiple trees yet",
                         self.__class___)
            raise NotImplementedError
        tree = trees[0]
        self.aqSafeSet('tree_cache', tree)
        return tree

    def under(self, forest, rpath):
        """Return the subtree of forest that's under given rpath, inclusive."""
        rpath = rpath.split('/')
        while True:
            for child in forest:
                child_rpath = child['rpath'].split('/')
                if lstartswith(child_rpath, rpath): # found
                    return child
                if lstartswith(rpath, child_rpath):
                    forest = child.get('children', ()) # go down
                    break
            else:
                raise LookupError(rpath)

    def makeChildEntry(self, container, oid, obj, container_rpath):
        return dict(title=obj.title_or_id(),
                    description='',
                    visible=True, # check done before-hand
                    url='%s%s/%s' % (self.url_tool.getBaseUrl(),
                                     container_rpath, oid))

    def addDocs(self, tree, container=None):
        """Add ordinary documents (not from TreeCache) to the given tree.

        We'll actually check for all proxy types and exclude those from
        TreeCache because:
          + it is assumed that there are usually more documents that folders
          + some folders may not be in the cache
        """
        rpath = tree['rpath']
        if container is None:
            portal = self.url_tool.getPortalObject()
            container = portal.restrictedTraverse(tree['rpath'])
        children = tree['children']

        # recurse and remember what was already there in the tree to avoid
        # duplicates
        already = set()
        for child in children:
            child_id = child['id']
            self.addDocs(child, container=container[child_id])
            already.add(child_id)

        children.extend(
            self.makeChildEntry(container, oid, obj, rpath)
            for oid, obj in container.objectItems(ALL_PROXY_META_TYPES)
            if oid not in already and _checkPermission(View, obj))

    security.declarePublic('getTree')
    def getTree(self):
        """Return the whole tree according to options and context. """
        tree = self.initTreeCache()
        dm = self.datamodel

        tkw = dict(start_depth=dm['start_depth'])
        end_depth = dm['end_depth']
        if end_depth: # 0 not understood by tree
            tkw[end_depth] = end_depth

        tlist = tree.getList(**tkw)
        forest = self.listToTree(tlist, unfold_to=self.here_rpath)
        if dm.get('with_docs', False):
            self.addDocs(self.under(forest, self.here_rpath))
        return forest

    security.declarePublic('nodeSubTree')
    def nodeSubTree(self, inclusive=False):
        """Return a subtree from context_obj.

        The depth is controlled by the 'subtree_depth' field.
        """
        tree = self.initTreeCache()
        dm = self.datamodel
        start = self.here_rpath
        tlist = tree.getList(prefix=start)
        depth = dm.get('subtree_depth', 1) # default value for BBB
        forest = self.listToTree(tlist, unfold_to=start, unfold_level=depth)
        if not inclusive:
            forest = forest[0]['children']
        if dm.get('with_docs'):
            self.addDocs(self.under(forest, self.here_rpath))
        return forest

InitializeClass(HierarchicalSimpleView)
