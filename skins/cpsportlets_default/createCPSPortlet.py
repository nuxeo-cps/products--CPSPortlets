##parameters=REQUEST=None, **kw

if REQUEST is not None:
    kw.update(REQUEST.form)

ptype_id = kw.get('ptype_id')
if ptype_id is None:
    return

ptltool = context.portal_cpsportlets
portlet_id = ptltool.createPortlet(context=context, **kw)
portlet_container = ptltool.getPortletContainer(context)
portlet = portlet_container.getPortletById(portlet_id)
ptltool.insertPortlet(portlet=portlet, **kw)
portlet_localfolder = portlet.getLocalFolder()

if REQUEST is not None:
    msg = 'cpsportlets_portlet_created_psm'
    redirect_url = portlet.absolute_url() \
                   + '/cpsportlet_edit_form' \
                   + '?portal_status_message=' + msg
    REQUEST.RESPONSE.redirect(redirect_url)
