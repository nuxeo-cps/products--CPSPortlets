##parameters=context_obj=None, show_docs=None, max_title_words=0

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
    # remove objects with ids beginning with '.'
    if object.getId().startswith('.'):
        continue
    # filter out objects that cannot be viewed
    if not checkPerm('View', object):
        continue
    if getattr(object, 'view', None) is None:
        continue
    # skip documents if show_docs is not set
    if int(show_docs) == 0 and not object.isPrincipiaFolderish:
        continue

    # XXX TODO: Dublin Core effective / expiration dates

    # title 
    title = object.title_or_id()
    if max_title_words > 0:
        words = title.split(' ')
        if len(words) > max_title_words:
            title = ' '.join(words[:int(max_title_words)]) + ' ...'

    folder_items.append(
        {'url': '/' + object.absolute_url(relative=1),
         'title': title,
         'icon_tag': '', #XXX render the icon tag
        })
return folder_items
