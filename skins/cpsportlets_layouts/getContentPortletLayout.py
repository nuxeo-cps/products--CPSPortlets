content_portlet_layout = {
    'widgets': {
        'content': {
            'type': 'CPS Content Widget',
            'data': {
                'title': '',
                'fields': ('content',),
                'is_required': False,
                'label': '',
                'label_edit': '',
                'description': '',
                'help': '',
                'is_i18n': False,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('edit',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
            },
        },
        'search_type': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'fields': ('search_type',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_content_search_type_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'vocabulary': 'cpsportlets_content_search_voc',
                'translated': True,
            },
        },
        'sort_on': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'fields': ('sort_on',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_content_sort_on_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'vocabulary': 'cpsportlets_content_sort_on_voc',
                'translated': True,
            },
        },
        'sort_reverse': {
            'type': 'Boolean Widget',
            'data': {
                'title': '',
                'fields': ('sort_reverse',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_content_sort_reverse_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
            },
        },
        'max_items': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('max_items',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_content_max_items_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'is_limited': True,
                'min_value': 1.0,
                'max_value': 20.0,
                'thousands_separator': '',
            },
        },
        'folder_path': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('folder_path',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_content_folder_path_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'display_width': 40,
                'size_max': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 3,
        'rows': [
            [{'widget_id': 'content', 'ncols': 3},
            ],
            [{'widget_id': 'search_type', 'ncols': 3},
            ],
            [{'widget_id': 'max_items', 'ncols': 1},
             {'widget_id': 'sort_on', 'ncols': 1},
             {'widget_id': 'sort_reverse', 'ncols': 1},
            ],
            [{'widget_id': 'folder_path', 'ncols': 3},
            ],
        ],
    },
}


layouts = {'content_portlet': content_portlet_layout}
return layouts
