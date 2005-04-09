content_portlet_layout = {
    'widgets': {
        'link_string': {
            'type': 'String Widget',
            'data': {
                'fields': ('link_string',),
                'label_edit': 'cpsportlets_common_link_string_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'display_width': 36,
            },
        },
        'query_title': {
            'type': 'String Widget',
            'data': {
                'fields': ('query_title',),
                'label_edit': 'cpsportlets_content_query_title_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'display_width': 36,
            },
        },
        'folder_path': {
            'type': 'String Widget',
            'data': {
                'fields': ('folder_path',),
                'label_edit': 'cpsportlets_content_folder_path_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'display_width': 36,
            },
        },
        'sort_on': {
            'type': 'Select Widget',
            'data': {
                'fields': ('sort_on',),
                'label_edit': 'cpsportlets_content_sort_on_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_if_expr': "python: context.search_type in ['last_modified', 'upcoming']",
                'vocabulary': 'cpsportlets_content_sort_on_voc',
                'translated': True,
            },
        },
        'max_items': {
            'type': 'Int Widget',
            'data': {
                'fields': ('max_items',),
                'label_edit': 'cpsportlets_common_max_items_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'is_limited': True,
                'min_value': 1.0,
                'max_value': 20.0,
            },
        },
        'search_type': {
            'type': 'Select Widget',
            'data': {
                'fields': ('search_type',),
                'label_edit': 'cpsportlets_content_search_type_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'vocabulary': 'cpsportlets_content_search_voc',
                'translated': True,
            },
        },
        'render_items': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('render_items',),
                'label_edit': 'cpsportlets_content_render_items_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'portlet': {
            'type': 'Generic Portlet Widget',
            'data': {
                'fields': ('portlet',),
                'hidden_layout_modes': ('edit',),
                'render_method': 'widget_portlet_content',
                'field_types': ('CPS String Field',),
            },
        },
        'cluster_id': {
            'type': 'String Widget',
            'data': {
                'fields': ('cluster_id',),
                'label_edit': 'cpsportlets_content_cluster_id_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_if_expr': 'not:context/render_items',
                'display_width': 20,
            },
        },
        'display_description': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('display_description',),
                'label_edit': 'cpsportlets_common_display_description_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_if_expr': 'context/render_items',
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'sort_reverse': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('sort_reverse',),
                'label_edit': 'cpsportlets_content_sort_reverse_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'searchable_types': {
            'type': 'MultiSelect Widget',
            'data': {
                'fields': ('searchable_types',),
                'label_edit': 'cpsportlets_content_searchable_types_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'vocabulary': 'cpsportlets_content_portal_types_voc',
                'translated': True,
                'size': 7,
            },
        },
        'max_words': {
            'type': 'Int Widget',
            'data': {
                'fields': ('max_words',),
                'label_edit': 'cpsportlets_content_max_words_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_if_expr': 'context/render_items',
                'min_value': 0.0,
                'max_value': 0.0,
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
        'ncols': 3,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 3},
            ],
            [{'widget_id': 'render_items', 'ncols': 1},
             {'widget_id': 'cluster_id', 'ncols': 1},
             {'widget_id': 'max_items', 'ncols': 1},
            ],
            [{'widget_id': 'search_type', 'ncols': 1},
             {'widget_id': 'sort_on', 'ncols': 1},
             {'widget_id': 'sort_reverse', 'ncols': 1},
            ],
            [{'widget_id': 'query_title', 'ncols': 2},
             {'widget_id': 'folder_path', 'ncols': 1},
            ],
            [{'widget_id': 'searchable_types', 'ncols': 3},
            ],
            [{'widget_id': 'display_description', 'ncols': 2},
             {'widget_id': 'max_words', 'ncols': 1},
            ],
            [{'widget_id': 'link_string', 'ncols': 3},
            ],
            [{'widget_id': 'syndication_formats', 'ncols': 1},
             {'widget_id': 'short_syndication_formats', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'content_portlet': content_portlet_layout}
return layouts
