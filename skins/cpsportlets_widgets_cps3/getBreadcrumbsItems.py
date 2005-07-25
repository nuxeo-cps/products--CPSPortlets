##parameters=**kw

REQUEST = context.REQUEST
breadcrumb_set = REQUEST.get('breadcrumb_set')
if breadcrumb_set != None:
    return breadcrumb_set

utool = context.portal_url
mtool = context.portal_membership
checkPermission = mtool.checkPermission

# display options
parent = int(kw.get('parent', 0))
display_hidden_folders = int(kw.get('display_hidden_folders', 1))
display_site_root = int(kw.get('display_site_root', 1))
first_item = int(kw.get('first_item', 0))

# compute the breadcrumbs
base_url = utool.getBaseUrl()
portal = utool.getPortalObject()
breadcrumbs = utool.getBreadCrumbs(context=context, only_parents=parent)

items = []
if first_item == 0 or display_site_root:
    items.append(
        {'id': portal.getId(),
         'title': portal.title_or_id(),
         'url': base_url,
        })

if first_item == 0:
    first_item = 1

for obj in breadcrumbs[first_item:]:
    # continue if the object is not visible
    if not checkPermission('View', obj):
        continue

    # compute the title
    title = obj.title_or_id()
    try:
        is_archived = obj.isProxyArchived()
    except AttributeError:
        is_archived = 0
    if is_archived:
        # XXX i18n
        title = 'v%s (%s)' % (obj.getRevision(), title)

    # hidden folders
    if not display_hidden_folders:
        content = obj.getContent()
        if getattr(content.aq_inner.aq_explicit, 'hidden_folder', 0):
            continue

    items.append({
        'id': obj.getId(),
        'title': title,
        'url': utool.getRpath(obj),
        })

return items
