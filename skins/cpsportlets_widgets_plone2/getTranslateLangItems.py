
if getattr(context, 'isTranslatable', None) is None:
    return []

if not context.isTranslatable():
    return []

if getattr(context, 'getUntranslatedLanguages', None) is None:
    return []

dest_langs = []
langs = context.getUntranslatedLanguages()

for lang in langs:
    lang_id = lang[0]
    title = lang[1]
    dest_langs.append({'lang': lang_id, 'title': title})

return dest_langs
