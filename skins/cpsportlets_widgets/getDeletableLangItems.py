
# permission check
mtool = context.portal_membership
if not mtool.checkPermission('Modify portal content', context):
    return []

# available languages
del_langs = []

# checking whether 'delLanguageFromProxy()' is supported
if getattr(context.aq_inner.aq_explicit,
    'delLanguageFromProxy', None) is None:
    return []

default_lang = context.getDefaultLanguage()

# existing language revisions
if getattr(context.aq_inner.aq_explicit,
    'getLanguageRevisions', None) is not None:
    revs = context.getLanguageRevisions().keys()

    # Cannot delete last language
    if len(revs) == 1:
        return []

    for lang in revs:
        # Cannot delete default language
        if lang == default_lang:
            continue

        title = 'label_language_%s' % lang
        del_langs.append({'lang': lang, 'title': title})

# there is no notion of language revision
else:
    return []

return del_langs
