mtool = context.portal_membership
utool = context.portal_url

parent = context.aq_inner.aq_parent

if not mtool.checkPermission('List folder contents', parent):
    return None

try:
    ti = parent.getTypeInfo()
except AttributeError:
    return None

icon_tag = ''
if ti is not None:
    ptltool = context.portal_cpsportlets
    base_url = context.REQUEST.get('cpsskins_base_url', '')
    icon_tag = ptltool.renderIcon(ti.getId(), base_url, '')

return {'url': '..',
    'title': parent.title_or_id(),
    'icon': icon_tag,
    }
