actions_portlet_layout = {
    'widgets': {
        'actions': {
            'type': 'CPS Actions Widget',
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
        'categories': {
            'type': 'Lines Widget',
            'data': {
                'title': '',
                'fields': ('categories',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_action_categories_label',
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
                'width': 30,
                'height': 5,
                'format_empty': '',
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'actions', 'ncols': 1},
            ],
            [{'widget_id': 'categories', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'actions_portlet': actions_portlet_layout}
return layouts
