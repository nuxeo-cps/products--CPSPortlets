
# XXX permission check ?

# available languages
del_langs = []

# checking whether 'getDeletableLanguages' is supported
# XXX acquisition ?
if getattr(context, 'getDeletableLanguages', None) is None:
    return []

langs = context.getDeletableLanguages()

for lang in langs:
    lang_id = lang[0]
    title = lang[1]
    del_langs.append({'lang': lang_id, 'title': title})

return del_langs
