lc = getattr(context, 'Localizer', None)
if lc is None:
    return []

# permission check
mtool = context.portal_membership
if not mtool.checkPermission('Modify portal content', context):
    return []

# available languages
langs = lc.get_languages()
dest_langs = []

# existing language revisions
if getattr(context.aq_explicit, 'getLanguageRevisions', None) is not None:
    revs = context.getLanguageRevisions().keys()
    cpsmcat = lc.default
    for lang in langs:
        if lang in revs:
            continue
        title = cpsmcat('label_language_%s' % lang)
        dest_langs.append({'lang': lang, 'title': title})

# there is no notion of language revision
else:
    return []

return dest_langs
