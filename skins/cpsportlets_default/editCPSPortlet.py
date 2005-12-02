##parameters=REQUEST, cluster=None
# $Id$
"""
edit layout and content if form submited

return html renderer + psm
"""

context_is_portlet = 0
if getattr(context.aq_explicit, 'isCPSPortlet', None) is not None:
    if context.aq_explicit.isCPSPortlet():
        context_is_portlet = 1

if context_is_portlet:
    doc = context
else:
    # Get portlet_id form the templet
    ptltool = context.portal_cpsportlets
    portlet_id = context.getPortletId()
    # Get the portlet from the tool
    doc = ptltool.getPortletById(portlet_id)

layout_changed = doc.editLayouts(REQUEST=REQUEST);

if layout_changed or REQUEST.has_key('cpsdocument_edit_button'):
    request = REQUEST
    psm = 'psm_content_changed'
else:
    request = None
    psm = ''

res = doc.renderEditDetailed(request=request, proxy=doc,
                             cluster=cluster)

if not res[1]:
    psm = 'psm_content_error'
    error = 1
else:
    # XXX
    # Has to be handled in here since the workflow doesn't take care
    # of that yet.
    error = 0
    from Products.CPSCore.EventServiceTool import getPublicEventService
    evtool = getPublicEventService(context)
    evtool.notifyEvent('workflow_modify', context, {})

# update cache parameters
ptype_id = doc.getPortletType()
doc.resetCacheTimeout()
doc.resetInterestingEvents(ptype_id)
doc.expireCache()

if context_is_portlet:
    return res[0], psm, error

if REQUEST is not None:
    redirect_url = REQUEST.get('HTTP_REFERER')
    return REQUEST.RESPONSE.redirect(redirect_url)
