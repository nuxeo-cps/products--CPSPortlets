internallinks_portlet_layout = {
    'widgets': {
        'links': {
            'type': 'InternalLinks Widget',
            'data': {
                'fields': ('links',),
                'label_edit': 'cpsportlets_internallinks_links_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'size': 0,
            },
        },
        'portlet': {
            'type': 'Generic Portlet Widget',
            'data': {
                'fields': ('portlet',),
                'hidden_layout_modes': ('edit',),
                'render_method': 'widget_portlet_internallinks',
                'field_types': ('CPS String Field',),
            },
        },
        'max_title_words': {
            'type': 'Int Widget',
            'data': {
                'fields': ('max_title_words',),
                'label_edit': 'cpsportlets_internallinks_max_title_words_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'min_value': 0.0,
                'max_value': 0.0,
                'thousands_separator': '',
            },
        },
        'show_icons': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('show_icons',),
                'label_edit': 'cpsportlets_internallinks_show_icons_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'display_description': {
            'type': 'Boolean Widget',
            'data': {
                'title': '',
                'fields': ('display_description',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_common_display_description_label',
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
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'syndication_formats': {
            'type': 'MultiSelect Widget',
            'data': {
                'fields': ('syndication_formats',),
                'label_edit': 'cpsportlets_common_syndication_formats_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'vocabulary': 'cpsportlets_syndication_formats_voc',
                'size': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'validate_values_expr': '',
        'ncols': 2,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 2},
            ],
            [{'widget_id': 'max_title_words', 'ncols': 1},
             {'widget_id': 'show_icons', 'ncols': 1},
             {'widget_id': 'display_description', 'ncols': 1},
            ],
            [{'widget_id': 'links', 'ncols': 2},
            ],
            [{'widget_id': 'syndication_formats', 'ncols': 3},
            ],
        ],
    },
}

layouts = {'internallinks_portlet': internallinks_portlet_layout}

return layouts
