##parameters=url=None, REQUEST=None, **kw

if not url:
    return

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(url)
