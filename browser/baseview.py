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

def parent(obj):
    """For readability."""
    return aq_parent(aq_inner(obj))

class BaseView(AqSafeBrowserView):
    """Base Portlets View for normal and specialized renderings."""

    prepared = False

    def __init__(self, context, request):
        AqSafeBrowserView.__init__(self, context, request)

    def prepare(self):
        """Preparation that can't be done in __init__

        These initializations are likely to require the authenticated user to
        be initialized, which happens after the traversal, during which the
        view class instantiation occurs.
        """
        if self.prepared:
            return
        portlet = self.context.aq_inner
        self.aqSafeSet('portlet', portlet)
        self.datamodel = portlet.getDataModel(context=portlet)

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

    def context_obj(self):
        context_obj = self.aqSafeGet('context_obj', None)
        if context_obj is not None:
            return context_obj

        definition_folder = parent(parent(self.aqSafeGet('portlet')))
        req_trav = getattr(self.request, REQUEST_TRAVERSAL_KEY, None)
        if req_trav is None:
            return definition_folder
        rpath = '/'.join(req_trav)
        logger.debug("Rpath to context_obj: %r", rpath)
        try:
            context_obj = definition_folder.restrictedTraverse(rpath)
        except (KeyError, AttributeError):
            raise NotFound('/'.join((
                        definition_folder.absolute_url_path() + rpath)))

        self.aqSafeSet('context_obj', context_obj)
        return context_obj

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
