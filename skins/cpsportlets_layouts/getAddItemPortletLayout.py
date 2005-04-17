additem_portlet_layout = {
    'widgets': {
        'portlet': {
            'type': 'Generic Portlet Widget',
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
                'render_method': 'widget_portlet_additem',
                'field_types': ('CPS String Field',),
            },
        },
        'display': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'help': 'cpsportlets_display_mode_help',
                'fields': ('display',),
                'is_required': False,
                'label_edit': 'cpsportlets_display_mode_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'vocabulary': 'cpsportlets_additem_display_voc',
                'translated': True,
            },
        },
        'show_icons': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('show_icons',),
                'label_edit': 'cpsportlets_additem_show_icons_label',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display not in ['standard_menu']",
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
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
            [{'widget_id': 'display', 'ncols': 1},
            ],
            [{'widget_id': 'show_icons', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'additem_portlet': additem_portlet_layout}
return layouts
