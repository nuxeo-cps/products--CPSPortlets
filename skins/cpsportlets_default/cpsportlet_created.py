##parameters=
"""
Do the necessary rendering or redirection after an object has been
successfully created and filled with the initial values by the user.

In CPS, context is a proxy.

May return a rendered document, or do a redirect.
"""
# $Id$

psm = 'psm_content_created'
action_path = context.getTypeInfo().immediate_view
context.REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                                  (context.absolute_url(), action_path, psm))
