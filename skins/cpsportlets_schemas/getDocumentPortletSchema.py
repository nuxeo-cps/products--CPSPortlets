document_portlet_schema = {
    'layout_ids': {
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
            'read_process_dependent_fields': [],
            'write_ignore_storage': 0,
            'write_process_expr': '',
        },
    },
}

schemas = {'document_portlet': document_portlet_schema}
return schemas
