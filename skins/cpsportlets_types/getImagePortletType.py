image_portlet_type = {
    'title': 'portal_type_ImagePortlet_title',
    'description': 'portal_type_ImagePortlet_description',
    'content_icon': 'image_portlet_icon.png',
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
    'cps_is_portalbox': False,
    'schemas': ('portlet_common','metadata', 'common'),
    'layouts': ('portlet_common', 'image'),
    'flexible_layouts': (),
    'storage_methods': (),
    'cps_is_portlet': True,
    'actions': (
         {'id': 'view',
          'name': 'action_view',
          'action': 'string:${object_url}/cpsportlet_view',
          'condition': '',
          'permission': ('View',),
          'category': 'object',
          'visible': 1,},
         {'id': 'edit',
          'name': 'action_edit',
          'action': 'string:${object_url}/cpsportlet_edit_form',
          'condition': '',
          'permission': ('Modify portal content',),
          'category': 'object',
          'visible': 1,},
    )
}

types = {}
types['Image Portlet'] = image_portlet_type
return types
