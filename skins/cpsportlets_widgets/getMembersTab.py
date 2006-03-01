##parameters=REQUEST=None, **kw
# $Id$
"""
Get the members tab used by the navigation portlet without using the
portal_trees and CPSNavigation.
"""

item = []

if REQUEST is not None:
    kw.update(REQUEST.form)
else:
    REQUEST=context.REQUEST

utool = context.portal_url
pmtool = context.portal_membership
checkPerm = pmtool.checkPermission
base_url = utool.getBaseUrl()
mcat = context.translation_service

context_rpath = kw.get('context_rpath')

current_uid = context_rpath

renderIcon = context.portal_cpsportlets.renderIcon

members = pmtool.getMembersFolder()
homeFolder = pmtool.getHomeFolder()
# translatable title
label = 'My stuff'

# if user has rights to view the members folder, this will be the private space
if checkPerm('View', members):
    homeFolder = members
    label = 'label_private_spaces'
if not homeFolder:
    return []

url = homeFolder.absolute_url(relative=1)
if not url.startswith('/'):
    url = '/' + url

rpath = utool.getRpathFromPath(url)
# XXX maybe this should not be hardcoded
depth = 0
selected_tab = (current_uid + '/').startswith(rpath + '/')
# XXX hardcoded for now
visible = True
ptype = homeFolder.portal_type
description = title = mcat(label)

item.append({'url': url,
             'title': title,
             'depth': depth,
             'selected_tab': selected_tab,
             'icon_tag': renderIcon(ptype, base_url, ''),
             'description': description,
             'visible': visible,
            })

return item
