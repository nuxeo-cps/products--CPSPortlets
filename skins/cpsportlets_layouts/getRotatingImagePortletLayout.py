rotating_image_portlet_layout = {
    'widgets': {
        'portlet': {
            'type': 'Generic Portlet Widget',
            'data': {
                'title': '',
                'fields': ('portlet',),
                'hidden_layout_modes': ('edit',),
                'render_method': 'widget_portlet_rotating_image',
                'field_types': ('CPS String Field',),
            },
        },
        'nb_images': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('nb_images',),
                'label_edit': 'cpsportlet_rot_image_nb_images_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'is_limited': False,
                'min_value': 1.0,
                'max_value': 0.0,
                'thousands_separator': '',
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
            [{'widget_id': 'nb_images', 'ncols': 1},
            ],
        ],
    },
}


rotating_image_portlet_flexible_layout = {
    'widgets': {
        'imagelink': {
            'type': 'Image Link Widget',
            'data': {
                'title': '',
                'fields': ('?',),
                'widget_ids': ('image', 'link'),
                'widget_type': 'Image Link Widget',
                'css_class': 'hidden',
            },
        },
        'image': {
            'type': 'Image Widget',
            'data': {
                'title': '',
                'fields': ('?',),
                'is_required': False,
                'label_edit': 'cpsportlets_image_image_label',
                'is_i18n': True,
                'deletable': True,
                'size_max': 4194304,
                'display_width': 0,
                'display_height': 0,
                'allow_resize': False,
            },
        },
        'link': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('?',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_image_link_label',
                'is_i18n': True,
                'display_width': 36,
                'size_max': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_js_',
        'flexible_widgets': ('imagelink',),
        'ncols': 1,
        'rows': [
        ],
    },
}

layouts = {
    'rotating_image_portlet': rotating_image_portlet_layout,
    'rotating_image_portlet_flexible': rotating_image_portlet_flexible_layout,
    }
return layouts
