##parameters=context_obj=None, show_docs=False, max_title_words=0, context_rpath='', context_is_portlet=0, **kw
#
# $Id$
"""Return the list of items found in the folder found through context_obj.
"""

utool = context.portal_url
base_url = utool.getBaseUrl()

if context_is_portlet:
    context_obj = context.getLocalFolder()

if context_rpath:
    context_obj = context.restrictedTraverse(context_rpath, default=None)

if context_obj is None:
    return []

context_url = context_obj.absolute_url_path()
folder_items = []

# Find bottom-most folder
obj = context_obj
bmf = None
while True:
    if obj.isPrincipiaFolderish:
        bmf = obj
        break
    parent = obj.aq_inner.aq_parent
    if not obj or parent == obj:
        break
    obj = parent
if bmf is None:
    bmf = folder


mtool = context.portal_membership
checkPerm = mtool.checkPermission
if not checkPerm('List folder contents', bmf):
    return []

portal_types = context.portal_types
renderIcon = context.portal_cpsportlets.renderIcon

getFTIProperty = context.portal_cpsportlets.getFTIProperty

display_folders = int(kw.get('display_folders', 1))
display_hidden_folders = int(kw.get('display_hidden_folders', 1))
display_hidden_docs = int(kw.get('display_hidden_docs', 0))
display_description = int(kw.get('display_description', 0))
display_valid_docs = int(kw.get('display_valid_docs', 0))
sort_by = kw.get('sort_by')

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

def getContent(object):
    content = None
    try:
        content = object.getContent()
    except AttributeError:
        pass
    return content

for object in bmf.contentValues():

    object_id = object.getId()
    # filter out objects that cannot be viewed
    if not checkPerm('View', object):
        continue
    if getattr(object, 'view', None) is None:
        continue

    # skip documents if show_docs is not set
    ptype = object.getPortalTypeName()
    # Using a RAM cache to optimize the retrieval of FTI
    isdocument = getFTIProperty(ptype, 'cps_proxy_type') == 'document'
    display_as_document_in_listing = getFTIProperty(
        ptype, 'cps_display_as_document_in_listing')
    if int(show_docs) == 0 and (isdocument or display_as_document_in_listing):
        continue

    content = None

    # a folder is not 'documentish'
    # folderish documents are not folders.
    isfolder = not isdocument

    # hide folders?
    if isfolder and not display_folders:
        continue

    # hide hidden folders
    if isfolder and not display_hidden_folders:
        content = content or getContent(object)
        if content is not None and \
            getattr(content.aq_inner.aq_explicit, 'hidden_folder', 0):
            continue

    # hide hidden documents
    # TODO not implemented in document schemas
    if isdocument and not display_hidden_docs:
        content = content or getContent(object)
        if content is not None and \
            getattr(content.aq_inner.aq_explicit, 'hidden_document', 0):
            continue

    # XXX TODO: Dublin Core effective / expiration dates

    # DublinCore / metadata information
    metadata_info = {}
    if get_metadata or sort_by in ('date', 'author'):
        content = content or getContent(object)
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

    # filter out documents not yet effective and expired documents
    if display_valid_docs:
        now = context.ZopeTime()
        content = content or getContent(object)
        if content is None:
            continue
        if now < content.effective() or now > content.expires():
            continue

    # title
    title = object.title_or_id()
    if max_title_words > 0:
        words = title.split(' ')
        if len(words) > max_title_words:
            title = ' '.join(words[:int(max_title_words)]) + ' ...'

    # description
    description = ''
    if display_description:
        content = content or getContent(object)
        if content is not None:
            description = getattr(content, 'Description', '')

    object_url = object.absolute_url_path()
    folder_items.append(
        {'id': object_id,
         'url': object_url,
         'title': title,
         'content': content,
         'description': description,
         'icon_tag': renderIcon(ptype, base_url, ''),
         'metadata': metadata_info,
         'selected': (context_url + '/').startswith(object_url + '/'),
        })

# sorting
def id_sortkey(a):
    return a['id']
def title_sortkey(a):
    return a['title'].lower()
def date_sortkey(a):
    return str(a['metadata']['date']) + a['id']
def author_sortkey(a):
    return a['metadata']['creator'] + a['id']
def cmp_desc(x, y):
    return -cmp(x, y)

if sort_by:
    sort_direction = kw.get('sort_direction')
    make_sortkey = id_sortkey
    if sort_by == 'date':
        make_sortkey = date_sortkey
        sort_direction = sort_direction or 'desc'
    elif sort_by == 'title':
        make_sortkey = title_sortkey
    elif sort_by == 'author':
        make_sortkey = author_sortkey
    items = [ (make_sortkey(x), x) for x in folder_items ]
    if sort_direction == 'desc':
        items.sort(cmp_desc)
    else:
        items.sort()
    folder_items = [x[1] for x in items]

return folder_items
