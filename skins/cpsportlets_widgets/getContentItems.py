##parameters=obj=None, REQUEST=None, **kw
# $Id$
if obj is None:
    return []

from Products.CPSUtil.timer import Timer
t = Timer('CPSPortlets getContentItems')

if REQUEST is not None:
    kw.update(REQUEST.form)

max_items = int(kw.get('max_items', 5))

query = {}
# set portal_type query parameter
searchable_types = kw.get('searchable_types', [])
if len(searchable_types) > 0:
    query['portal_type'] = searchable_types

# cps filter (portal_xyz, .___)
query['cps_filter_sets'] = {'query': ('searchable',),
                            'operator': 'and'}

# path
query_rpath = ''

# contextual search (using the context as the path prefix)
contextual = int(kw.get('contextual', 0))
if contextual:
    if not obj.isPrincipiaFolderish:
        obj = obj.aq_inner.aq_parent
    query_rpath = context.portal_url.getRelativeUrl(obj)

# explicit folder path
else:
    query_rpath = kw.get('folder_path')

if query_rpath:
    query['path'] = context.portal_url.getPortalPath() + '/' + query_rpath

# sort on
query['sort_on'] = kw.get('sort_on')

# return the results in descending order
if int(kw.get('sort_reverse', 0)) == 1:
    query['sort-order'] = 'reverse'

# Title search (if specified)
query_title = kw.get('query_title')
if query_title is not None:
    if query_title == '*':
        query_title = ''
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
    query.update({'sort_on': 'modified'})

# Last published documents
elif search_type == 'last_published':
    query.update({'review_state': 'published',
                  'sort_on': 'modified'})

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
                  'sort_on': 'modified',
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


elif search_type == 'all':
    pass

# unknown search type
else:
    query = {}

if not query:
    return []

# This is for classical ZCatalog
query['sort_limit'] = max_items
# This is for NXLucene which works with batching
query['b_start'] = 0
query['b_size'] = max_items
# match_languages index purpose is to make the default language match if
# users' doesn't exist in proxy.
# we use it if 'strict_lang_filtering' is False
translation_service = context.translation_service
match_languages = 'en'
match_languages = translation_service.getSelectedLanguage()
if not match_languages:
    if context.isUsePortalDefaultLang():
        match_languages = translation_service.getDefaultLanguage()
if kw.get('strict_lang_filtering'):
    query['Language'] = match_languages
else:
    query['match_languages'] = match_languages
t.mark('query: %s' % str(query))
brains = context.portal_catalog(**query)
t.mark('search done')
# post-filtering
if search_type == 'related':
    # XXX also remove the same versions of a document published
    # in different places?
    obj_url = obj.absolute_url()
    brains = [o for o in brains if o.getURL() != obj_url]

# build results dictionary
def summarize(text='', max_words=20):
    """summarize the text by returning the first max_words"""
    if not text:
        return ''
    words = text.split(' ')
    if len(words) > max_words:
        words = words[:max_words] + [' ...']
    return ' '.join(words)

# return the catalog brain's actual content
def getBrainInfo():
    content = None
    object = None
    if getattr(brain.aq_inner.aq_explicit, 'getRID', None) is not None:
        object = brain.getObject()
        getContent = getattr(object.aq_inner.aq_explicit, 'getContent', None)
        if getContent is not None:
            content = getContent()
    return content, object

items = []
render_items = int(kw.get('render_items', 0))
cluster_id = kw.get('cluster_id')
display_description = int(kw.get('display_description', 0))
show_icons = int(kw.get('show_icons', 0))

DEFAULT_CONTENT_ITEM_DISPLAY = 'cpsportlet_contentitem_display'
render_method = kw.get('render_method') or DEFAULT_CONTENT_ITEM_DISPLAY
render_method = getattr(context, render_method, None)

# Dublin Core / metadata
get_metadata = int(kw.get('get_metadata', 0))
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

# portal type icons
portal_types = context.portal_types
renderIcon = context.portal_cpsportlets.renderIcon

utool = context.portal_url
base_url = utool.getBaseUrl()

order = 0
for brain in brains:
    order += 1

    content = None
    if render_items or render_method != DEFAULT_CONTENT_ITEM_DISPLAY:
        content, object = getBrainInfo()

    # DublinCore / metadata information
    metadata_info = {}
    if get_metadata:
        content = content or getBrainInfo()[0]

        for key, attr in metadata_map.items():
            meth = getattr(content, attr)
            if callable(meth):
                value = meth()
            else:
                value = meth
            if not value or value is 'None':
                continue
            if not isinstance(value, str):
                try:
                    value = ', '.join(value)
                except TypeError:
                    value = str(value)
            metadata_info[key] = value

    # Item's icon
    icon_tag = ''
    if show_icons:
        content = content or getBrainInfo()[0]
        ti = content.getTypeInfo()
        if ti is not None:
            icon_tag = renderIcon(ti.getId(), base_url, '')

    # Item's summary
    summary = brain['Description']
    if display_description:
        max_words = int(kw.get('max_words', 20))
        if max_words > 0:
            summary = summarize(summary, max_words)

    # Item rendering and display
    rendered = ''
    # render the item using CPSDocument render()
    if render_items:
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
            renderer = getattr(content, 'render', None)
            if renderer is not None:
                try:
                    rendered = renderer(proxy=object, cluster=cluster_id)
                except TypeError:
                    pass

    # render the item using a custom display method (.zpt, .py, .dtml)
    elif render_method is not None:
        kw.update({'item': content,
                   'brain': brain,
                   'summary': summary,
                   'order': order,
                   'metadata_info': metadata_info,
                   'icon_tag': icon_tag})
        rendered = apply(render_method, (), kw)

    # this information is used by custom templates that call getContentItems()
    # directly.
    title = brain['Title'] or getattr(brain, 'dc:title', '')
    items.append(
        {'url': brain.getURL(),
         'title': title,
         'description': summary,
         'rendered': rendered,
         'metadata': metadata_info,
         'icon_tag': icon_tag,
        })
#t.log('done')
return items
