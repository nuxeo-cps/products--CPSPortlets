##parameters=context_obj=None, only_children=None, REQUEST=None, **kw

from Products.CPSNavigation.CPSNavigation import CPSNavigation

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

context_rpath = kw.get('prefix')
# XXX: root_uid
nav = CPSNavigation(context_uid=context_rpath,
                    context=context_obj,
                    request_form=REQUEST.form,
                    **kw
                   )

folder_items = []
for tree in nav.getTree():
    object = tree['object']

    # only display children
    if only_children and object['rpath'] == context_rpath:
        continue

    folder_items.append({'url': object['url'],
                         'title': object['title_or_id'],
                        })

return folder_items
