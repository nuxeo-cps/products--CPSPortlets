##parameters=context_obj=None, show_docs=None

if context_obj is None:
    return []

mtool = context.portal_membership
if not mtool.checkPermission( 'List folder contents', context_obj):
    return []

folder_items = []

# Find bottom-most folder:
obj = context_obj
bmf = None
while 1:
    if obj.isPrincipiaFolderish:
        bmf = obj
        break
    parent = obj.aq_parent
    if not obj or parent == obj:
        break
    obj = parent
if bmf is None:
    bmf = context_obj

for object in bmf.objectValues():
    # skip folders beginning with '.'
    if object.getId()[0] == '.':
        continue
    # skip documents if show_docs is not set
    if int(show_docs) == 0 and not object.isPrincipiaFolderish:
        continue

    folder_items.append({'url': object.absolute_url(),
                         'title': object.title_or_id(),
                        })
return folder_items
