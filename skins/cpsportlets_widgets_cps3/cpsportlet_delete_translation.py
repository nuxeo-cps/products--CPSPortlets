##parameters=lang=None, REQUEST=None

if not lang:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

lc = getattr(context, 'Localizer', None)
if lc is None:
    return

# existing language revisions
if getattr(context.aq_explicit, 'getLanguageRevisions', None) is None:
    return

revs = context.getLanguageRevisions().keys()
# Cannot delete invalid language
if lang not in revs:
    return

# Cannot delete last language
if len(revs) == 1:
    return

# checking whether 'delLanguageFromProxy()' is implemented
if getattr(context.aq_inner.aq_explicit, 'delLanguageFromProxy', None) is None:
    return

# delete the language revision in 'lang'
context.delLanguageFromProxy(lang=lang)

# switch to 'default_lang'
if REQUEST is not None:
    default_lang = context.getDefaultLanguage()
    context_url = REQUEST.get('context_url', context.getContextUrl())
    psm = 'cpsportlets_translation_deleted_psm'
    redirect_url = '%s/switchLanguage/%s/?portal_status_message=%s' % \
                   (context_url, default_lang, psm)
    REQUEST.RESPONSE.redirect(redirect_url)
