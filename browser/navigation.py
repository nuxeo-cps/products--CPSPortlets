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

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import View
from Products.CPSCore.ProxyBase import ALL_PROXY_META_TYPES
from Products.CPSUtil import minjson as json
from baseview import BaseView

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
        if item.get('children', ()):
            produced['children'] = tree_to_rpaths(item['children'])
        produced['rpath'] = item['rpath']

        res.append(produced)
    return res

class HierarchicalSimpleView(BaseView):
    """This view provides a full tree, in a purely static way. No AJAX.

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

    def __init__(self, datamodel, request):
        BaseView.__init__(self, datamodel, request)
        self.here_rpath = self.url_tool().getRpath(self.context)
        self.icon_uris = {} # cache portal_type -> icon URI

    def listToTree(self, tlist, unfold_to=None, unfold_level=1,
                   show_hidden=False):
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

        utool = self.url_tool()
        portal_path = utool.getPortalObject().absolute_url_path()

        if unfold_to is None: # BBB
            here_rpath = self.here_rpath.split('/')
        else:
            here_rpath = unfold_to.split('/')

        if portal_path == '/':
            portal_path = ''

        res_tree = []
        from_top = []
        prev_rpath = ()
        for item in tlist:
            if not show_hidden and item.get('hidden_folder'):
                continue
            terminal = False
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
                if len(here_rpath) - len(f_rpath) == unfold_level - 1:
                    terminal = True
                if prev_rpath:
                    from_top.append(produced)
            else:
                # sibling of previous one is terminal if prev is
                terminal = produced.get('terminal', False)

            if from_top:
                parent = from_top[-1]
                append_to = parent['children']
                classes = parent.get('auto_classes', '')
                if not 'unfolded' in classes:
                    parent['auto_classes'] = ' '.join(('unfolded', classes))
            else:
                append_to = res_tree

            produced = item.copy()
            if terminal:
                produced['terminal'] = True
            produced['from_treecache'] = True
            append_to.append(produced)
            produced['children'] = []
            produced['icon'] = self.iconUri(item)
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
                         self.__class__)
            raise NotImplementedError
        tree = trees[0]
        self.aqSafeSet('tree_cache', tree)
        return tree

    def under(self, forest, rpath):
        """Return the subtree of forest that's under given rpath, inclusive.
        """
        if not forest:
            return
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
        doc = obj.getContent()
        base_url = self.url_tool().getBaseUrl()

        rpath = '/'.join((container_rpath, oid))
        child = dict(title=obj.title_or_id(),
                    isLazy=False,
                    description='',
                    visible=True, # check done before-hand,
                    portal_type=obj.portal_type,
                    rpath=rpath,
                    icon=self.iconUri(obj),
                    url=base_url+rpath)

        if not self.datamodel['show_attached_files']:
            child['is_folder'] = False
        else:
            files = [dict(title=att['current_filename'],
                          url=att['content_url'],
                          rpath=att['content_url'][len(base_url):],
                          is_folder=False,
                          icon=base_url+att['mimetype'].icon_path)
                     for att in doc.getAttachedFilesInfo()]
            child['is_folder'] = bool(files)
            if files:
                child['children'] = files

        return child

    def addDocs(self, tree, container=None, container_rpath=None):
        """Add ordinary documents (not from TreeCache) to the given tree.

        We'll actually check for all proxies and exclude those from
        TreeCache because:
          + it is assumed that there are usually more documents that folders
          + some folders may not be in the cache

        Nodes that are marked as terminal don't get any documents.

        container and container_rpath kwargs are used for recursion,
        and should not be passed by primary caller.
        If they are, and don't correspond, result is likely to be an exception
        or to be impredictible.

        Note: it'd be probably simpler and a bit faster to add document leaves
        directly from list_to_tree, and avoid this addDocs method altogether,
        but for now we prefer the latter to stay a pure manipulation of python
        base types, and not have to do with Zope API (easier to unit test).
        """
        if not tree or tree.get('terminal', False):
            return
        rpath = tree['rpath']
        if container is None:
            portal = self.url_tool().getPortalObject()
            container_rpath = tree['rpath']
            container = portal.restrictedTraverse(container_rpath)

        children = tree['children']

        # recurse and remember what was already there in the tree to avoid
        # duplicates
        already = set()
        for child in children:
            child_rpath = child['rpath']
            self.addDocs(child, container_rpath=child_rpath,
                         container=container.restrictedTraverse(
                    child_rpath[len(container_rpath)+1:]))
            already.add(child['id'])

        children.extend(
            self.makeChildEntry(container, oid, obj, rpath)
            for oid, obj in container.objectItems(ALL_PROXY_META_TYPES)
            if oid not in already and _checkPermission(View, obj))

    def getTree(self):
        """Return the whole tree according to options and context. """
        tree = self.initTreeCache()
        dm = self.datamodel

        tkw = dict(start_depth=dm['start_depth'])
        end_depth = dm['end_depth']
        if end_depth: # 0 not understood by tree
            tkw['stop_depth'] = end_depth

        tkw['filter'] = not dm['display_hidden_folders']
        tlist = tree.getList(**tkw)
        forest = self.listToTree(tlist, unfold_to=self.here_rpath,
                                 show_hidden=dm.get('display_hidden_folders'))

        if dm.get('show_docs', False):
            self.addDocs(self.under(forest, self.here_rpath))
        return forest

    def nodeSubTree(self, inclusive=False):
        """Return a subtree from context_obj.

        The depth is controlled by the 'subtree_depth' field.
        """
        tree = self.initTreeCache()
        dm = self.datamodel
        start = self.here_rpath

        tlist = tree.getList(prefix=start,
                             filter=not dm['display_hidden_folders'])
        depth = dm.get('subtree_depth', 1) # default value for BBB
        forest = self.listToTree(tlist, unfold_to=start, unfold_level=depth,
                                 show_hidden=dm.get('display_hidden_folders'))
        if dm.get('show_docs'):
            self.addDocs(self.under(forest, self.here_rpath))
        if not inclusive and forest:
            # in practice (see #2569) the current node might already be skipped
            if forest[0]['rpath'] == start:
                if len(forest) > 1:
                    logger.error("While removing current node (for unfolding)"
                                 "found unexpected siblings. forest=%r",
                                 forest)
                forest = forest[0]['children']
        return forest

    def iconUri(self, item):
        """Return URI of icon for item's portal_type.

        item can be a dict (as from the TreeCache) or a content object.
        """
        ptype = item['portal_type']
        if ptype is None: # happens in unit tests
            return
        uri = self.icon_uris.get(ptype)
        if uri is not None:
            return uri
        icon = getToolByName(self.context, 'portal_types')[ptype].getIcon()
        self.icon_uris[ptype] = uri = self.url_tool().getBaseUrl() + icon
        return uri


class JsonNavigation(HierarchicalSimpleView):
    """Subclass to present subtrees under context_obj node in Json."""

    def nodeUnfold(self):
        """Return unfolded navigation in json"""
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        return json.write(self.extract(self.nodeSubTree()))


class DynaTreeNavigation(JsonNavigation):

    def extract(self, forest):
        """Extract from forest in format expected by dynatree.
        """
        res = []
        for tree in forest:
            is_folder = tree.get('from_treecache') or tree.get('is_folder')
            node = dict(title=tree['title'], isFolder=is_folder,
                        href=tree['url'])
            if is_folder:
                node['children'] = self.extract(tree.get('children', ()))
                node['isLazy'] = True
            if self.datamodel['show_icons']:
                icon = tree.get('icon')
                if icon is not None:
                    node['icon'] = icon
            res.append(node)
        return res
