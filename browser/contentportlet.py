import re
import logging

from DateTime.DateTime import DateTime
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.DataStructure import DataStructure
from exportviews import BaseExportView
from exportviews import RssMixin
from exportviews import AtomMixin

logger = logging.getLogger(__name__)

class ContentPortletView(BaseExportView):
    """The export base view is very suitable for this portlet in all cases."""

    def initFolder(self):
        """Set folder and portal attributes."""
        rpath = self.datamodel['folder_path']
        if rpath.startswith('/'):
            rpath = rpath[1:]
        portal =  self.url_tool().getPortalObject()
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

    def initItems(self):
        kw = dict(self.datamodel) # dict() necessary to pass on
        kw['get_metadata'] = True
        self.items = self.context.getContentItems(obj=self.getContextObj(),
                                                  **kw)

    def isContextual(self):
        dm = self.datamodel
        return dm['contextual'] or dm['search_type'] == 'related'


class RssExportView(RssMixin, ContentPortletView):
    """The class to use for all RSS exports of content portlets"""


class AtomExportView(AtomMixin, ContentPortletView):
    """The class to use for all Atom exports of content portlets"""
