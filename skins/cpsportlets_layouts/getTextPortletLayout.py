text_portlet_layout = {
    'widgets': {
        'text': {
            'type': 'Rich Text Editor Widget',
            'data': {
                'title': '',
                'fields': ('text',),
                'is_required': False,
                'label': '',
                'label_edit': '',
                'description': '',
                'help': '',
                'is_i18n': False,
                'readonly_layout_modes': (),
                'hidden_layout_modes': (),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'width': 40,
                'height': 5,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'text', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'text_portlet': text_portlet_layout}
return layouts
