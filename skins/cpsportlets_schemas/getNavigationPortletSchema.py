navigation_portlet_schema = {
    'dummy': {
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
    'display': {
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
    'rel_depth': {
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
            'read_process_dependent_fields': [],
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
}

schemas = {'navigation_portlet': navigation_portlet_schema}
return schemas