## Script (Python) "logout"
##title=Logout handler
##parameters=

# notify the event service that the user has logged out
user = context.portal_membership.getAuthenticatedMember()
etool = getattr(context, 'portal_eventservice', None)
if etool is not None:
    if user:
        etool.notifyEvent('user_logout', user, {})

REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
    context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
return REQUEST.RESPONSE.redirect(REQUEST.URL1+'/logged_out')
