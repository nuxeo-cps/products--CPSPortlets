text_portlet_layout = {
    'widgets': {
        'text': {
            'type': 'Text Widget',
            'data': {
                'fields': ('text', 'text_format', 'text_position'),
                'width': 50,
                'height': 10,
                'size_max': 0,
                'render_position': 'normal',
                'render_format': 'html',
                'configurable': 'format',
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'validate_values_expr': '',
        'ncols': 1,
        'rows': [
            [{'widget_id': 'text', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'text_portlet': text_portlet_layout}
return layouts
