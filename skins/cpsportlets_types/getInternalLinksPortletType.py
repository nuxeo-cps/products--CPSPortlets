internal_links_portlet_type = {
    'title': 'portal_type_InternalLinksPortlet_title',
    'description': '',
    'content_icon': 'internallinks_portlet_icon.png',
    'content_meta_type': 'CPS Portlet',
    'product': 'CPSPortlets',
    'factory': 'addCPSPortlet',
    'immediate_view': 'cpsportlet_view',
    'global_allow': True,
    'filter_content_types': True,
    'allowed_content_types': (),
    'allow_discussion': False,
    'cps_is_searchable': True,
    'cps_proxy_type': '',
    'cps_display_as_document_in_listing': False,
    'schemas': ('portlet_common', 'internallinks_portlet'),
    'layouts': ('portlet_common', 'internallinks_portlet',),
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
    )
}

types = {'Internal Links Portlet': internal_links_portlet_type}

return types
