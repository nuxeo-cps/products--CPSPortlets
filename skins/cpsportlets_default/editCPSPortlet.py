##parameters=REQUEST, layout_id=None
# $Id$
"""
edit layout and content if form submited

return html renderer + psm
"""

ptl_tool = context.portal_cpsportlets

# Get portlet_id form the templet
portlet_id = context.getPortletId()

# Get the portlet from the tool
doc = ptl_tool.getPortletById(portlet_id)

layout_changed = doc.editLayouts(REQUEST=REQUEST);

if layout_changed or REQUEST.has_key('cpsdocument_edit_button'):
    request = REQUEST
    psm = 'psm_content_changed'
else:
    request = None
    psm = ''

res = doc.renderEditDetailed(request=request, proxy=doc,
                             layout_id=layout_id)

if not res[1]:
    psm = 'psm_content_error'
else:
    # XXX
    # Has to be handled in here since the workflow doesn't take care
    # of that yet.
    context.portal_eventservice.notifyEvent('workflow_modify',
                                            context,
                                            {})

if REQUEST is not None:
    redirect_url = context.absolute_url() + \
                   '/edit_form/?' + \
                   REQUEST.get('QUERY_STRING') + \
                   '?portal_status_message=' + \
                   psm
    return REQUEST.RESPONSE.redirect(redirect_url)
