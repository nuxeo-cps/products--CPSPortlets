##parameters=obj=None, REQUEST=None, **kw


if obj is None:
    return []

if REQUEST is not None:
    kw.update(REQUEST.form)

search_type = kw.get('search_type')
sort_reverse = kw.get('sort_reverse')
max_items = kw.get('max_items', 5)
max_items = int(max_items)
folder_path = kw.get('folder_path')

# remove unwanted search options
for k in kw.keys():
    if k not in ('sort_on', 'review_state'):
       del kw[k]

query = kw

# cps filter (portal_xyz, .___)
query['cps_filter_sets'] = {'query': ('searchable', 'leaves'),
                            'operator': 'and'}

# folder path
if folder_path is not None:
    portal_path = context.portal_url.getPortalPath()
    query['path'] = portal_path + folder_path

# return the results in descending order
if sort_reverse:
    query['sort_order'] = 'reverse'

# optimization
query['sort_limit'] = max_items

# Override some of the query options depending on the type of search

# Related documents
# XXX remove the current document from the search results
if search_type == 'related':
    obj = obj.getContent()
    if getattr(obj.aq_explicit, 'Subject'):
        subjects=obj.Subject()

        if subjects:
            query.update({'Subject': subjects,
                          'review_state': 'published'})
        else:
            query = {}

# Pending documents
# - review_state is pending
# XXX: only include the documents that the current user may change the
# workflow on from pending to another state.
elif search_type == 'pending':
    query.update({'review_state': 'pending'})

# Last modified documents
elif search_type == 'last_modified':
    query.update({'review_state': 'published',
                  'sort_on': 'Date'})

# Upcoming events:
# - published
# - end date > now
elif search_type == 'upcoming':
    now = context.ZopeTime()
    query.update({'review_state': 'published',
                  'end': {'query': now, 'range': 'min'},
                  'sort_on': 'start',
                 })

# Recent documents:
# - published
# - modified date > last_login_time
elif search_type == 'recent':
    member = context.portal_membership.getAuthenticatedMember()
    if member and getattr(member, 'last_login_time', None) is not None:
        query.update({'modified': member.last_login_time,
                      'modified_usage': 'range:min',
                      'review_state': 'published',
                     })
    else:
        query = {}

# unknown search type
else:
    query = {}

if not query:
    return []

brains = context.portal_catalog(**query)
try:
    brains = context.portal_catalog(**query)
except: # XXX
    brains = []

if len(brains) > max_items:
    brains = brains[:max_items]
return brains
