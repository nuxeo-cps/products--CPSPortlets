
pltool = getattr(context, 'portal_languages', None)
if pltool is None:
    return []


if getattr(pltool, 'getAvailableLanguages', None) is None:
    return []

langs = pltool.getAvailableLanguages()

available_langs = []

for lang in langs:
    lang_id = lang[0]
    title = lang[1]
    available_langs.append({'lang': lang_id, 'title': title})

return available_langs
