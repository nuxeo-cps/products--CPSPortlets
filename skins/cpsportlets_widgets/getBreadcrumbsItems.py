##parameters=**kw
# $Id$

REQUEST = context.REQUEST
# XXX: Document what the breadcrumb_set is for !
breadcrumb_set = REQUEST.get('breadcrumb_set')
if breadcrumb_set != None:
    return breadcrumb_set

utool = context.portal_url

# Display options
parent = int(kw.get('parent', 0))
display_hidden_folders = int(kw.get('display_hidden_folders', 1))
display_site_root = int(kw.get('display_site_root', 1))
first_item = int(kw.get('first_item', 0))

# Compute the breadcrumbs
base_url = utool.getBaseUrl()
portal = utool.getPortalObject()
items = utool.getBreadCrumbsInfo(context=context, only_parents=parent,
                                 restricted=True,
                                 show_hidden_folders=display_hidden_folders,
                                 first_item=first_item)
return items
