document_portlet_layout = {
    'widgets': {
        'document': {
            'type': 'CPS Document Widget',
            'data': {
                'title': '',
                'fields': ('dummy',),
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
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'document', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'document_portlet': document_portlet_layout}
return layouts