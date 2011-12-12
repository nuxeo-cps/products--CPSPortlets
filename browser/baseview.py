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
from zExceptions import NotFound
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CPSPortlets.CPSPortlet import REQUEST_TRAVERSAL_KEY
from Products.CPSonFive.browser import AqSafeBrowserView

logger = logging.getLogger(__name__)

class BaseView(AqSafeBrowserView):
    """Base Portlets View for normal and specialized renderings."""

    def __init__(self, datamodel, request):
        AqSafeBrowserView.__init__(self, datamodel, request)
        self.datamodel = datamodel
        self.context = datamodel.getContext()

    def context_obj(self):
        return self.datamodel.getContext()

    getContextObj = context_obj

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
