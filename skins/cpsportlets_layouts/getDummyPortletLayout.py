dummy_portlet_layout = {
    'widgets': {
        'portlet': {
            'type': 'CPS Portlet Dummy Widget',
            'data': {
                'title': '',
                'fields': ('portlet',),
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
                'display_width': 20,
                'size_max': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'dummy_portlet': dummy_portlet_layout}

return layouts
