##parameters=REQUEST=None

is_view = len(REQUEST.form.keys()) == 0

edit_metadata = context.portal_membership.checkPermission('Modify portal content', context)

if not edit_metadata:
    return context.cpsdocument_metadata_template(metadata=0)
else:
    rendered_main, portal_status_message = context.editCPSDocument(REQUEST=REQUEST,
                                                                   layout_id='metadata')
    error = portal_status_message == 'psm_content_error'
    
    if is_view:
        return context.cpsdocument_metadata_template(edit_metadata=1, rendered_main=rendered_main,
                                                     portal_status_message=portal_status_message)
    elif error:
        return context.cpsdocument_metadata_template(edit_metadata=1, rendered_main=rendered_main,
                                                     portal_status_message=portal_status_message)
    else:
       REQUEST.RESPONSE.redirect(context.absolute_url())
       
