
cache_params = {
    'Dummy Portlet': [],
    'Text Portlet': [],
    'Search Portlet': ['no-cache'],
    'Internal Links Portlet': ['object:path'],
    'Add Item Portlet': ['portal_type', 'wf_create'],
    'Breadcrumbs Portlet': ['object:published_path', 'user',
                            'objects:relative_path'],
    'Actions Portlet': ['actions:(categories)'],
    'Content Portlet': ['no-cache'],
    'Language Portlet': ['object:path,langs', 'current_lang'],
    'Image Portlet': [],
    'Navigation Portlet': ['no-cache'],
}

return cache_params
