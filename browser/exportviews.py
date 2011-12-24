import re
import logging

from DateTime.DateTime import DateTime
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.DataStructure import DataStructure
from baseview import BaseView

RSS_CONTENT_TYPE = 'application/rss+xml'

ATOM_CONTENT_TYPE = 'application/atom+xml'

logger = logging.getLogger(__name__)

class BaseExportView(BaseView):
    """Provide helpers for various portlets exports (Atom feeds, etc.)

    The contents of an export is made of "items", whose lookup is done by
    the initItems() method.

    An export is always related to a folder, whose lookup is done by the
    initFolder() method.

    Subclasses must implement the appropriate initItems(), initFolder() and
    contentType()
    """

    def prepare(self):
        if self.prepared:
            return

        BaseView.prepare(self)
        self.initFolder()
        self.initItems()

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

    def responseHeaders(self):
        """Last-Modified is typically to be set for exports only."""
        response = self.request.RESPONSE
        response.setHeader('Content-Type', self.contentType())
        response.setHeader('Last-Modified', self.lastModified().rfc822())

    def lastModified(self):
        lmd = self.datamodel['ModificationDate']
        for i in self.items:
            i_lmd = self.itemLastModified(i)
            if i_lmd > lmd:
                lmd = i_lmd
        return lmd

    def itemLastModified(self, item):
        """Return last modified date as a DateTime object."""
        date_str = item['metadata'].get('date')
        if date_str:
            return DateTime(date_str) # lame, but that's the input we have

    def l10nPortletTitle(self):
        return self.getCpsMcat()(self.datamodel['Title'])

    def folderTitle(self):
        return self.aqSafeGet('folder').Title() # TODO l10n in some cases ?

    def portletDescription(self):
        return self.datamodel['Description']

    def contentUrl(self):
        return self.portlet().getLocalFolder().absolute_url()

    #
    # Subclass API
    #

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

    def initFolder(self):
        """Initialize the folder related to this export."""
        raise NotImplementedError

    def initItems(self):
        """Initialize the items that make this export.

        They are afterwards available as the 'items' attribute.
        This must be a list of dicts, with the following keys:
           - rpath : relative path of the item from the portal
           - metadata : dict of metadata, must have at least 'date' (string
           representation of item last modification date/time)
        """
        raise NotImplementedError


class RssMixin:
    """To enhance a subclass."""

    def contentType(self):
        """TODO: detection of browsers that don't recognize the standard.
        """
        return RSS_CONTENT_TYPE


class RssExportView(RssMixin, BaseExportView):
    """For direct subclassing."""


class AtomMixin:
    """To enhance a subclass."""

    urlregexp = re.compile(r"^(http://|https://)([^/:]+):?(\d+)?(/.*)$")

    def contentType(self):
        """TODO: detection of browsers that don't recognize the standard.
        """
        return ATOM_CONTENT_TYPE

    def atomId(self, permalink, datetime):
        """Helper method adapted from cpsportlet_contstruct_atomid

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

    def feedAtomId(self):
        return self.constructAtomId(self.contentUrl(),
                                    self.datamodel['CreationDate'])


class AtomExport(BaseExportView):
    """For direct subclassing."""
