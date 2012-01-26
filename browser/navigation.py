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

class HierarchicalSimpleView(AqSafeBrowserView):
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

    security = ClassSecurityInfo()

    security.declarePublic('setOptions')
    def setOptions(self, options):
        """Corresponds to the 'options' as seen from the template."""
        self.options = options
        ds = self.datastructure = options['datastructure']
        self.datamodel = ds.getDataModel()

        here = options.get('context_obj')
        if here is None:
            here = self.context
        utool = getToolByName(self.context, 'portal_url')
        self.here_rpath = utool.getRpath(here)

    def listToTree(self, tlist):
        """Transform TreeCache.getList() output into a proper tree.

        Yes, this far too complicated, but one should NEVER represent
        a tree as a list, except at outermost level of the system.
        """

        here_rpath = self.here_rpath.split('/')
        utool = getToolByName(self.context, 'portal_url')
        portal_path = utool.getPortalObject().absolute_url_path()
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
                if not lstartswith(here_rpath, prev_rpath):
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

    security.declarePublic('getTree')
    def getTree(self):
        """Return the tree according to options and context. """
        dm = self.datamodel
        ttool = getToolByName(self.context, 'portal_trees')
        trees = [ttool[tid] for tid in dm['root_uids']]
        if len(trees) > 1:
            logger.error("%r does not support multiple trees yet",
                         self.__class___)
            raise NotImplementedError
        tree = trees[0]
        self.aqSafeSet('tree_cache', tree)

        tkw = dict(start_depth=dm['start_depth'])
        end_depth = dm['end_depth']
        if end_depth: # 0 not understood by tree
            tkw['stop_depth'] = end_depth

        tlist = tree.getList(**tkw)
        return self.listToTree(tlist)


InitializeClass(HierarchicalSimpleView)
