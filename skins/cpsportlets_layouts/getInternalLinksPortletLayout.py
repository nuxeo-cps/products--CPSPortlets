internallinks_portlet_layout = {
    'widgets': {
        'links': {
            'type': 'InternalLinks Widget',
            'data': {
                'title': '',
                'fields': ('links',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_internallinks_links_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': (),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'new_window': False,
                'size': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'links', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'internallinks_portlet': internallinks_portlet_layout}

return layouts
