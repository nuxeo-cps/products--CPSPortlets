##parameters=lang=None, REQUEST=None, **kw

if not lang:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

context.deleteTranslations(languages=[lang])

redirect_url = context.absolute_url()
REQUEST.RESPONSE.redirect(redirect_url)
