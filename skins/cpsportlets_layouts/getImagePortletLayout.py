image_portlet_layout = {
    'widgets': {
        'imagelink': {
            'type': 'Image Link Widget',
            'data': {
                'title': '',
                'fields': ('image', 'link'),
                'widget_ids': ('image', 'link'),
                'widget_type': 'Image Link Widget',
            },
        },
        'image': {
            'type': 'Image Widget',
            'data': {
                'title': '',
                'fields': ('image',),
                'is_required': False,
                'label': '',
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
                'fields': ('link',),
                'is_required': False,
                'label_edit': 'cpsportlets_image_link_label',
                'is_i18n': True,
                'display_width': 36,
                'size_max': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'imagelink', 'ncols': 1},
            ],
        ],
    },
}


layouts = {'image_portlet': image_portlet_layout}
return layouts
