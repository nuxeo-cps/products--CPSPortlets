portlet_common_layout = {
    'widgets': {
        'title': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('title',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_title_label_edit',
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
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'title', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'portlet_common': portlet_common_layout}
return layouts
