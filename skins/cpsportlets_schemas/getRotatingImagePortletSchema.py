rotating_image_portlet_flexible_schema = {
}

rotating_image_portlet_schema = {
    'nb_images': {
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
}

schemas = {
    'rotating_image_portlet': rotating_image_portlet_schema,
    'rotating_image_portlet_flexible': rotating_image_portlet_flexible_schema,
    }
return schemas
