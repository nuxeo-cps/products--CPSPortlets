content_portlet_schema = {
    'search_type': {
        'type': 'CPS String Field',
        'data': {
            'default_expr': 'string:',
            'is_searchabletext': 0,
            'acl_read_permissions': '',
            'acl_read_roles': '',
            'acl_read_expr': '',
            'acl_write_permissions': '',
            'acl_write_roles': '',
            'acl_write_expr': '',
            'read_ignore_storage': 0,
            'read_process_expr': '',
            'read_process_dependent_fields': (),
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
    'sort_on': {
        'type': 'CPS String Field',
        'data': {
            'default_expr': 'string:',
            'is_searchabletext': 0,
            'acl_read_permissions': '',
            'acl_read_roles': '',
            'acl_read_expr': '',
            'acl_write_permissions': '',
            'acl_write_roles': '',
            'acl_write_expr': '',
            'read_ignore_storage': 0,
            'read_process_expr': '',
            'read_process_dependent_fields': (),
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
    'max_items': {
        'type': 'CPS Int Field',
        'data': {
            'default_expr': 'python:1',
            'is_searchabletext': False,
            'acl_read_permissions': '',
            'acl_read_roles': '',
            'acl_read_expr': '',
            'acl_write_permissions': '',
            'acl_write_roles': '',
            'acl_write_expr': '',
            'read_ignore_storage': False,
            'read_process_expr': '',
            'read_process_dependent_fields': (),
            'write_ignore_storage': False,
            'write_process_expr': '',
        },
    },
    'content': {
        'type': 'CPS String Field',
        'data': {
            'default_expr': 'string:',
            'is_searchabletext': 0,
            'acl_read_permissions': '',
            'acl_read_roles': '',
            'acl_read_expr': '',
            'acl_write_permissions': '',
            'acl_write_roles': '',
            'acl_write_expr': '',
            'read_ignore_storage': 0,
            'read_process_expr': '',
            'read_process_dependent_fields': (),
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
    'sort_reverse': {
        'type': 'CPS Int Field',
        'data': {
            'default_expr': 'python:0',
            'is_searchabletext': 0,
            'acl_read_permissions': '',
            'acl_read_roles': '',
            'acl_read_expr': '',
            'acl_write_permissions': '',
            'acl_write_roles': '',
            'acl_write_expr': '',
            'read_ignore_storage': 0,
            'read_process_expr': '',
            'read_process_dependent_fields': (),
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
    'review_state': {
        'type': 'CPS String List Field',
        'data': {
            'default_expr': 'python:[]',
            'is_searchabletext': 0,
            'acl_read_permissions': '',
            'acl_read_roles': '',
            'acl_read_expr': '',
            'acl_write_permissions': '',
            'acl_write_roles': '',
            'acl_write_expr': '',
            'read_ignore_storage': 0,
            'read_process_expr': '',
            'read_process_dependent_fields': (),
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
    'folder_path': {
        'type': 'CPS String Field',
        'data': {
            'default_expr': 'string:',
            'is_searchabletext': 0,
            'acl_read_permissions': '',
            'acl_read_roles': '',
            'acl_read_expr': '',
            'acl_write_permissions': '',
            'acl_write_roles': '',
            'acl_write_expr': '',
            'read_ignore_storage': 0,
            'read_process_expr': '',
            'read_process_dependent_fields': [],
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
}

schemas = {'content_portlet': content_portlet_schema}
return schemas