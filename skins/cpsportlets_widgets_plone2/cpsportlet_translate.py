##parameters=lang=None, REQUEST=None, **kw

if not lang:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

redirect_url = context.absolute_url() +\
             '/createTranslation?language=%s&set_language=%s' % (lang, lang)
REQUEST.RESPONSE.redirect(redirect_url)
