##parameters=lang=None, REQUEST=None

if not lang:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

doc_lang = context.getLanguage()

# existing language revisions
if getattr(context.aq_explicit, 'getLanguageRevisions', None) is None:
    return

revs = context.getLanguageRevisions().keys()
# the revision in 'lang' exists already
if lang in revs:
    return

# checking whether 'addLanguageToProxy()' is supported
if getattr(context.aq_explicit, 'addLanguageToProxy', None) is None:
    return

# create a language revision in 'lang'
context.addLanguageToProxy(lang=lang, from_lang=doc_lang)

# switch to 'lang'
if REQUEST is not None:
    context_url = REQUEST.get('context_url', context.getContextUrl())
    psm = 'cpsportlets_content_translated_psm'
    redirect_url = '%s/switchLanguage/%s/?portal_status_message=%s' % \
                   (context_url, lang, psm)
    REQUEST.RESPONSE.redirect(redirect_url)
