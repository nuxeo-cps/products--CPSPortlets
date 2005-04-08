navigation_portlet_layout = {
    'widgets': {
        'show_docs': {
            'type': 'Boolean Widget',
            'data': {
                'title': '',
                'fields': ('show_docs',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_navigation_show_docs_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display not in ['folder_contents', 'collapsible_menu']",
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'display': {
            'type': 'Select Widget',
            'data': {
                'title': '',
                'fields': ('display',),
                'is_required': False,
                'label_edit': 'cpsportlets_display_mode_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'vocabulary': 'cpsportlets_navigation_display_voc',
                'translated': True,
            },
        },
        'rel_depth': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('rel_depth',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_navigation_rel_depth_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display in ['folder_contents', 'subfolder_contents', 'navigation_tree', 'site_map']",
                'is_limited': False,
                'min_value': 0.0,
                'max_value': 0.0,
                'thousands_separator': '',
            },
        },
        'end_depth': {
            'type': 'Int Widget',
            'data': {
                'title': '',
                'fields': ('end_depth',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_navigation_end_depth_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display in ['folder_contents', 'subfolder_contents', 'collapsible_menu']",
                'is_limited': False,
                'min_value': 0.0,
                'max_value': 0.0,
                'thousands_separator': '',
            },
        },
        'contextual': {
            'type': 'Boolean Widget',
            'data': {
                'title': '',
                'fields': ('contextual',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_navigation_contextual_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display in ['vertical_breadcrumbs_menu', 'folder_contents', 'subfolder_contents', 'site_map', 'collapsible_menu']",
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'context_is_portlet': {
            'type': 'CheckBox Widget',
            'data': {
                'title': '',
                'fields': ('context_is_portlet',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_nav_context_is_portlet_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display != 'folder_contents'",
                'css_class': '',
                'widget_mode_expr': '',
                'display_true': 'Yes',
                'display_false': 'No',
            },
        },
        'show_icons': {
            'type': 'Boolean Widget',
            'data': {
                'title': '',
                'fields': ('show_icons',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_navigation_show_icons_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display in ['vertical_breadcrumbs_menu', 'folder_contents', 'subfolder_contents']",
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'authorized_only': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('authorized_only',),
                'label_edit': 'cpsportlets_navigation_authorized_only_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_empty': False,
                'hidden_if_expr':
                    "python: context.display != 'extended_site_map'",
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'display_managers': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('display_managers',),
                'label_edit': 'cpsportlets_navigation_display_managers_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_empty': False,
                'hidden_if_expr':
                    "python: context.display != 'extended_site_map'",
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'display_description': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('display_description',),
                'label_edit': 'cpsportlets_navigation_display_description_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_empty': False,
                'hidden_if_expr':
                    "python: context.display != 'extended_site_map'",
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'display_hidden_folders': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ('display_hidden_folders',),
                'label_edit': 'cpsportlets_navigation_display_hidden_folders_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_empty': False,
                'label_false': 'cpsschemas_label_false',
                'label_true': 'cpsschemas_label_true',
                'render_format': 'select',
            },
        },
        'portlet': {
            'type': 'Generic Portlet Widget',
            'data': {
                'title': '',
                'fields': ('portlet',),
                'hidden_layout_modes': ('edit',),
                'render_method': 'widget_portlet_navigation',
                'field_types': ('CPS String Field',),
            },
        },
        'root_uids': {
            'type': 'Lines Widget',
            'data': {
                'fields': ('root_uids',),
                'label_edit': 'cpsportlets_navigation_root_uids_label',
                'is_i18n': True,
                'hidden_layout_modes': ('view',),
                'hidden_if_expr': "python: context.display in ['vertical_breadcrumbs_menu', 'folder_contents']",
                'width': 40,
                'height': 5,
            },
        },
        'context_rpath': {
            'type': 'String Widget',
            'data': {
                'title': '',
                'fields': ('context_rpath',),
                'is_required': False,
                'label': '',
                'label_edit': 'cpsportlets_nav_context_rpath_label',
                'description': '',
                'help': '',
                'is_i18n': True,
                'readonly_layout_modes': (),
                'hidden_layout_modes': ('view',),
                'hidden_readonly_layout_modes': (),
                'hidden_empty': False,
                'hidden_if_expr': "python: context.display != 'folder_contents' or context.context_is_portlet",
                'widget_mode_expr': '',
                'css_class': '',
                'css_class_expr': '',
                'javascript_expr': '',
                'display_width': 30,
                'size_max': 0,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_portlet_',
        'flexible_widgets': (),
        'ncols': 6,
        'rows': [
            [{'widget_id': 'portlet', 'ncols': 1},
            ],
            [{'widget_id': 'display', 'ncols': 1},
            ],
            [{'widget_id': 'root_uids', 'ncols': 1},
             {'widget_id': 'rel_depth', 'ncols': 1},
             {'widget_id': 'end_depth', 'ncols': 1},
             {'widget_id': 'contextual', 'ncols': 1},
             {'widget_id': 'context_is_portlet', 'ncols': 1},
             {'widget_id': 'context_rpath', 'ncols': 1},
            ],
            [{'widget_id': 'show_docs', 'ncols': 1},
             {'widget_id': 'show_icons', 'ncols': 1},
             {'widget_id': 'display_hidden_folders', 'ncols': 1},
            ],
            [{'widget_id': 'display_managers', 'ncols': 1},
             {'widget_id': 'display_description', 'ncols': 1},
             {'widget_id': 'authorized_only', 'ncols': 1},
            ],
        ],
    },
}

layouts = {'navigation_portlet': navigation_portlet_layout}
return layouts
