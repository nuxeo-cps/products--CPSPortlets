##parameters=
"""Return portlet widgets
"""

widgets = {
    'CPS Portlet Dummy Widget': {
    'type': 'CPS Portlet Dummy Widget Type',
    'data': {},
    },
    'Generic Portlet Widget': {
    'type': 'CPS Generic Portlet Widget Type',
    'data': {},
    },
    'Image Link Widget': {
        'type': 'CPS Compound Widget Type',
        'data': {
            'prepare_validate_method': 'widget_imagelink_prepare_validate',
            'render_method': 'widget_imagelink_render',
        },
    },
}

return widgets
