document_portlet_schema = {
    'cluster_id': {
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
    'render_container': {
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
    'cluster_no_fallback': {
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

schemas = {'document_portlet': document_portlet_schema}
return schemas
