##parameters=context_obj=None, root_uids=[], REQUEST=None, **kw

from Products.CPSNavigation.CPSNavigation import CPSNavigation

if root_uids is None:
    return []

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

base_url = context.cpsskins_getBaseUrl()

context_rpath = kw.get('context_rpath')
start_depth = kw.get('start_depth', 0)
end_depth = kw.get('end_depth', 0)

# contextual navigation
contextual = int(kw.get('contextual', 0)) == 1

if contextual:
    context_uid = context_rpath
else:
    context_uid = None

# show hidden folders
display_hidden_folders = int(kw.get('display_hidden_folders', 0)) == 1

# expand all nodes?
expand_all = int(kw.get('expand', 0)) == 1

# apply view control
authorized_only = int(kw.get('authorized_only', 1)) == 1

# addition display details
display_managers = kw.get('display_managers', 0)
display_description = kw.get('display_description', 0)

current_uid = context_rpath
if contextual:
    root_uids = [root_uid for root_uid in root_uids
                 if current_uid.startswith(root_uid+'/')]

portal_types = context.portal_types
renderIcon = context.portal_cpsportlets.renderIcon
folder_items = []

# the relative depth is relative to the current folder in contextual mode
delta = 0
if contextual:
    delta = len(context_rpath.split('/')) -1

# this is needed to get into the 'for' loop in case root_uid in not set.
# in that case, the 'context' is used to determine the root_uid.
if root_uids == []:
    root_uids = ['']

for root_uid in root_uids:
    try:
        nav = CPSNavigation(current_uid=current_uid,
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
            continue

        # filter out items outside the specified depth
        if start_depth and depth < start_depth:
            continue
        if end_depth and depth >= end_depth:
            continue

        object = node['object']

        rpath = object['rpath']

        # filter out hidden folders
        if not display_hidden_folders and object['hidden_folder']:
            continue

        # gather data
        ptype = object['portal_type']
        selected = node['is_current'] and current_uid == rpath

        if contextual:
            if depth == 0 and not selected:
                continue
            if not rpath.startswith(context_rpath):
                continue

        description = ''
        if display_description:
            description = object['description'] # XXX not acquisition safe

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
            {'url': base_url + rpath,
             'title': object['title_or_id'],
             'depth': depth,
             'level': level,
             'selected': selected,
             'open': node.get('is_open'),
             'icon_tag': renderIcon(ptype, base_url, ''),
             'managers': managers,
             'description': description,
             'visible': visible,
            })

return folder_items
