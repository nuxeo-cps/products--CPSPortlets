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

metadata_map = {
    'creator': 'Creator',
    'date': 'ModificationDate',
    'issued': 'EffectiveDate',
    'created': 'CreationDate',
    'rights': 'Rights',
    'language': 'Language',
    'contributor': 'Contributors',
    'source': 'source',
    'relation': 'relation',
    'coverage': 'coverage'}

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

    # DublinCore / metatada information
    metadata_info = {}
    content = object.getContent()
    for key, attr in metadata_map.items():
        meth = getattr(content, attr)
        if callable(meth):
            value = meth()
        else:
            value = meth
        if not value or value is 'None':
            continue
        if not isinstance(value, str):
            value = ', '.join(value)
        metadata_info[key] = value

    rpath = getRelativeUrl(object)

    items.append(
        {'url': object.absolute_url(),
         'rurl': base_url + rpath,
         'rpath': rpath,
         'title': object.title_or_id(),
         'description': content.Description(),
         'icon_tag': renderIcon(ptype, base_url, ''),
         'metadata': metadata_info,
        })

return items
