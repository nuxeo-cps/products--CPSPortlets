##parameters=context_obj=None, root_uids=None, REQUEST=None, **kw

from Products.CPSNavigation.CPSNavigation import CPSNavigation

if root_uids is None:
    return []

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

# XXX get base url from the request
base_url = context.getBaseUrl()

context_rpath = kw.get('context_rpath')
start_depth = kw.get('start_depth', 0)
end_depth = kw.get('end_depth', 0)

# contextual navigation
contextual = int(kw.get('contextual', 0)) == 1

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

for root_uid in root_uids:
    nav = CPSNavigation(current_uid=current_uid,
                        no_leaves=0,
                        context=context_obj,
                        root_uid=root_uid,
                        expand_all=expand_all,
                        authorized_only=authorized_only)
    for node in nav.getTree():
        # filter out items outside the specified depth
        depth = node['level'] - delta

        if start_depth and depth < start_depth:
            continue
        if end_depth and depth >= end_depth:
            continue

        object = node['object']

        rpath = object['rpath']
        open = (context_rpath + '/').startswith(rpath + '/')

        # filter out hidden folders
        if not display_hidden_folders and object['hidden_folder']:
            continue

        # gather data
        ptype = object['portal_type']
        selected = node['is_current'] and current_uid == rpath
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
            {'url': base_url + rpath,
             'title': object['title_or_id'],
             'depth': depth,
             'selected': selected,
             'open': open, # node.get('is_open') returns incorrect information
             'icon_tag': renderIcon(ptype, base_url, ''),
             'managers': managers,
             'description': description,
             'visible': visible,
            })

return folder_items
