##parameters=ptype_id=None

if ptype_id is None:
    return []

cache_params_dict = {
    'Dummy Portlet': [],
    'Search Portlet': [],
    'Internal Links Portlet': ['folder'],
    'Add Item Portlet': ['folder'],
    'Breadcrumbs Portlet': ['folder', 'user'],
}

return cache_params_dict.get(ptype_id, [])
