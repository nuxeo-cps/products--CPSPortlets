##parameters=lang=None, REQUEST=None

lc = getattr(context, 'Localizer', None)
if lc is None:
    return

if REQUEST is None:
    REQUEST = context.REQUEST

doc_lang = context.getDefaultLanguage()

# existing language revisions
if getattr(context.aq_explicit, 'getLanguageRevisions', None) is None:
    return

revs = context.getLanguageRevisions().keys()
# the revision in 'lang' exists already
if lang in revs:
    return

# create a language revision in 'lang'
context.addLanguageToProxy(lang=lang, from_lang=doc_lang)
context.reindexObject()

# switch to 'lang'
portal = context.portal_url.getPortalObject()
portal.Localizer.changeLanguage(lang=lang)

if REQUEST is not None:
    # XXX i18n
    msg = 'Document translated'
    redirect_url = context.absolute_url() + '?portal_status_message=%s' % msg
    REQUEST.RESPONSE.redirect(redirect_url)
