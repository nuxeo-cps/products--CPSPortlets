custom_portlet_layout = {
    'widgets': {
        'render_method': {
            'type': 'String Widget',
            'data': {
                'fields': ('render_method',),
                'is_required': True,
                'label_edit': 'cpsportlets_custom_render_method_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'display_width': 36,
                'size_max': 0,
            },
        },
        'portlet': {
            'type': 'CPS Portlet Custom Widget',
            'data': {
                'fields': ('portlet',),
                'hidden_layout_modes': ('edit',),
                'display_width': 20,
                'size_max': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 1},
            ],
            [{'widget_id': 'render_method', 'ncols': 1},
            ],
        ],
    },
}


layouts = {'custom_portlet': custom_portlet_layout}
return layouts
