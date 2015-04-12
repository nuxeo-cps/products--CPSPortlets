import logging

from ZTUtils import make_query

from Products.CMFCore.utils import getToolByName
from Products.CPSUtil.timer import Timer
from Products.CPSUtil.text import summarize

from exportviews import BaseExportView
from exportviews import RssMixin
from exportviews import AtomMixin

logger = logging.getLogger(__name__)


class ContentPortletView(BaseExportView):
    """The export base view is very suitable for this portlet in all cases."""

    brains = None
    total_results = 0
    page_size = 5
    current_page = 0

    def initFolder(self):
        """Set folder and portal attributes."""
        rpath = self.datamodel['folder_path']
        if rpath.startswith('/'):
            rpath = rpath[1:]
        portal = self.url_tool().getPortalObject()
        self.aqSafeSet('portal', portal)
        self.aqSafeSet('folder', portal.restrictedTraverse(rpath))

    def itemDataModel(self, item):
        """Return a DataModel for the prescribed item, or None"""
        rpath = item.get('rpath')
        if rpath is None:
            logger.error('Item rpath not provided for %r. Check overrides',
                         item)
            return
        return self.rpathToDataModel(rpath)

    def isContextual(self):
        dm = self.datamodel
        return dm['contextual'] or dm['search_type'] == 'related'

    def catalog_tool(self):
        ctool = self.aqSafeGet('_catalog_tool', None)
        if ctool is None:
            ctool = getToolByName(self.context, 'portal_catalog')
            self.aqSafeSet('_catalog_tool', ctool)
        return ctool

    def performSearch(self):
        """Perfom the search and sets the ``brains`` attribute."""

        obj = self.getContextObj()
        if obj is None:
            return  # kept from skins script, but should not happen

        context = self.portlet()
        kw = dict(self.datamodel)  # avoid side effects

        t = Timer('CPSPortlets contentportlet search')
        kw.update(self.request.form)

        self.page_size = max_items = int(kw.get('max_items', 5))

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
            query_rpath = self.url_tool().getRelativeUrl(obj)

        # explicit folder path
        else:
            query_rpath = kw.get('folder_path')

        if query_rpath:
            query['path'] = self.url_tool().getPortalPath() + '/' + query_rpath

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
            if getattr(content.aq_inner.aq_explicit, 'Subject', None):
                subjects = content.Subject()
                if subjects:
                    query.update({'Subject': subjects,
                                  'review_state': 'published',
                                  })
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
            member = getToolByName(
                self, 'portal_membership').getAuthenticatedMember()
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
            return

        # TODO make this configurable (this can wait, usually there's need
        # for at most one batchable portlet on a page)
        page = int(kw.get('content_page', 1))
        batch = self.insertBatchingParameters(query, page, max_items)

        # match_languages index purpose is to make the default language match
        # if users' doesn't exist in proxy.
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
        # unicode index will not match path index stored as str
        if 'path' in query:
            query['path'] = str(query['path'])

        brains = self.catalog_tool()(**query)
        t.mark('search done')
        # post-filtering
        if search_type == 'related':
            # XXX also remove the same versions of a document published
            # in different places?
            obj_url = obj.absolute_url()
            brains = [o for o in brains if o.getURL() != obj_url]

        # brains don't support slicing through a slice object
        self.total_results = len(brains)
        self.brains = brains[batch[0]:batch[1]]
        self.current_page = page

    def batching_window(self):
        """Return URIs and page numbers for known pages around the current one.

        This is a helper for the template
        """
        first = 1
        last = (self.total_results / self.page_size) + 1
        # TODO harcoded content_page
        form = self.request.form.copy()
        form.pop('-C', None)
        res = []
        for i in range(first, last + 1):
            form['content_page'] = i
            res.append((i, '?' + make_query(form)))
        return res

    def insertBatchingParameters(self, query, page, items_per_page):
        """Add parameters to query so that offset, limit are respected.

        :page: human-friendly page number (starting from 1)
        :returns: a slice to be applied to results (can be for double
                  safety, or really need to achieve what's wanted)
        """

        self.lucene = 'Lucene' in self.catalog_tool().meta_type
        start = (page - 1) * items_per_page
        end = start + items_per_page
        if self.lucene:
            query['b_start'] = start
            query['b_size'] = items_per_page
        else:
            # results will have to be resliced, ZCatalog has seemingly
            # no builtin support for offset
            # no support for total number of results, either, we'll ask for
            # 3 more pages
            query['sort-limit'] = end + 3 * items_per_page
        return start, end

    def initItems(self):
        self.performSearch()
        self.items = self.convertBrains()

    def brainContent(self, brain):
        """Pick the brain's actual content.

        NB: should be avoided as much as possible for performance
        :return: ``(content, brain object)``, where ``content`` is ``None``
                 if the brain object is not a proxy, else its target.
        """
        content = None
        obj = None
        if getattr(brain.aq_inner.aq_explicit, 'getRID', None) is not None:
            obj = brain.getObject()
            getContent = getattr(obj.aq_inner.aq_explicit, 'getContent',
                                 None)
            if getContent is not None:
                content = getContent()
        return content, obj

    def convertBrains(self):
        """Convert search results (brains) in the expected ``items``.

        :returns: a list of dicts.
        """
        brains = self.brains
        if not brains:
            return ()

        context = self.context
        kw = dict(self.datamodel)  # avoid side-effects
        kw['get_metadata'] = True
        kw.update(self.request.form)

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
        renderIcon = context.portal_cpsportlets.renderIcon
        utool = context.portal_url
        base_url = utool.getBaseUrl()
        order = 0
        for brain in brains:
            order += 1

            content = None
            if render_items or render_method != DEFAULT_CONTENT_ITEM_DISPLAY:
                content, brain_obj = self.brainContent(brain)

            # DublinCore / metadata information
            metadata_info = {}
            if get_metadata:
                content = content or self.brainContent()[0]

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
                content = content or self.brainContent()[0]
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
            if render_items:
                self.itemCPSDocumentRender(content,
                                           cluster_id=cluster_id,
                                           proxy=brain_obj)
            # render the item using a custom display method (.zpt, .py, .dtml)
            # GR so in case of downstream explicit rendering, we'll allways
            # have the default template going (slow) or a miss.
            # changing this would be an API break. In the meanwhile, users are
            # encouraged to use 'cpsportlet_contentitem_no_rendering'
            elif render_method is not None:
                kw.update({'item': content,
                           'brain': brain,
                           'summary': summary,
                           'order': order,
                           'metadata_info': metadata_info,
                           'icon_tag': icon_tag})
                rendered = apply(render_method, (), kw)

            # this information is used by custom templates that call
            # getContentItems() directly.
            title = brain['Title'] or getattr(brain, 'dc:title', '')
            items.append(
                {'url': brain.getURL(),
                 'title': title,
                 'description': summary,
                 'rendered': rendered,
                 'metadata': metadata_info,
                 'icon_tag': icon_tag,
                 'portal_type': brain['portal_type'],
                 'rpath': brain.relative_path,
                 })
        return items


def itemCPSDocumentRender(self, doc, cluster_id=None, proxy=None):
    """Render ``doc`` the CPSDocument way (layout clusters).

    :param ``doc``: CPSDocument instance.
    """
    renderable = 1
    # check whether the cluster exists.
    # XXX: this could be done in CPSDocument.FlexibleTypeInformation.py
    if cluster_id:
        ti = doc.getTypeInfo()
        if ti is None:
            return ''
        renderable = 0
        for cluster in ti.getProperty('layout_clusters', []):
            cl, v = cluster.split(':')
            if cl == cluster_id:
                renderable = 1
                break

    if renderable:
        renderer = getattr(doc, 'render', None)
        if renderer is not None:
            try:
                return renderer(proxy=proxy, cluster=cluster_id)
            except TypeError:
                logger.exception("Error while rendering doc %r "
                                 "(cluster_id=%r, proxy=%r)",
                                 doc, cluster_id, proxy)
                return ''


class RssExportView(RssMixin, ContentPortletView):
    """The class to use for all RSS exports of content portlets"""


class AtomExportView(AtomMixin, ContentPortletView):
    """The class to use for all Atom exports of content portlets"""
