##parameters=context_obj=None, show_docs=None

if context_obj is None:
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

mtool = context.portal_membership
checkPerm = mtool.checkPermission
if not checkPerm( 'List folder contents', bmf):
    return []

for object in bmf.objectValues():
    # filter out objects that cannot be viewed
    if not checkPerm('View', object):
        continue
    if getattr(object, 'view', None) is None:
        continue
    # skip documents if show_docs is not set
    if int(show_docs) == 0 and not object.isPrincipiaFolderish:
        continue

    # XXX TODO: Dublin Core effective / expiration dates

    folder_items.append({'url': object.absolute_url(),
                         'title': object.title_or_id(),
                        })
return folder_items
