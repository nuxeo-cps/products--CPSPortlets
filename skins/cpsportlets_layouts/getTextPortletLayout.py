text_portlet_layout = {
    'widgets': {
        'text': {
            'type': 'Text Widget',
            'data': {
                'fields': ('text', 'text_format', 'text_position'),
                'hidden_layout_modes': ('view',),
                'width': 50,
                'height': 10,
                'size_max': 0,
                'file_uploader': False,
                'render_format': 'html',
                'render_position': 'normal',
                'configurable': 'format',
            },
        },
        'portlet': {
            'type': 'Generic Portlet Widget',
            'data': {
                'fields': ('portlet',),
                'hidden_layout_modes': ('edit',),
                'render_method': 'widget_portlet_text',
                'field_types': ('CPS String Field',),
            },
        },
        'i18n': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('i18n',),
                'label_edit': 'label_cpsportlets_i18n',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'layout_create_method': '',
        'layout_edit_method': '',
        'layout_view_method': '',
        'flexible_widgets': (),
        'validate_values_expr': '',
        'ncols': 2,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 2},
            ],
            [{'widget_id': 'text', 'ncols': 1},
             {'widget_id': 'i18n', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'text_portlet': text_portlet_layout}
return layouts
