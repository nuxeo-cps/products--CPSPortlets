##parameters=lang=None, REQUEST=None

if not lang:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

# existing language revisions
if getattr(context.aq_explicit, 'getLanguageRevisions', None) is None:
    return

revs = context.getLanguageRevisions().keys()
# Cannot set invalid language names
if lang not in revs:
    return

context_url = REQUEST.get('context_url', context.getContextUrl())

if REQUEST is not None:
    redirect_url = '%s/switchLanguage/%s/' % (context_url, lang)
    REQUEST.RESPONSE.redirect(redirect_url)
