
switch_langs = []

# existing language revisions
if getattr(context.aq_inner.aq_explicit,
    'getLanguageRevisions', None) is not None:
    revs = context.getLanguageRevisions().keys()

    for lang in revs:
        title = 'label_language_%s' % lang
        switch_langs.append({'lang': lang,
                             'title': title})

# there is no notion of language revision
else:
    return []

return switch_langs
