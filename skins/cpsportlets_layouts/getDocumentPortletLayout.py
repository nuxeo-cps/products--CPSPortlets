document_portlet_layout = {
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
                'render_method': 'widget_portlet_document',
                'field_types': ('CPS String Field',),
            },
        },
        'cluster_id': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('cluster_id',),
                'label_edit': 'cpsportlets_document_cluster_id_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'display_width': 36,
                'size_max': 0,
            },
        },
        'render_container': {
            'type': 'CheckBox Widget',
            'data': {
                'fields': ('render_container',),
                'label_edit': 'cpsportlets_document_render_container_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'display_true': 'Yes',
                'display_false': 'No',
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
            [{'widget_id': 'render_container', 'ncols': 1},
             {'widget_id': 'cluster_id', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'document_portlet': document_portlet_layout}
return layouts
