##parameters=context_obj=None, only_children=None, REQUEST=None, **kw

from Products.CPSNavigation.CPSNavigation import CPSNavigation

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

context_rpath = kw.get('prefix')
try:
    nav = CPSNavigation(context_uid=context_rpath,
                        context=context_obj,
                        request_form=REQUEST.form,
                        **kw)
# root_uid not set
except KeyError:
    return []

folder_items = []

start_depth = kw.get('start_depth', 0)
end_depth = kw.get('end_depth', 0)
contextual = kw.get('contextual')

# the depth is relative to the current folder in contextual mode
delta = 0
if contextual:
    delta = len(context_rpath.split('/')) -1

for tree in nav.getTree():
    object = tree['object']

    # only display children
    if only_children and object['rpath'] == context_rpath:
        continue

    # filter out items outside the specified depth
    depth = object['depth'] - delta
    if start_depth:
        if depth < start_depth:
            continue
    if end_depth:
        if depth > end_depth:
            continue

    folder_items.append({'url': object['url'],
                         'title': object['title_or_id'],
                         'depth': depth,
                        })

return folder_items
