navigation_portlet_layout = {
    'widgets': {
        'dummy': {
            'type': 'CPS Navigation Widget',
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
        'display': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'fields': ('display',),
                'is_required': False,
                'label': '',
                'label_edit': '',
                'description': '',
                'help': '',
                'is_i18n': False,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'vocabulary': 'cpsportlet_navigation_display_voc',
                'translated': True,
            },
        },
        'rel_depth': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('rel_depth',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_navigation_rel_depth_label',
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
                'is_limited': False,
                'min_value': 0.0,
                'max_value': 0.0,
                'thousands_separator': '',
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'dummy', 'ncols': 1},
            ],
            [{'widget_id': 'display', 'ncols': 1},
            ],
            [{'widget_id': 'rel_depth', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'navigation_portlet': navigation_portlet_layout}
return layouts