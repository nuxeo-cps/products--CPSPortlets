##parameters=REQUEST=None, **kw

if REQUEST is not None:
    kw.update(REQUEST.form)

ptype_id = kw.get('ptype_id')

ptltool = context.portal_cpsportlets
if ptype_id is not None:
    portlet_id = ptltool.createPortlet(context=context, **kw)
    portlet_container = ptltool.getPortletContainer(context)
    portlet = portlet_container.getPortletById(portlet_id)
    portlet_localfolder = portlet.getLocalFolder()

if REQUEST is not None:
    msg = 'psm_portlet_created'
    redirect_url = portlet_localfolder.absolute_url() \
                   + '/portlet_manage_form' \
                   + '?portal_status_message=' + msg
    REQUEST.RESPONSE.redirect(redirect_url)
