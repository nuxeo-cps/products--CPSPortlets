##parameters=context_obj=None, only_children=None, REQUEST=None, **kw

from Products.CPSNavigation.CPSNavigation import CPSNavigation

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

utool = context.portal_url

nav = CPSNavigation(context=context_obj,
                    request_form=REQUEST.form,
                    **kw
                   )

context_url = context_obj.absolute_url()

folder_items = []
for tree in nav.getTree():
    object = tree['object']
    url = object['url']

    # only display children
    if only_children and url == context_url:
        continue

    folder_items.append({'url': url,
                         'title': object['title_or_id'],
                        })

return folder_items
