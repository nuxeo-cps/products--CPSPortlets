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
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'additem_portlet': additem_portlet_layout}
return layouts
