breadcrumbs_portlet_layout = {
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
                'depends_on_field_id': '',
                'depends_on_field_value': '',
                'display_if_depends_equals': True,
                'render_method': 'widget_portlet_breadcrumbs',
                'field_types': ('CPS String Field',),
            },
        },
        'display': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'fields': ('display',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_display_mode_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'depends_on_field_id': '',
                'depends_on_field_value': '',
                'display_if_depends_equals': True,
                'vocabulary': 'cpsportlets_bcs_display_voc',
                'translated': True,
            },
        },
        'display_hidden_folders': {
            'type': 'Boolean Widget',
            'data': {
                'title': '',
                'fields': ('display_hidden_folders',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_display_hidden_folders_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'depends_on_field_id': '',
                'depends_on_field_value': '',
                'display_if_depends_equals': True,
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'first_item': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('first_item',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_common_first_item_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': '',
                'css_class': '',
                'widget_mode_expr': '',
                'depends_on_field_id': '',
                'depends_on_field_value': '',
                'display_if_depends_equals': False,
                'is_limited': False,
                'min_value': 0.0,
                'max_value': 0.0,
                'thousands_separator': '',
            },
        },
        'display_site_root': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('display_site_root',),
                'label_edit': 'cpsportlets_bcs_display_site_root_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_if_expr': 'python: context.first_item <= 0',
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'highlight_last_item': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('highlight_last_item',),
                'label_edit': 'cpsportlets_bcs_highlight_last_item_label',
                'is_i18n': True,
                'hidden_if_expr': "python: context.display in ['dropdown_list']",
                'hidden_layout_modes': ('view',),
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'ncols': 1,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 2},
            ],
            [{'widget_id': 'display', 'ncols': 2},
            ],
            [{'widget_id': 'first_item', 'ncols': 1},
             {'widget_id': 'display_site_root', 'ncols': 1},
             {'widget_id': 'highlight_last_item', 'ncols': 1},
            ],
            [{'widget_id': 'display_hidden_folders', 'ncols': 2},
            ],
        ],
    },
}

layouts = {'breadcrumbs_portlet': breadcrumbs_portlet_layout}
return layouts
