##parameters=lang=None, REQUEST=None

if not lang:
    return

lc = getattr(context, 'Localizer', None)
if lc is None:
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
context.reindexObject()

# switch to 'lang'
portal = context.portal_url.getPortalObject()
portal.Localizer.changeLanguage(lang=lang)

if REQUEST is not None:
    msg = 'cpsportlets_content_translated_psm'
    redirect_url = context.absolute_url() + '?portal_status_message=%s' % msg
    REQUEST.RESPONSE.redirect(redirect_url)
