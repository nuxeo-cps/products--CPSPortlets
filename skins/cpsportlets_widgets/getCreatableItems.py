
items = []
utool = context.portal_url
base_url = utool.getBaseUrl()

content_types = context.getSortedContentTypes(allowed=1)
renderIcon = context.portal_cpsportlets.renderIcon

for ptype in content_types:
    ptype_id = ptype['id']
    items.append({
        'title': ptype['Title'],
        'id': ptype_id,
        'icon_tag': renderIcon(ptype_id, base_url, '')
    })

return items
