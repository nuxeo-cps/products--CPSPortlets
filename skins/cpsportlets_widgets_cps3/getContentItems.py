##parameters=obj=None, REQUEST=None, **kw


if obj is None:
    return []

if REQUEST is not None:
    kw.update(REQUEST.form)

max_items = int(kw.get('max_items', 5))

query = {}
# set portal_type query parameter
searchable_types = kw.get('searchable_types', [])
if len(searchable_types) > 0:
    query['portal_type'] = searchable_types

# cps filter (portal_xyz, .___)
query['cps_filter_sets'] = {'query': ('searchable', 'leaves'),
                            'operator': 'and'}
# folder path
folder_path = kw.get('folder_path')
if folder_path is not None:
    portal_path = context.portal_url.getPortalPath()
    query['path'] = portal_path + folder_path

# return the results in descending order
if kw.get('sort_reverse'):
    query['sort_order'] = 'reverse'

# Title search (if specified)
query_title = kw.get('query_title')
if query_title is not None:
    query['ZCTitle'] = query_title

# Override some of the query options depending on the type of search

# Related documents
search_type = kw.get('search_type')
if search_type == 'related':
    content = obj.getContent()
    if getattr(content.aq_inner.aq_explicit, 'Subject'):
        subjects=content.Subject()
        if subjects:
            query.update({'Subject': subjects,
                          'review_state': 'published',})
            max_items += 1
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
    query.update({'sort_on': 'Date'})

# Last published documents
elif search_type == 'last_published':
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

# Today's events:
# - published
# - today's latest time > start date
elif search_type == 'today':
    now = context.ZopeTime()
    query.update({'review_state': 'published',
                  'start': {'query': now.latestTime(),
                            'range': 'max'},
                  'sort_on': 'start',
                 })

# Upcoming events:
# - published
# - effective date > now
elif search_type == 'upcoming':
    now = context.ZopeTime()
    query.update({'review_state': 'published',
                  'effective': {'query': now, 'range': 'max'},
                  'sort_on': 'Date',
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

# optimization
query['sort_limit'] = max_items

brains = context.portal_catalog(**query)
try:
    brains = context.portal_catalog(**query)
except: # XXX
    brains = []

# post-filtering
if search_type == 'related':
    # XXX also remove the same versions of a document published
    # in different places?
    obj_url = obj.absolute_url()
    brains = [o for o in brains if o.getURL() != obj_url]

# build results dictionary
def summarize(text='', max_words=20):
    """summarize the text by returning the first max_words
    """
    split_text = text.split(' ', max_words)[0:max_words]
    res = ''
    if split_text:
        res = ' '.join(split_text) + ' ...'
    return res

# return the catalog brain's actual content
def getBrainContent():
    content = None
    if getattr(brain.aq_inner.aq_explicit, 'getRID', None) is not None:
        obj = brain.getObject()
        getContent = getattr(obj.aq_inner.aq_explicit, 'getContent', None)
        if getContent is not None:
            content = getContent()
    return content

items = []
render_items = int(kw.get('render_items'), 0) == 1
cluster_id = kw.get('cluster_id')
display_description = kw.get('display_description')

# Dublin Core / metadata
getMetaData = kw.get('getMetaData')
metadata_map = {
    'creator': 'Creator',
    'date': 'ModificationDate',
    'issued': 'EffectiveDate',
    'created': 'CreationDate',
    'rights': 'Rights',
    'language': 'Language',
    'contributor': 'Contributors',
    'source': 'source',
    'relation': 'relation',
    'coverage': 'coverage'}

for brain in brains:
    content = None

    rendered = ''
    # render the item
    if render_items:
        content = getBrainContent()
        renderable = 1
        # check whether the cluster exists.
        # XXX: this could be done in CPSDocument.FlexibleTypeInformation.py
        if cluster_id:
            ti =  content.getTypeInfo()
            if ti is None:
                continue
            renderable = 0
            for cluster in ti.getProperty('layout_clusters', []):
                cl, v = cluster.split(':')
                if cl == cluster_id:
                    renderable = 1
                    break

        if renderable:
            render = getattr(content, 'render', None)
            if render is not None:
                # render the document by cluster (if specified)
                try:
                    rendered = render(proxy=obj, cluster=cluster_id)
                except TypeError:
                    pass

    # default item presentation (summary of description)
    if not rendered:
        if display_description:
            description = brain['Description']
            max_words = int(kw.get('max_words', 20))
            if max_words > 0:
                description = summarize(description, max_words)
            rendered = description

    # DublinCore / metadata information
    metadata_info = {}

    if getMetaData:
        if content is None:
            content = getBrainContent()

        for key, attr in metadata_map.items():
            meth = getattr(content, attr)
            if callable(meth):
                value = meth()
            else:
                value = meth
            if not value or value is 'None':
                continue
            if not isinstance(value, str):
                value = ', '.join(value)
            metadata_info[key] = value

    items.append(
        {'url': brain.getURL(),
         'title': brain['Title'],
         'description': brain['Description'],
         'rendered': rendered,
         'metadata': metadata_info,
        })

return items
