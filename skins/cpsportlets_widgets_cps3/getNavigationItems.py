##parameters=context_obj=None, root_uids=[''], REQUEST=None, **kw

from Products.CPSNavigation.CPSNavigation import CPSNavigation

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
kw['expand_all'] = int(kw.get('expand', 0)) == 1

if contextual:
    context_uid = context_rpath
else:
    context_uid = None

folder_items = []

# the depth is relative to the current folder in contextual mode
delta = 0
if contextual:
    delta = len(context_rpath.split('/')) -1

portal_types = context.portal_types
renderIcon = context.portal_cpsportlets.renderIcon

if root_uids == []:
    root_uids = ['']

for root_uid in root_uids:
    try:
        nav = CPSNavigation(context_uid=context_uid,
                            no_leaves=0,
                            context=context_obj,
                            root_uid=root_uid,
                            request_form=REQUEST.form,
                            **kw)
    # root_uid not set
    except KeyError:
        nav = None

    if nav is None:
        continue
    for tree in nav.getTree():
        object = tree['object']
        rpath = object['rpath']
        ptype = object['portal_type']
        depth = object['depth'] - delta
        if depth < 0:
             continue

        selected = (context_rpath == rpath)
        open = (context_rpath + '/').startswith(rpath + '/')

        if contextual:
            if depth == 0 and not selected:
                 continue

            if not rpath.startswith(context_rpath):
                continue

        # filter out items outside the specified depth
        if start_depth:
            if depth < start_depth:
                continue
        if end_depth:
            if depth >= end_depth:
                continue

        # filter out hidden folders
        if not display_hidden_folders:
            if object.get('hidden_folder', False):
                continue

        folder_items.append(
            {'url': base_url + rpath,
             'title': object['title_or_id'],
             'depth': depth,
             'selected': selected,
             'open': open,
             'icon_tag': renderIcon(ptype, base_url, ''),
            })

return folder_items
