image_portlet_layout = {
    'widgets': {
        'imagelink': {
            'type': 'Image Link Widget',
            'data': {
                'title': '',
                'fields': ('image', 'link'),
                'widget_ids': ('image', 'link'),
                'widget_type': 'Image Link Widget',
                'is_required': False,
                'label': '',
                'label_edit': '',
                'description': '',
                'help': '',
                'is_i18n': False,
                'readonly_layout_modes': (),
                'hidden_layout_modes': (),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'widget_group_id': '',
                'depends_on_field_id': '',
                'depends_on_field_value': '',
                'display_if_depends_equals': True,
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
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': (),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'widget_group_id': '',
                'depends_on_field_id': '',
                'depends_on_field_value': '',
                'display_if_depends_equals': True,
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
                'label': '',
                'label_edit': 'cpsportlets_image_link_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': (),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'widget_group_id': '',
                'depends_on_field_id': '',
                'depends_on_field_value': '',
                'display_if_depends_equals': True,
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
