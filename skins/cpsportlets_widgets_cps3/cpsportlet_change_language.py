##parameters=lang=None, REQUEST=None

if not lang:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

# switch to 'lang'
portal = context.portal_url.getPortalObject()
portal.Localizer.changeLanguage(lang=lang)

if REQUEST is not None:
    redirect_url = REQUEST['HTTP_REFERER']
    REQUEST.RESPONSE.redirect(redirect_url)
