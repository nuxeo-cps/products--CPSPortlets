##parameters=context_obj=None, show_docs=None

mtool = context.portal_membership
if not mtool.checkPermission( 'List folder contents', context_obj):
    return []

utool = context.portal_url

folder_items = []
for object in context_obj.objectValues():
    # skip documents if show_docs is not set
    if int(show_docs) == 0 and not object.isPrincipiaFolderish:
        continue

    folder_items.append({'url': utool.getRelativeUrl(object),
                         'title': object.title_or_id(),
                        })
return folder_items
