import re
import logging

from DateTime.DateTime import DateTime
from AccessControl import Unauthorized
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CPSonFive.browser import AqSafeBrowserView
from Products.CPSSchemas.DataStructure import DataStructure

RSS_CONTENT_TYPE = 'application/rss+xml'

ATOM_CONTENT_TYPE = 'application/atom+xml'

DATETIME_FORMATS = dict(W3CDTF='%Y-%m-%dT%H:%M:%SZ',
                        )
logger = logging.getLogger(__name__)

class BaseExport(AqSafeBrowserView):

    ready = False

    def prepare(self):
        """Can't be done in __init__

        These initializations are likely to require the authenticated user to
        be initialized, which happens after the traversal, during which the
        view class instantiation occurs.
        """
        if self.ready:
            return
        portlet = self.context.aq_inner
        self.aqSafeSet('portlet', portlet)
        self.datamodel = portlet.getDataModel(context=portlet)
        self.initFolder()
        self.initItems()
        self.responseHeaders()
        self.ready = True

    def __call__(self, *args, **kwargs):
        """Intercept the rendering to call prepare().

        We're subclassing Five.browser.metaconfigure.ViewMixinForTemplate, here
        used as metaclass base (as the current class) for instantiation of
        self.

        TODO: maybe insulate that kind of trick from Five specifics
        by putting a generic base class in CPSonFive.browser.
        Note that Five's naming is fortunately the same as the one from
        zope.app.pagetemplate.simpleviewclass
        It's also probably a better idea to understand the use of (standard
        python new-style) metaclass in Zope 3 before Five's adaptation for
        old-style classes.
        """
        self.prepare()
        return self.index(self,  *args, **kwargs) # self.index is the ZPT

    def __getitem__(self, segment):
        """Zope2-style traversal (implementing ITraversable does not work).

        The goal is to control the last URL segment (becomes name of resource
        once downloaded). Subclasses may want to override to restrict to names
        ending, e.g, in '.rss' or to a unique name based on the portlet title.

        Of course, the canonical URI for this export is likely to be the one
        that the portlet may display in its normal rendering mode.
        We don't dare using 'Content-Location' header, whose most common
        use-case is to provide canonical URIs for different entities that may be
        accessible at the same URI (varying resource), because that may confuse
        caching agents.
        """
        return self

    def initFolder(self):
        """Set folder and portal attributes."""
        rpath = self.datamodel['folder_path']
        utool = getToolByName(self.context.aq_inner, 'portal_url')
        portal =  utool.getPortalObject()
        self.aqSafeSet('portal', portal)
        self.aqSafeSet('folder', portal.restrictedTraverse(rpath))

    def contentType(self):
        """Return applicable MIME type for this export.

        This is a method because views can't have properties, and we probably
        need browser-dependent behaviour: not all of them support the standard
        MIME types.
        See e.g., http://www.imc.org/atom-syntax/mail-archive/msg17802.html
        (might be outdated, though, but similar problems arise wih more recent
        standards)
        """
        raise NotImplementedError

    def lastModified(self):
        lmd = self.datamodel['ModificationDate']
        for i in self.items:
            i_lmd = self.itemLastModified(i)
            if i_lmd > lmd:
                lmd = i_lmd
        return lmd

    def responseHeaders(self):
        response = self.request.RESPONSE
        response.setHeader('Content-Type', self.contentType())
        response.setHeader('Last-Modified', self.lastModified().rfc822())

    def getCpsMcat(self):
        _cpsmcat = getattr(self, '._cpsmcat', None)
        if _cpsmcat is not None:
            return _cpsmcat
        ts = self._cpsmcat = getToolByName(self.context, 'translation_service')
        return ts

    def cpsVersion(self):
        """Return suitable CPS version string"""
        # TODO duplicated from CPSCore.PatchCopyright
        try:
            from Products.CPSCore.portal import CPSSite
        except ImportError: # CPS portlets more or less CPS-independent
            return ''

        vstr = '.'.join((str(x) for x in CPSSite.cps_version[1:]))
        vsuffix = getattr(CPSSite, 'cps_version_suffix', '')
        if vsuffix:
            vstr += '-' + vsuffix
        return vstr

    def l10nPortletTitle(self):
        return self.getCpsMcat()(self.datamodel['Title'])

    def folderTitle(self):
        return self.aqSafeGet('folder').Title() # TODO l10n in some cases ?

    def portletDescription(self):
        return self.datamodel['Description']

    def contentUrl(self):
        return self.context.getLocalFolder().absolute_url()

    def dataStructure(self):
        """Return a prepared DataStructure instance for request and context.

        Simplified version of what happens in FlexibleTypeInformation
        Request query parameters are taken into account, just in case.
        Session isn't.

        Of course portlets rendering should not rely on datastructure, but
        that's a whole different story.
        """

        portlet = self.aqSafeGet('portlet')
        fti = portlet.getTypeInfo()
        layouts = (fti.getLayout(lid, portlet) for lid in fti.getLayoutIds())

        ds = DataStructure(datamodel=self.datamodel)
        for layout in layouts:
            layout.prepareLayoutWidgets(ds)
        ds.updateFromMapping(self.request.form)
        return ds

    def dateTimeFormat(self, dt, format):
        if dt is None:
            return None
        if isinstance(dt, basestring):
            dt = DateTime(dt)
        format = DATETIME_FORMATS.get(format)
        if format is None:
            return dt.rfc822() # makes a good default
        return dt.strftime(format)

    def itemDataModel(self, item):
        """Return a DataModel for the prescribed item, or None"""
        rpath = item.get('rpath')
        if rpath is None:
            logger.error('Item rpath not provided for %r. Check overrides',
                         item)
            return

        try:
            proxy = self.aqSafeGet('portal').restrictedTraverse(rpath)
            if proxy is None:
                return
            doc = proxy.getContent()
            return doc.getDataModel(proxy=proxy)
        except Unauthorized:
            # in theory, it is possible to access the brain information
            # without accessing the object itself. This is exceptional and
            # happens only if the security index would be bypassed par
            # custom code or would be somewhat broken
            logger.warn("%r unauthorized to access content %r returned "
                        "by search", user, rpath)
        except (KeyError, AttributeError):
            logger.warn("Inconsistency: item %r not reachable or "
                        "cannot provide DataModel", rpath)


class ContentPortletExport(BaseExport):

    def itemLastModified(self, item):
        """Return last modified date as a DateTime object."""
        date_str = item['metadata'].get('date')
        if date_str:
            return DateTime(date_str) # lame, but that's the input we have

    def initItems(self):
        kw = dict(self.dataStructure()) # dict() necessary to pass on
        kw['get_metadata'] = True
        portlet = self.aqSafeGet('portlet')
        self.items = portlet.getContentItems(obj=portlet, **kw)

class RssExport(object):

    def contentType(self):
        """TODO: detection of browsers that don't recognize the standard.
        """
        return RSS_CONTENT_TYPE


class ContentPortletRssExport(RssExport, ContentPortletExport):
    """The class to use for all RSS exports of content portlets"""


class AtomExport(object):

    urlregexp = re.compile(r"^(http://|https://)([^/:]+):?(\d+)?(/.*)$")

    def contentType(self):
        """TODO: detection of browsers that don't recognize the standard.
        """
        return ATOM_CONTENT_TYPE

    def atomId(self, permalink, datetime):
        """Adapted from cpsportlet_contstruct_atomid

        Original docstring:
          <link rel="alternate"> is always the permalink of the entry
          http://diveintomark.org/archives/2004/05/28/howto-atom-id - article
          about constructing id
        """
        m = self.urlregexp.search(permalink)
        if not m:
            return permalink
        location, port, path = m.groups()[1:]
        path = path.split('?')[0]
        uid = 'tag:' + location + ',' + \
            DateTime(datetime).strftime('%Y-%m-%d') + ':' + path
        return uid



class ContentPortletAtomExport(AtomExport, ContentPortletExport):
    """The class to use for all Atom exports of content portlets"""

