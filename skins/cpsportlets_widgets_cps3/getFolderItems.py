##parameters=context_obj=None, show_docs=None, max_title_words=0, context_rpath='', context_is_portlet=0, display_hidden_folders=1, **kw

base_url = context.getBaseUrl()

if context_is_portlet:
    context_obj = context.getLocalFolder()

if context_rpath:
    context_obj = context.restrictedTraverse(context_rpath, default=None)

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
    parent = obj.aq_parent.aq_inner
    if not obj or parent == obj:
        break
    obj = parent
if bmf is None:
    bmf = folder


mtool = context.portal_membership
checkPerm = mtool.checkPermission
if not checkPerm('List folder contents', bmf):
    return []

portal_types = context.portal_types
renderIcon = context.portal_cpsportlets.renderIcon

getFTIProperty = context.portal_cpsportlets.getFTIProperty
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
    ptype = getattr(object, 'portal_type', None)
    # Using a RAM cache to optimize the retrieval of FTI
    isdocument = getFTIProperty(ptype, 'cps_proxy_type') == 'document'
    display_as_document_in_listing = getFTIProperty(
        ptype, 'cps_display_as_document_in_listing')
    if int(show_docs) == 0 and (isdocument or display_as_document_in_listing):
        continue

    if not (isdocument or display_hidden_folders):
        try:
            content = object.getContent()
        except AttributeError:
            continue
        if content and \
            getattr(content.aq_inner.aq_explicit, 'hidden_folder', 0):
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
         'icon_tag': renderIcon(ptype, base_url, ''),
        })
return folder_items
