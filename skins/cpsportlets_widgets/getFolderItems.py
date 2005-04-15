##parameters=context_obj=None, show_docs=None, max_title_words=0, context_rpath='', context_is_portlet=0, **kw

base_url = context.cpsskins_getBaseUrl()

if not not context_is_portlet:
    context_obj = context.getLocalFolder()

if context_rpath:
    context_obj = context.restrictedTraverse(base_url + context_rpath, default=None)

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

getRelativeUrl = context.portal_url.getRelativeUrl

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
        {'url': base_url + getRelativeUrl(object),
         'title': title,
         'icon_tag': '', #XXX render the icon tag
        })
return folder_items
