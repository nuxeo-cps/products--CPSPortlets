##parameters=context_obj=None, only_children=None, REQUEST=None, **kw

from Products.CPSNavigation.CPSNavigation import CPSNavigation

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

context_rpath = kw.get('context_rpath')
start_depth = kw.get('start_depth', 0)
end_depth = kw.get('end_depth', 0)
contextual = kw.get('contextual')
contextual = int(contextual) == 1

if contextual:
    context_uid = context_rpath
else:
    context_uid = None

try:
    nav = CPSNavigation(context_uid=context_uid,
                        context=context_obj,
                        request_form=REQUEST.form,
                        **kw)
# root_uid not set
except KeyError:
    return []

folder_items = []

# the depth is relative to the current folder in contextual mode
delta = 0
if contextual:
    delta = len(context_rpath.split('/')) -1

for tree in nav.getTree():
    object = tree['object']
    rpath = object['rpath']
    depth = object['depth'] - delta
    if depth < 0:
        continue

    selected = (rpath == context_rpath)

    if contextual:
        if depth == 0 and not selected:
            continue

    # only display children
    if only_children:
        if rpath == context_rpath:
            continue

    # filter out items outside the specified depth
    if start_depth:
        if depth < start_depth:
            continue
    if end_depth:
        if depth > end_depth:
            continue

    folder_items.append({'url': object['url'],
                         'title': object['title_or_id'],
                         'depth': depth,
                         'selected': selected,
                        })

return folder_items
