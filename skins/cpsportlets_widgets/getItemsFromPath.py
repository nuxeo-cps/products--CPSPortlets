##parameters=links=[], max_title_words=0, **kw

# XXX get base url from the request
base_url = context.getBaseUrl()

max_title_words = int(max_title_words)

portal_url = context.portal_url
portal = portal_url.getPortalObject()

items = []
mtool = context.portal_membership
checkPerm = mtool.checkPermission
portal_types = context.portal_types
renderIcon = context.portal_cpsportlets.renderIcon
getRelativeUrl = portal_url.getRelativeUrl

for path in links:
    if path.startswith('/'):
        path = path[1:]
    object = portal.restrictedTraverse(path, default=None)
    if object is None:
        continue
    if not checkPerm('View', object):
        continue

    ptype = getattr(object, 'portal_type', None)

    # title 
    title = object.title_or_id()
    if max_title_words > 0:
        words = title.split(' ')
        if len(words) > max_title_words:
            title = ' '.join(words[:int(max_title_words)]) + ' ...'

    items.append(
        {'url': base_url + getRelativeUrl(object),
         'title': title,
         'icon_tag': renderIcon(ptype, base_url, ''),
        })

return items
