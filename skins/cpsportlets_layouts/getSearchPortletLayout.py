search_portlet_layout = {
    'widgets': {
        'search': {
            'type': 'CPS Search Widget',
            'data': {
                'title': '',
                'fields': ('dummy',),
                'is_required': True,
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
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'search', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'search_portlet':search_portlet_layout}
return layouts
