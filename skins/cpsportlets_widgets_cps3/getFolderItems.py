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

getFTIProperty = context.portal_cpsportlets.getFTIProperty
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
    portal_type = getattr(object, 'portal_type', None)
    # Using a RAM cache to optimize the retrieval of FTI
    isdocument = getFTIProperty(portal_type, 'cps_proxy_type') == 'document'
    display_as_document_in_listing = getFTIProperty(
        portal_type, 'cps_display_as_document_in_listing')
    if int(show_docs) == 0 and (isdocument or display_as_document_in_listing):
        continue

    # XXX TODO: Dublin Core effective / expiration dates

    folder_items.append(
        {'url': '/' + object.absolute_url(relative=1),
         'title': object.title_or_id(),
        })
return folder_items
