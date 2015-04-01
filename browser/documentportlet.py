import logging

from AccessControl import Unauthorized
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import View

from baseview import BaseView

logger = logging.getLogger(__name__)


class DocumentPortletView(BaseView):
    """View for Document Portlets.

    Provide helper to access content, in the form of a ``Datamodel`` instance.
    """

    def docDataModel(self):
        """Return a DataModel for the document this portlet is about."""
        # TODO take context_rpath and render_container fields into account
        proxy = self.context_obj()
        # I'm not sure any more if permissions checkings are done automatically
        # or not
        if not _checkPermission(View, proxy):
            raise Unauthorized
        return proxy.getContent().getDataModel(proxy=proxy)

    def docPortalType(self):
        """Return the type of the document this portlet is about."""
        return self.context_obj().portal_type
