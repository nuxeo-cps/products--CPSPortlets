# (C) Copyright 2011 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <gracinet@cps-cms.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import warnings
from zExceptions import NotFound
from Acquisition import aq_parent, aq_inner
from DateTime.DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSPortlets.CPSPortlet import REQUEST_TRAVERSAL_KEY
from Products.CPSonFive.browser import AqSafeBrowserView

logger = logging.getLogger(__name__)

DATETIME_FORMATS = dict(W3CDTF='%Y-%m-%dT%H:%M:%SZ',
                        )
class BaseView(AqSafeBrowserView):
    """Base Portlets View for normal and specialized renderings.

    In portlet views, self.context is neither the portlet (self.portlet()),
    nor its datamodel (self.datamodel), but the object from/for which the
    portlet rendering is called (aka context_obj in most portlets related
    existing code).

    the whole_response attribute is set to True if the view instance is
    supposed to perform the whole response (typicaly looked up by a direct
    traversal for ESI, AJAX/JSON or feeds), and defaults to False.
    """

    whole_response = False

    def __init__(self, datamodel, request):
        AqSafeBrowserView.__init__(self, datamodel, request)
        self.datamodel = datamodel
        self.context = datamodel.getContext()
        self.prepared = False

    def prepare(self):
        """To subclass, for preparations that need to be done after __init__.

        For instance, __init__ occurs during traversal, but the authenticated
        user is resolved after traversing is done.
        This is usually called from CPSPortlet.render()
        """
        self.prepared = True

    def responseHeaders(self):
        """Set the headers in case the view does the whole rendering.

        Suitable default for rendering as an HTML fragment (ESI, AJAX...)"""
        self.request.RESPONSE.setHeader('Content-Type', 'text/html')

    def context_obj(self):
        return self.datamodel.getContext()

    getContextObj = context_obj

    def portlet(self):
        return self.datamodel.getObject()

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

    def url_tool(self):
        utool = self.aqSafeGet('_url_tool', None)
        if utool is None:
            utool = getToolByName(self.context, 'portal_url')
            self.aqSafeSet('_url_tool', utool)
        return utool

    def base_url(self):
        return self.url_tool().getBaseUrl()

    def l10nPortletTitle(self):
        return self.getCpsMcat()(self.datamodel['Title'])

    def portletDescription(self):
        return self.datamodel['Description']

    def rpathToDataModel(self, rpath):
        """Return the DataModel for a proxy document at rpath."""
        try:
            proxy = self.aqSafeGet('portal').restrictedTraverse(rpath)
            if proxy is None:
                return
            doc = proxy.getContent()
            return doc.getDataModel(proxy=proxy)
        except Unauthorized:
            # in theory, it is possible to access, e.g, brain information
            # without accessing the object itself. This is exceptional and
            # happens only if the security index would be bypassed par
            # custom code or would be somewhat broken
            logger.warn("User %r unauthorized to access content at %r. "
                        "See traceback to know how it got looked up",
                        user, rpath, exc_info=True)
        except (KeyError, AttributeError):
            logger.warn("Inconsistency: item %r not reachable or "
                        "cannot provide DataModel",
                        "See traceback to know how it got looked up",
                        rpath, exc_info=True)

    @classmethod
    def dateTimeFormat(self, dt, format):
        """Format a DateTime instance or a string parseable by DateTime.

        Abbreviation for this method:
        >>> dtf = BaseView.dateTimeFormat

        W3C format:
        >>> dtf(DateTime('2011/12/25'), 'W3CDTF')
        '2011-12-25T00:00:00Z'
        >>> dtf('2011/12/25', 'W3CDTF')
        '2011-12-25T00:00:00Z'

        Unknown format defaults to RFC 822:
        >>> dtf(DateTime('2011/12/25 EST'), 'Unknown')
        'Sun, 25 Dec 2011 00:00:00 -0500'

        Special cases:
        >>> dtf(None, 'W3CDTF') is None
        True
        >>> dtf(None, 'Unknown') is None
        True
        """

        if dt is None:
            return None
        if isinstance(dt, basestring):
            dt = DateTime(dt)
        format = DATETIME_FORMATS.get(format)
        if format is None:
            return dt.rfc822() # makes a good default
        return dt.strftime(format)

    def dataStructure(self):
        """Return a prepared DataStructure instance for request and context.

        This method is a convenience for quick conversion of legacy portlet
        widgets to view renderings. Script skins that were called from such
        widget templates can still be used, provided that one feeds them a
        datastructure.

        Using datastructures to represent the portlet parameters is now
        strongly discouraged. That's why this method sends deprecation
        warnings.

        This is a simplified version of what happens in FlexibleTypeInformation
        Request query parameters are taken into account, just in case.
        Session isn't.
        """

        warnings.warn("Access to portlet parameters through a DataStructure"
                      "is deprecated. You should rely on view.datamodel "
                      "instead", DeprecationWarning, 2)
        portlet = self.portlet()
        fti = portlet.getTypeInfo()
        layouts = (fti.getLayout(lid, portlet) for lid in fti.getLayoutIds())

        ds = DataStructure(datamodel=self.datamodel)
        for layout in layouts:
            layout.prepareLayoutWidgets(ds)
        ds.updateFromMapping(self.request.form)
        return ds
