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
                'is_i18n': False,
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
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'content', 'ncols': 1},
            ],
            [{'widget_id': 'search_type', 'ncols': 1},
            ],
        ],
    },
}


layouts = {'content_portlet': content_portlet_layout}
return layouts
