##parameters=ptype_id=None

if ptype_id is None:
    return []

cache_params_dict = {
    'Dummy Portlet': [],
    'Search Portlet': ['i18n'],
    'Internal Links Portlet': ['i18n', 'url'],
    'Add Item Portlet': ['i18n', 'url'],
    'Breadcrumbs Portlet': ['i18n', 'url'],
}

return cache_params_dict.get(ptype_id, [])
