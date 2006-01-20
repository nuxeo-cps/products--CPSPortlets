rss_portlet_type = {
    'title': 'portal_type_RSSPortlet_title',
    'description': 'portal_type_RSSPortlet_description',
    'content_icon': 'rss_portlet_icon.png',
    'content_meta_type': 'CPS Portlet',
    'product': 'CPSPortlets',
    'factory': 'addCPSPortlet',
    'immediate_view': 'cpsportlet_edit_form',
    'global_allow': False,
    'filter_content_types': False,
    'allowed_content_types': (),
    'allow_discussion': False,
    'cps_is_searchable': False,
    'cps_proxy_type': '',
    'cps_display_as_document_in_listing': False,
    'schemas': ('portlet_common', 'rss_portlet', 'common', 'metadata'),
    'layouts': ('portlet_common', 'rss_portlet'),
    'layout_clusters': ('metadata:metadata',),
    'flexible_layouts': (),
    'storage_methods': (),
    'cps_is_portlet': True,
    'actions': (
         {'id': 'create',
          'name': 'action_create',
          'action': 'string:${object_url}/cpsportlet_create_form',
          'condition': '',
          'permission': ('Manage Portlets',),
          'category': 'object',
          'visible': False,},
         {'id': 'edit',
          'name': 'action_edit',
          'action': 'string:${object_url}/cpsportlet_edit_form',
          'condition': '',
          'permission': ('Manage Portlets',),
          'category': 'object',
          'visible': False,},
         {'id': 'view',
          'name': 'action_view',
          'action': 'string:${object_url}/render',
          'condition': '',
          'permission': ('View',),
          'category': 'object',
          'visible': False,},
         {'id': 'metadata',
          'name': 'action_metadata',
          'action': 'string:${object_url}/cpsportlet_metadata',
          'condition': '',
          'permission': ('Manage Portlets',),
          'category': 'object',
          'visible': 0,},
    )
}

types = {'RSS Portlet': rss_portlet_type}
return types
