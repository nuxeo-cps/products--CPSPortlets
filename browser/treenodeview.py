# -*- coding: iso-8859-15 -*-
# (C) Copyright 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""
  View that knows how to return a given branch of a treeview

"""
import logging

from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from OFS.CopySupport import CopyError
from Products.Five import BrowserView

class TreeNodeView(BrowserView):

    log = logging.getLogger('CPSPortlets.browser.TreeNodeView')

    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        self.utool = getToolByName(self.context, 'portal_url')
        self.tree_tool = getToolByName(self.context, 'portal_trees')

    def getNode(self, root=''):
        """ root is the url of the root node """
        self.log.debug("getNode: root rpath=%s", root)
        utool = self.utool
        portal_cpsportlets = getToolByName(self.context, 'portal_cpsportlets')

        base_url = self.utool.getBaseUrl()
        node = self._getRoot(root)
        object_id = node.getId()
        context_url = self.context.absolute_url_path()
        ptype = getattr(node, 'portal_type', None)
        title = node.title_or_id()
        has_folderish_children = self._hasSubFolders(node)
        object_url = node.absolute_url_path()
        renderIcon = portal_cpsportlets.renderIcon
        children = [self.getNode(item['rpath'])
                    for item in self._folderishChildren(node)]

        if object_url == context_url:
            selected = 'selected'
        else:
            selected = ''

        return {'id': object_id,
                'url': object_url,
                'safe_url': 'url:%s' % object_url.replace('/', '.'),
                'title': title,
                'icon_tag': renderIcon(ptype, base_url, ''),
                'has_folderish_children': has_folderish_children,
                'folderish_children': children,
                'selected': selected,
                'dynamic': not context_url.startswith(object_url)
                }

    def getBranch(self, show_docs=0, display_hidden_folders=1, recursive=0,
                  root=''):
        """ root is the url of the root node """
        context_obj = self._getRoot(root)

        folder_items = self._getFolderItems(context_obj, show_docs=show_docs,
                                 display_hidden_folders=display_hidden_folders,
                                 recursive=0)
        return folder_items

    def _rootRestrictedTraverse(self, path):
        
        portal = self.utool.getPortalObject()
        return portal.restrictedTraverse(path, default=None)

    def _getRoot(self, root=''):
        if (root is None or root == '') and (self.request is None
                                        or self.request.get('root', '') == ''):
            return self.context
        else:
            if root is None or root == '':
                root = self.request.get('root', '')
            return self._rootRestrictedTraverse(root)

    def _getTreeCache(self, folder, rpath=None):
        """Find the TreeCache object for given folder.

        Optional rpath can be passed to avoid computing it twice.

        Implementation uses for now a big assumption on the tree naming and uses
        rpath only
        """

        if rpath is None:
            if folder is None:
                return
            rpath = self.utool.getRpath(folder)
        
        return getattr(self.tree_tool.aq_explicit, rpath.split('/', 1)[0], None)
        
    def _getContent(self, object):
        content = None
        try:
            content = object.getContent()
        except AttributeError:
            pass
        return content

    def _hasSubFolders(self, folder):
        rpath = self.utool.getRpath(folder)
        tc = self._getTreeCache(folder, rpath=rpath)

        if tc is None:
            # costly fallback
            for id, item in folder.objectItems():
                if self._isFolderish(item):
                    return True
            return False
        
        # TODO cache this call for reuse ?
        depth = len(rpath.split('/')) # depth of children (l-1+1=l)
        return len(tc.getList(prefix=rpath, 
                              start_depth=depth, 
                              stop_depth=depth,filter=True)) > 0


    def _isFolderish(self, object): 
       return ((hasattr(object, 'isPrincipiaFolderish') and
                object.isPrincipiaFolderish==1) and
                not (object.getId().startswith('.') or
                     object.getId().startswith('_')))

    def _folderishChildren(self, folder):
       """GR: now returns part of a treecache structure. """
       rpath = self.utool.getRpath(folder)
       tc = self._getTreeCache(folder, rpath=rpath)
       if tc is None:
           # costly BBB fallback
           return [{'rpath': '/'.join((rpath, id)), 
                    'id': id} 
                   for id, item in folder.objectItems()
                   if self._isFolderish(item)]
       depth = len(rpath.split('/')) # depth of children (l-1+1=l)
       return tc.getList(prefix=rpath, start_depth=depth, stop_depth=depth,
                         filter=True, order=True)

    def _getFolderItems(self, context_obj=None, show_docs=0,
                        max_title_words=0, context_rpath='',
                        context_is_portlet=0, recursive=0, **kw):

       
        self.log.debug(
            "Enter _getFolderItems context_obj=%s, context_rpath=%s", 
            context_obj, context_rpath)

        context = self.context
        base_url = self.utool.getBaseUrl()

        if context_is_portlet:
            context_obj = context.getLocalFolder()

        if context_rpath:
            context_obj = context.restrictedTraverse(context_rpath, default=None)

        if context_obj is None:
            return []

        context_url = self.context.absolute_url_path()
        folder_items = []

        # Find bottom-most folder:
        obj = context_obj
        bmf = None
        while 1:
            if obj.isPrincipiaFolderish:
                bmf = obj
                break
            parent = obj.aq_inner.aq_parent
            if not obj or parent == obj:
                break
            obj = parent
        if bmf is None:
            bmf = folder


        mtool = getToolByName(context, 'portal_membership')
        checkPerm = mtool.checkPermission
        if not checkPerm('List folder contents', bmf):
            return []

        portal_types = getToolByName(context, 'portal_types')
        portal_cpsportlets = getToolByName(context, 'portal_cpsportlets')

        renderIcon = portal_cpsportlets.renderIcon
        getFTIProperty = portal_cpsportlets.getFTIProperty

        display_folders = int(kw.get('display_folders', 1))
        display_hidden_folders = int(kw.get('display_hidden_folders', 1))
        display_hidden_docs = int(kw.get('display_hidden_docs', 0))
        display_description = int(kw.get('display_description', 0))
        display_valid_docs = int(kw.get('display_valid_docs', 0))
        sort_by = kw.get('sort_by')

        # Dublin Core / metadata
        get_metadata = int(kw.get('get_metadata', 0))
        metadata_map = {
            'creator': 'Creator',
            'date': 'ModificationDate',
            'issued': 'EffectiveDate',
            'created': 'CreationDate',
            'rights': 'Rights',
            'language': 'Language',
            'contributor': 'Contributors',
            'source': 'source',
            'relation': 'relation',
            'coverage': 'coverage'}

        for item in self._folderishChildren(bmf):
            # GR: simply avoid contentValues, did not change anything else
            # once object variable is set
            object_id = item['id']
            if not bmf.hasObject(object_id):
                continue
            object = getattr(bmf, object_id)

            # filter out objects that cannot be viewed
            if not checkPerm('View', object):
                continue
            if getattr(object, 'view', None) is None:
                continue

            # skip documents if show_docs is not set
            ptype = getattr(object, 'portal_type', None)
            # Using a RAM cache to optimize the retrieval of FTI
            isdocument = getFTIProperty(ptype, 'cps_proxy_type') == 'document'
            display_as_document_in_listing = getFTIProperty(
                ptype, 'cps_display_as_document_in_listing')
            if int(show_docs) == 0 and (isdocument or display_as_document_in_listing):
                continue

            content = None

            # a folder is not 'documentish'
            # folderish documents are not folders.
            isfolder = not isdocument

            # hide folders?
            if isfolder and not display_folders:
                continue

            # hide hidden folders
            if isfolder and not display_hidden_folders:
                content = content or self._getContent(object)
                if content is not None and \
                    getattr(content.aq_inner.aq_explicit, 'hidden_folder', 0):
                    continue

            # hide hidden documentscontext_url
            # TODO not implemented in document schemas
            if isdocument and not display_hidden_docs:
                content = content or self._getContent(object)
                if content is not None and \
                    getattr(content.aq_inner.aq_explicit, 'hidden_document', 0):
                    continue

            # XXX TODO: Dublin Core effective / expiration dates

            # DublinCore / metadata information
            metadata_info = {}
            if get_metadata or sort_by in ('date', 'author'):
                content = content or self._getContent(object)
                for key, attr in metadata_map.items():
                    meth = getattr(content, attr)
                    if callable(meth):
                        value = meth()
                    else:
                        value = meth
                    if not value or value is 'None':
                        continue
                    if not isinstance(value, str):
                        try:
                            value = ', '.join(value)
                        except TypeError:
                            value = str(value)
                    metadata_info[key] = value

            # filter out documents not yet effective and expired documents
            if display_valid_docs:
                now = context.ZopeTime()
                content = content or self._getContent(object)
                if content is None:
                    continue
                if now < content.effective() or now > content.expires():
                    continue

            # title
            title = object.title_or_id()
            if max_title_words > 0:
                words = title.split(' ')
                if len(words) > max_title_words:
                    title = ' '.join(words[:int(max_title_words)]) + ' ...'

            # description
            description = ''
            if display_description:
                content = content or self._getContent(object)
                if content is not None:
                    description = getattr(content, 'Description', '')

            object_url = object.absolute_url_path()

            has_folderish_children = self._hasSubFolders(object)
            children = [self.getNode(item['rpath'])
                        for item in self._folderishChildren(object)]
            if object_url == context_url:
                selected = 'selected'
            else:
                selected = ''

            folder_items.append(
                {'id': object_id,
                 'url': object_url,
                 'safe_url': 'url:%s' % object_url.replace('/', '.'),
                 'title': title,
                 'content': content,
                 'description': description,
                 'icon_tag': renderIcon(ptype, base_url, ''),
                 'metadata': metadata_info,
                 'has_folderish_children': has_folderish_children,
                 'folderish_children': children,
                 'selected': selected,
                 'dynamic': not context_url.startswith(object_url)
                })

        # sorting
        def id_sortkey(a):
            return a['id']
        def title_sortkey(a):
            return a['title'].lower()
        def date_sortkey(a):
            return str(a['metadata']['date']) + a['id']
        def author_sortkey(a):
            return a['metadata']['creator'] + a['id']
        def cmp_desc(x, y):
            return -cmp(x, y)

        if sort_by:
            sort_direction = kw.get('sort_direction')
            make_sortkey = id_sortkey
            if sort_by == 'date':
                make_sortkey = date_sortkey
                sort_direction = sort_direction or 'desc'
            elif sort_by == 'title':
                make_sortkey = title_sortkey
            elif sort_by == 'author':
                make_sortkey = author_sortkey
            items = [ (make_sortkey(x), x) for x in folder_items ]
            if sort_direction == 'desc':
                items.sort(cmp_desc)
            else:
                items.sort()
            folder_items = [x[1] for x in items]

        return folder_items
