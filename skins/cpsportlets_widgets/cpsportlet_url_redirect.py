##parameters=url=None, REQUEST=None, **kw

if url is None:
    return

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(url)
