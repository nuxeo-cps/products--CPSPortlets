language_portlet_layout = {
    'widgets': {
        'language': {
            'type': 'Generic Portlet Widget',
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
                'render_method': 'widget_portlet_language',
                'field_types': ('CPS String Field',),
            },
        },
        'action': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'fields': ('action',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_language_action_label',
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
                'vocabulary': 'cpsportlets_language_action_voc',
                'translated': True,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'language', 'ncols': 1},
            ],
            [{'widget_id': 'action', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'language_portlet': language_portlet_layout}
return layouts
