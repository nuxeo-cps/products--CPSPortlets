##parameters=obj=None, REQUEST=None, **kw

if REQUEST is not None:
    kw.update(REQUEST.form)

catalog = context.portal_catalog

search_type = kw.get('search_type')

if obj is None:
    return []

query = {}

if search_type == 'related':
    obj = obj.getContent()
    if getattr(obj.aq_explicit, 'Subject'):
        subjects=obj.Subject()

        if subjects:
            query.update({'Subject': subjects,
                          'review_state': 'published'})

if search_type == 'pending':
    query.update({'review_state': 'pending'})

if search_type == 'last_modified':
    query.update({'review_state': 'published'})

if not query:
    return []

try:
    brains = catalog(**query)
except ParseError:
    brains = []

return brains
