from DateTime.DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.DataStructure import DataStructure

RSS_CONTENT_TYPE = 'application/rss+xml'

ATOM_CONTENT_TYPE = 'application/atom+xml'

DATETIME_FORMATS = dict(W3CDTF='%Y-%m-%dT%H:%M:%SZ',
                        )


class BaseExport(BrowserView):

    def __init__(self, *args):
        BrowserView.__init__(self, *args)
        portlet = self.portlet = self.context
        self.datamodel = portlet.getDataModel(context=portlet)
        self.initFolder()
        self.initItems()
        self.responseHeaders()

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
        rpath = self.datamodel['folder_path']
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.folder = portal.restrictedTraverse(rpath) # might be portal

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

    def l10nPortletTitle(self):
        return self.getCpsMcat()(self.datamodel['Title'])

    def folderTitle(self):
        return self.folder.Title() # TODO l10n in some cases ?

    def portletDescription(self):
        return self.datamodel['Description']

    def contentUrl(self):
        return self.portlet.getLocalFolder().absolute_url()

    def dataStructure(self):
        """Return a prepared DataStructure instance for request and context.

        Simplified version of what happens in FlexibleTypeInformation
        Request query parameters are taken into account, just in case
        Session isn't.

        Of course portlets rendering should not rely on datastructure, but
        that's a whole different story.
        """

        portlet = self.portlet
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
        format = DATETIME_FORMATS.get(format)
        if format is None:
            return dt.rfc822() # makes a good default
        return dt.strftime(format)


class ContentPortletExport(BaseExport):

    def itemLastModified(self, item):
        """Return last modified date as a DateTime object."""
        date_str = item['metadata'].get('date')
        if date_str:
            return DateTime(date_str) # lame, but that's the input we have

    def initItems(self):
        kw = dict(self.dataStructure()) # dict() necessary to pass on
        kw['get_metadata'] = True
        self.items = self.context.getContentItems(obj=self.portlet, **kw)

class RssExport(object):

    def contentType(self):
        """TODO: detection of browsers that don't recognize the standard.
        """
        return RSS_CONTENT_TYPE


class ContentPortletRssExport(RssExport, ContentPortletExport):
    """The class to use for all RSS exports of content portlets"""


class AtomExport(object):

    def contentType(self):
        """TODO: detection of browsers that don't recognize the standard.
        """
        return ATOM_CONTENT_TYPE


class AtomContentExport(AtomExport, ContentPortletExport):
    """The class to use for all Atom exports of content portlets"""

