##parameters=context_obj=None, show_docs=None, max_title_words=0, context_rpath='', context_is_portlet=0, **kw

base_url = context.cpsskins_getBaseUrl()

if context_is_portlet:
    context_obj = context.getLocalFolder()

if context_rpath:
    context_obj = context.restrictedTraverse(context_rpath, default=None)

if context_obj is None:
    return []

folder_items = []

# Find bottom-most folder:
obj = context_obj
bmf = None
while 1:
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
getRelativeUrl = context.portal_url.getRelativeUrl

display_folders = int(kw.get('display_folders', 1))
display_hidden_folders = int(kw.get('display_hidden_folders', 1))
display_hidden_docs = int(kw.get('display_hidden_docs', 0))
display_description = int(kw.get('display_description', 0))

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

for object in bmf.objectValues():
    # remove objects with ids beginning with '.'
    if object.getId().startswith('.'):
        continue
    # filter out objects that cannot be viewed
    if not checkPerm('View', object):
        continue
    if getattr(object, 'view', None) is None:
        continue

    # skip documents if show_docs is not set
    ptype = getattr(object, 'portal_type', None)
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
    if get_metadata:
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

    folder_items.append(
        {'id': object.getId(),
         'url': base_url + getRelativeUrl(object),
         'title': title,
         'description': description,
         'icon_tag': renderIcon(ptype, base_url, ''),
         'metadata': metadata_info,
        })
return folder_items
