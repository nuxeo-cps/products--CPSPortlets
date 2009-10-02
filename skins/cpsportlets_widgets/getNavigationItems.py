##parameters=context_obj=None, root_uids=[], REQUEST=None, **kw
#
# $Id$
"""Return a list of navigation items (with depth information)
corresponding to the given constraints, roots, start depth, end_depth, etc.
"""

from logging import getLogger

from Products.CPSNavigation.CPSNavigation import CPSNavigation

logger = getLogger('getNavigationItems')

if root_uids is None:
    return []

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

# Used to discard nodes with depth < start_depth:
start_depth = kw.get('start_depth', 0)

# Used to discard nodes with depth >= end_depth:
end_depth = kw.get('end_depth', 0)

## logger.debug("start, end = %s, %s"
##              % (start_depth, end_depth))

# Used to only consider root_uids of the given context_rpath (context_rpath
# being the current location during a navigation).
contextual = int(kw.get('contextual', 0)) == 1
context_rpath = kw.get('context_rpath')

# folder prefixes
folder_prefixes = kw.get('folder_prefixes', [])

# show hidden folders
display_hidden_folders = int(kw.get('display_hidden_folders', 0)) == 1

# expand all nodes?
expand_all = int(kw.get('expand', 0)) == 1

# apply view control
authorized_only = int(kw.get('authorized_only', 1)) == 1

# addition display details
display_managers = kw.get('display_managers', 0)
display_description = kw.get('display_description', 0)

utool = context.portal_url
current_obj = context_obj
while not current_obj.isPrincipiaFolderish:
    current_obj = current_obj.aq_inner.aq_parent
current_uid = utool.getRpath(current_obj)

if contextual:
    root_uids = [root_uid for root_uid in root_uids
                 if current_uid.startswith(root_uid+'/')]

portal_types = context.portal_types
renderIcon = context.portal_cpsportlets.renderIcon
folder_items = []

# The relative depth is relative to the current folder in contextual mode
delta = 0
if contextual:
    delta = len(context_rpath.split('/')) -1

# This is needed to get into the 'for' loop in case root_uid in not set.
# in that case, the 'context' is used to determine the root_uid.
if root_uids == []:
    root_uids = ['']

base_url = utool.getBaseUrl()

for root_uid in root_uids:
    if current_uid.startswith(root_uid):
        # use a fake current object for cpsnavigation otherwhise it will not
        # find the object corresponding to current_uid if it is not a container
        # (element of portal_tree) and will not expand properly the tree.
        current = {'rpath': current_uid}
    else:
        current = None
    try:
        nav = CPSNavigation(current=current, current_uid=current_uid,
            no_leaves=0,
            context=context_obj,
            root_uid=root_uid,
            expand_all=expand_all,
            authorized_only=authorized_only)
    except KeyError:
        nav = None

    if nav is None:
        continue

    for node in nav.getTree():

        # save the node's level
        level = node['level']

        # compute the item's depth
        depth = level - delta
        if depth < 0:
##             logger.debug("%s, %s depth < 0"
##                          % (node['object'].get('rpath'),
##                             node.get('level')))
            continue

        # filter out items outside the specified depth
        if start_depth and depth < start_depth:
##             logger.debug("%s, %s depth < start_depth"
##                          % (node['object'].get('rpath'),
##                             node.get('level')))
            continue
        if end_depth and depth >= end_depth:
##             logger.debug("%s, %s depth >= end_depth"
##                          % (node['object'].get('rpath'),
##                             node.get('level')))
            continue

##         logger.debug("%s, %s CONSIDERING"
##                      % (node['object'].get('rpath'),
##                         node.get('level')))

        # cpsnav object is a mapping
        object = node['object']

        rpath = object['rpath']

        # keeps items located under specified folder prefixes
        if folder_prefixes:
            ok = False
            for folder_prefix in folder_prefixes:
                if rpath.startswith(folder_prefix):
                    ok = True
                    break
            if not ok:
                continue

        # filter out hidden folders
        if not display_hidden_folders and object['hidden_folder']:
            continue

        # gather data
        ptype = object['portal_type']
        selected = node['is_current'] and current_uid == rpath
        # used for navigation tabs
        selected_tab = (current_uid + '/').startswith(rpath + '/')

        if contextual:
            if depth == 0 and not selected:
                continue
            if not rpath.startswith(context_rpath + '/'):
                continue


        description = ''
        if display_description:
            description = object['description']

        managers = []
        if display_managers:
            managers = object['managers']
        # the visible attribute specify wheter or not the current user as the
        # view permission on the target object: if authorized_only is set to
        # False, the user can still view the title/description/managers but
        # cannot directly access the object (no link to it)
        visible = 1
        if not authorized_only:
            visible = object['visible']

        folder_items.append(
            {'url': utool.getUrlFromRpath(rpath),
             'rpath': rpath,
             'title': object['title_or_id'],
             'depth': depth-start_depth,
             'level': level,
             'selected': selected,
             'selected_tab': selected_tab,
             'open': node.get('is_open'),
             'icon_tag': renderIcon(ptype, base_url, ''),
             'managers': managers,
             'description': description,
             'visible': visible,
            })

return folder_items
