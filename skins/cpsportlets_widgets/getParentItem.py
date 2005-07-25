mtool = context.portal_membership
utool = context.portal_url
base_url = utool.getBaseUrl()

rpath = utool.getRelativeContentPath(context)
parent = context

while rpath:
    rpath = rpath[:-1]
    if rpath:
        parent = context.restrictedTraverse(rpath, default=None)
    else:
        parent = utool.getPortalObject()
        
    if parent is not None \
    and mtool.checkPermission('List folder contents', parent):
        break

try:
    ti = parent.getTypeInfo()
except AttributeError:
    return None

icon_tag = ''
if ti is not None:
    ptltool = context.portal_cpsportlets
    icon_tag = ptltool.renderIcon(ti.getId(), base_url, '')

return {'url':  base_url + '/'.join(rpath),
    'title': parent.title_or_id(),
    'icon': icon_tag,
    }
