portlet_common_layout = {
    'widgets': {
        'Title': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('Title',),
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
        'Description': {
            'type': 'TextArea Widget',
            'data': {
                'title': '',
                'fields': ('Description',),
                'is_required': False,
                'label': '',
                'label_edit': 'label_description',
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
                'width': 40,
                'height': 2,
                'render_format': 'text',
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 3,
        'rows': [
            [{'widget_id': 'Title', 'ncols': 3},
            ],
            [{'widget_id': 'Description', 'ncols': 3},
            ],
        ],
    },
}

layouts = {'portlet_common': portlet_common_layout}
return layouts
