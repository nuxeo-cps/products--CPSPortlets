dummy_portlet_type = {
    'title': 'portal_type_DummyPortlet_title',
    'description': '',
    'content_icon': 'portlet_icon.gif',
    'content_meta_type': 'CPS Portlet',
    'product': 'CPSPortlets',
    'factory': 'addCPSPortlet',
    'immediate_view': 'cpsportlet_view',
    'global_allow': True,
    'filter_content_types': True,
    'allowed_content_types': (),
    'allow_discussion': False,
    'cps_is_searchable': True,
    'cps_proxy_type': 'document',
    'cps_display_as_document_in_listing': False,
    'schemas': ('portlet_common', 'dummy_portlet'),
    'layouts': ('dummy_portlet',),
    'flexible_layouts': (),
    'storage_methods': (),
    'cps_is_portlet': True,
    'actions': (
    )
}

types = {'Dummy Portlet': dummy_portlet_type}

return types
