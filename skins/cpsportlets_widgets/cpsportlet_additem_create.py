##parameters=type_name, REQUEST=None, **kw

if type_name == '':
    return

if REQUEST is not None:
    redirect_url = context.absolute_url() +\
    '/content_create?type_name=' + type_name
    REQUEST.RESPONSE.redirect(redirect_url)
