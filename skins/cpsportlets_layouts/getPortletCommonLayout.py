portlet_common_layout = {
    'widgets': {
        'title': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('title',),
                'is_required': False,
                'label': '',
                'label_edit': 'label_cpsportlets_title',
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
                'display_width': 36,
                'size_max': 36,
            },
        },
        'i18n': {
            'type': 'CheckBox Widget',
            'data': {
                'title': '',
                'fields': ('i18n',),
                'is_required': False,
                'label': '',
                'label_edit': 'label_cpsportlets_i18n',
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
                'display_true': 'cpsschemas_label_true',
                'display_false': 'cpsschemas_label_false',
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'title', 'ncols': 1},
            ],
            [{'widget_id': 'i18n', 'ncols': 1},
            ],
        ],
    },
}


layouts = {'portlet_common': portlet_common_layout}
return layouts
