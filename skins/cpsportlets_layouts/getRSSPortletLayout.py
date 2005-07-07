rss_portlet_layout = {
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
                'render_method': 'widget_portlet_rss',
                'field_types': ('CPS String Field',),
            },
        },
        'link_string': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('link_string',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_common_link_string_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': 'context/render_method',
                'css_class': '',
                'widget_mode_expr': '',
                'display_width': 20,
                'size_max': 0,
            },
        },
        'first_item': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('first_item',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_common_first_item_label',
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
                'is_limited': True,
                'min_value': 1.0,
                'max_value': 15.0,
                'thousands_separator': '',
            },
        },
        'max_items': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('max_items',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_common_max_items_label',
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
                'min_value': 1.0,
                'max_value': 15.0,
                'thousands_separator': '',
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
                'hidden_if_expr': 'context/render_method',
                'css_class': '',
                'widget_mode_expr': '',
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'render_method': {
            'type': 'String Widget',
            'data': {
                'fields': ('render_method',),
                'label_edit': 'cpsportlets_common_render_method_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_if_expr': '',
                'display_width': 30,
            },
        },
        'cache_timeout': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('cache_timeout',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_rss_update_frequency_label',
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
        'channel': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'fields': ('channel',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_rss_channel_label',
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
                'vocabulary': 'cpsportlets_rss_channels_voc',
                'translated': False,
            },
        },
        'max_words': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('max_words',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_rss_max_words_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': 'context/render_method',
                'css_class': '',
                'widget_mode_expr': '',
                'is_limited': False,
                'min_value': 0.0,
                'max_value': 0.0,
                'thousands_separator': '',
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
                'translated': True,
                'size': 0,
            },
        },
        'short_syndication_formats': {
            'type': 'CheckBox Widget',
            'data': {
                'fields': ('short_syndication_formats',),
                'label_edit': 'cpsportlets_common_short_syndication_formats_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'widget_mode_expr': '',
                'display_true': 'Yes',
                'display_false': 'No',
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
            [{'widget_id': 'channel', 'ncols': 1},
            ],
            [{'widget_id': 'cache_timeout', 'ncols': 1},
            ],
            [{'widget_id': 'render_method', 'ncols': 1},
            ],
            [{'widget_id': 'display_description', 'ncols': 1},
            ],
            [{'widget_id': 'first_item', 'ncols': 1},
            ],
            [{'widget_id': 'max_items', 'ncols': 1},
            ],
            [{'widget_id': 'max_words', 'ncols': 1},
            ],
            [{'widget_id': 'link_string', 'ncols': 1},
            ],
            [{'widget_id': 'syndication_formats', 'ncols': 1},
             {'widget_id': 'short_syndication_formats', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'rss_portlet':rss_portlet_layout}
return layouts
