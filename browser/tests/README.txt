===============
TreeNode View
===============
:Version: $Id$
:Author: Tarek Ziad�
TreeNodeView let the client-side retrieve display-oriented informations about
the current location.

It is used to display the treeview and to get nodes from AJAX clients.

Note that Zope 3 provides an XMLTree based on xml branch retrieval.

This first version doesn't desync the tree with localdata, and gets raw branches
from the server, to keep client-side as light as possible.

It is more likely to be a static treeview with nodes that can get their
children from the server.

Let's create a fake folder for our tests and plug the view::

    >>> class FakeFactory:
    ...     id = 'Link'
    ...
    >>> class FakePortalUrl:
    ...     def getBaseUrl(self):
    ...         return '/'
    ...     def getPortalPath(self):
    ...         return '/cps'
    ...
    >>> class FakeMemberShip:
    ...     def checkPermission(self, *args, **kwargs):
    ...         return True
    ...
    >>> class FakePortalType:
    ...     pass
    ...
    >>> class FakePortalPortlets:
    ...     def renderIcon(self, *args, **kwargs):
    ...         return ''
    ...     def getFTIProperty(self, *args, **kwargs):
    ...         return ''
    ...
    >>> from zope.interface import implements
    >>> from OFS.interfaces import IObjectManager
    >>> class FakeFolder:
    ...     isPrincipiaFolderish = 1
    ...     portal_url = FakePortalUrl()
    ...     portal_membership = FakeMemberShip()
    ...     portal_types = FakePortalType()
    ...     portal_cpsportlets = FakePortalPortlets()
    ...     view = "yes, i have the view, don't worry"
    ...     portal_type = "Pretty Cool though heavy folder"
    ...
    ...     def __init__(self, id='none', parent=None):
    ...         self.id = id
    ...         self.items = []
    ...         self.parent = parent
    ...         if self.parent is not None:
    ...             if self not in self.parent.items:
    ...                 self.parent.items.append(self)
    ...
    ...     def getObjectPosition(self, id):
    ...         for item in self.items:
    ...             if isinstance(item, str) and item == id:
    ...                 return self.items.index(item)
    ...             elif hasattr(item, 'id') and item.id == id:
    ...                 return self.items.index(item)
    ...         return -1
    ...
    ...     def moveObjectToPosition(self, id, newpos):
    ...         oldpos = self.getObjectPosition(id)
    ...         temp = self.items[oldpos]
    ...         del self.items[oldpos]
    ...         self.items.insert(newpos, temp)
    ...
    ...     def objectIds(self):
    ...         ids = []
    ...         for element in self.items:
    ...             if isinstance(element, str):
    ...                 ids.append(element)
    ...             else:
    ...                 ids.append(element.id)
    ...         return ids
    ...
    ...     def objectItems(self):
    ...         return zip(self.objectIds(), self.items)
    ...
    ...     def restrictedTraverse(self, url, default=None):
    ...         return FakeFolder(url.split('/')[-1])
    ...
    ...     def manage_CPScutObjects(self, ids):
    ...         for id in ids:
    ...             position = self.getObjectPosition(id)
    ...             if position != -1:
    ...                 del self.items[position]
    ...
    ...     def manage_CPSpasteObjects(self, cb):
    ...         pass
    ...
    ...     def __getitem__(self, id):
    ...         for element in self.items:
    ...             if isinstance(element, str) and id == element:
    ...                 return element
    ...             elif hasattr(element, 'id') and id == element.id:
    ...                 return element
    ...         raise AttributeError(id)
    ...
    ...     def allowedContentTypes(self):
    ...         return (FakeFactory(),)
    ...
    ...     def absolute_url_path(self):
    ...         if self.parent is not None:
    ...             parent = self.parent.absolute_url_path()
    ...         else:
    ...             parent = ''
    ...         return  '%s/%s' % (parent, self.id)
    ...
    ...     def contentValues(self):
    ...         return self.items
    ...
    ...     def getId(self):
    ...         return self.id
    ...
    ...     def title_or_id(self):
    ...         return self.id


Let's create a structure::

    >>> root = FakeFolder('root')
    >>> sub_folder = FakeFolder('sub_folder', root)
    >>> sub_folder2 = FakeFolder('sub_folder2', root)
    >>> sub_folder3 = FakeFolder('sub_folder3', sub_folder2)
    >>> cps_portlets = FakeFolder('.cps_portlets', root)

Now let's try to get the nodes::

    >>> from Products.CPSPortlets.browser.treenodeview import TreeNodeView
    >>> my_view = TreeNodeView(root, None)
    >>> branch = my_view.getBranch()
    >>> branch.sort()
    >>> branch
    [{'folderish_children': [], 'has_folderish_children': False,
     'description': '', 'title': 'sub_folder', 'url': '/root/sub_folder',
     'selected': '', 'dynamic': True, 'content': None, 'safe_url':
     'url:.root.sub_folder', 'id': 'sub_folder', 'icon_tag': '', 'metadata':
      {}}, {'folderish_children': [{'has_folderish_children': False, 'title':
     'sub_folder3', 'url': '/sub_folder3', 'selected': '', 'dynamic': True,
     'folderish_children': [], 'safe_url': 'url:.sub_folder3', 'id':
     'sub_folder3', 'icon_tag': ''}], 'has_folderish_children': True,
     'description': '', 'title': 'sub_folder2', 'url': '/root/sub_folder2',
     'selected': '', 'dynamic': True, 'content': None, 'safe_url':
     'url:.root.sub_folder2', 'id': 'sub_folder2', 'icon_tag': '',
     'metadata': {}}]
