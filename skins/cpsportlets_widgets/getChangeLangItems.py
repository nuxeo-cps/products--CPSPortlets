lc = getattr(context, 'Localizer', None)
if lc is None:
    return []

# current language
current_lang = lc.get_selected_language()

# available languages
lang_map = lc.get_languages_map()

langs = []
for lang in lang_map:
    lang_id = lang['id']
    if lang_id == current_lang:
        continue
    title = 'label_language_native_%s' % lang_id
    langs.append({'lang': lang_id, 'title': title})

return langs
