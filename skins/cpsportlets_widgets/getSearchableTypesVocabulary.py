##parameters=key=None

items = []
for ptype in context.getSearchablePortalTypes():
    ptype_id = ptype.getId()
    ptype_title = ptype.Title()
    if key is not None and key == ptype_id:
        return ptype_title
    items.append((ptype_id, ptype_title))

return items
