
cache_params = {
    'Dummy Portlet': [],
    'Text Portlet': [],
    'Search Portlet': ['no-cache'],
    'Internal Links Portlet': ['object:path'],
    'Add Item Portlet': ['portal_type', 'wf_create'],
    'Breadcrumbs Portlet': ['user',
        'object:published_path',
        'objects:relative_path'
        ],
    'Actions Portlet': ['actions:(categories)'],
    'Content Portlet': ['user', 
        'event_ids:workflow_publish,workflow_modify,sys_del_object',
        'event_in_folders:(folder_path)',
        'event_on_types:(searchable_types)',
        ],
    'Language Portlet': ['object:path,langs', 'current_lang'],
    'Image Portlet': [],
    'Navigation Portlet': ['no-cache'],
    'Document Portlet': ['no-cache'],
}

return cache_params
