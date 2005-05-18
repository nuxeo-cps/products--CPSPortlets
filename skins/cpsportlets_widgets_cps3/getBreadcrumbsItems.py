##parameters=**kw

parent = kw.get('parent')
if not context.isPrincipiaFolderish:
    parent = 1

REQUEST = context.REQUEST
breadcrumb_set = REQUEST.get('breadcrumb_set')
if breadcrumb_set != None:
    return breadcrumb_set

base_url = context.cpsskins_getBaseUrl()
url = kw.get('url')
if url is None:
    url = base_url

display_hidden_folders = int(kw.get('display_hidden_folders', 1))
display_site_root = int(kw.get('display_site_root', 1))

path = url.split('/')
path = filter(None, path)
if parent:
    path = path[:-1]

portal = context.portal_url.getPortalObject()
portal_id = portal.getId()
checkPermission = context.portal_membership.checkPermission
items = []

first_item = int(kw.get('first_item', 0))
if first_item == 0 or display_site_root:
    items.append(
        {'id': portal_id,
         'title': portal.title_or_id(),
         'url': base_url,
        })

if first_item == 0:
    first_item = 1

bc_range = range(first_item, len(path) +1)
for i in bc_range:
    ipath = path[:i]
    obj = portal.restrictedTraverse(ipath)

    if not checkPermission('View', obj):
        continue
    title = obj.title_or_id()

    try:
        is_archived = obj.isProxyArchived()
    except AttributeError:
        is_archived = 0
    if is_archived:
        # XXX i18n
        title = 'v%s (%s)' % (obj.getRevision(), title)

    if not display_hidden_folders:
        content = obj.getContent()
        if getattr(content.aq_inner.aq_explicit, 'hidden_folder', 0):
            continue

    rpath = '/'.join(ipath)
    url = base_url + '%s/' % rpath
    obj_id = ipath[-1]

    items.append({'id': obj_id,
                  'title': title,
                  'url': url,
                 })

return items
