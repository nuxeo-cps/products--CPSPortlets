##parameters=obj=None, REQUEST=None, **kw

if obj is None:
    return []

if REQUEST is not None:
    kw.update(REQUEST.form)

search_type = kw.get('search_type')
sort_reverse = kw.get('sort_reverse')

# remove unwanted search options
for k in kw.keys():
    if k not in ('sort_on', 'review_state'):
       del kw[k]

query = kw

# Related documents
if search_type == 'related':
    obj = obj.getContent()
    if getattr(obj.aq_explicit, 'Subject'):
        subjects=obj.Subject()

        if subjects:
            query.update({'Subject': subjects,
                          'review_state': 'published'})

# Pending documents
elif search_type == 'pending':
    query.update({'review_state': 'pending'})

# Last modified documents
elif search_type == 'last_modified':
    query.update({'review_state': 'published'})

# Upcoming events
elif search_type == 'upcoming':
    # XXX
    pass

# Recent documents 
elif search_type == 'recent':
    # XXX
    pass


# XXX does not work yet
if sort_reverse:
    query.update({'sort_order': 'reverse'})

if not query:
    return []

try:
    brains = context.portal_catalog(**query)
except ParseError:
    brains = []

return brains
