##parameters=REQUEST, layout_id=None
# $Id$
"""
edit layout and content if form submited

return html renderer + psm
"""
doc = context.getContent()

layout_changed = context.editLayouts(REQUEST=REQUEST);

if layout_changed or REQUEST.has_key('cpsdocument_edit_button'):
    request = REQUEST
    psm = 'psm_content_changed'
else:
    request = None
    psm = ''

res = doc.renderEditDetailed(request=request, proxy=context,
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


return res[0], psm
