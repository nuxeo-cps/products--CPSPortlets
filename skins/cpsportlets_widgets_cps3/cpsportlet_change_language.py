##parameters=lang=None, REQUEST=None

if not lang:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

from Products.CPSCore.utils import resetSessionLanguageSelection

# Reset previous language settings in the current session
resetSessionLanguageSelection(REQUEST)

# switch to 'lang'
portal = context.portal_url.getPortalObject()
portal.Localizer.changeLanguage(lang=lang)

if REQUEST is not None:
    redirect_url = REQUEST['HTTP_REFERER']
    # Avoid redirection to a switchLanguage action
    if '/switchLanguage' in redirect_url:
        index = redirect_url.find('/switchLanguage')
        redirect_url = redirect_url[:index]
    REQUEST.RESPONSE.redirect(redirect_url)
