
cache_params = {
    'Dummy Portlet': ['user'],
    'Custom Portlet': ['no-cache'],
    'Text Portlet': [],
    'Search Portlet': ['no-cache'],
    'Internal Links Portlet': ['no-cache'],
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
    'Language Portlet': ['object:path,langs,current_lang', 'current_lang'],
    'Image Portlet': ['no-cache'],
    'Navigation Portlet': ['no-cache'],
    'Document Portlet': ['no-cache'],
    'RSS Portlet': ['event_ids:rss_channel_refresh','timeout:10'],
}

return cache_params
