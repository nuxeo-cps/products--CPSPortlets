image_portlet_layout = {
    'widgets': {
        'image': {
            'type': 'Image Widget',
            'data': {
                'title': '',
                'fields': ('?',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_image_image_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'deletable': True,
                'size_max': 2097152,
                'display_width': 0,
                'display_height': 0,
                'allow_resize': True,
            },
        },
        'portlet': {
            'type': 'Generic Portlet Widget',
            'data': {
                'fields': ('portlet',),
                'render_method': 'widget_portlet_image',
                'field_types': ('CPS String Field',),
            },
        },
        'link': {
            'type': 'String Widget',
            'data': {
                'fields': ('?',),
                'is_required': False,
                'label_edit': 'cpsportlets_image_link_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'display_width': 36,
                'size_max': 0,
            },
        },
        'imagelink': {
            'type': 'Image Link Widget',
            'data': {
                'fields': ('?',),
                'widget_ids': ('image', 'link'),
                'widget_type': 'Image Link Widget',
                'hidden_layout_modes': ('view',),
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': ('imagelink',),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'image_portlet': image_portlet_layout}
return layouts
