
cache_params = {
    'Dummy Portlet': ['user'],
    'Custom Portlet': [],
    'Text Portlet': [],
    'Search Portlet': ['no-cache'],
    'Internal Links Portlet': ['user',
        'current_lang',
        'objects:(links)'
        ],
    'Add Item Portlet': ['portal_type', 'wf_create', 'current_lang'],
    'Breadcrumbs Portlet': ['user',
        'current_lang',
        'object:published_path',
        'objects:relative_path',
        'timeout:300',
        ],
    'Actions Portlet': ['actions:(categories)', 'current_lang'],
    'Content Portlet': ['user',
        'event_ids:workflow_create,workflow_publish,workflow_modify,sys_del_object,workflow_cut_copy_paste,workflow_copy_submit',
        'event_in_folders:(folder_path)',
        'event_on_types:(searchable_types)',
        'baseurl',
        ],
    'Language Portlet': ['object:path,langs,lang', 'current_lang'],
    'Image Portlet': ['baseurl'],
    'Rotating Image Portlet': ['baseurl'],
    'Navigation Portlet': ['no-cache'],
    'Document Portlet': ['no-cache'],
    'RSS Portlet': ['event_ids:rss_channel_refresh','timeout:10'],
}

return cache_params
