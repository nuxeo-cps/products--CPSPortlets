##parameters=**kw

parent = kw.get('parent')
if not context.isPrincipiaFolderish:
    parent = 1

REQUEST = context.REQUEST
breadcrumb_set = REQUEST.get('breadcrumb_set')
if breadcrumb_set != None:
    return breadcrumb_set

url = kw.get('url')
if url is None:
    url = context.getBaseUrl()

display_hidden_folders = kw.get('display_hidden_folders', 1)

path = url.split('/')
path = filter(None, path)
if parent:
    path = path[:-1]

portal = context.portal_url.getPortalObject()
portal_id = portal.getId()
checkPermission = context.portal_membership.checkPermission
items = []

first_item = kw.get('first_item', 0)

for i in range(first_item, len(path)):
    ipath = path[:i+1]
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
        if getattr(content.aq_explicit, 'hidden_folder', 0):
            continue

    rpath = '/'.join(ipath)
    url = '/%s/' % rpath
    obj_id = ipath[-1]
    if obj_id != portal_id:
        url += 'view'

    items.append({'id': obj_id,
                  'title': title,
                  'url': url,
                 })
return items
