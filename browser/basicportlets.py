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

from Products.CMFCore.utils import getToolByName
from baseview import BaseView

class BreadCrumbsPortletView(BaseView):

    def breadcrumbs(self):
        """Return the breadcrumbs items."""

        # might be already cached in request
        breadcrumb_set = self.request.get('breadcrumb_set')
        if breadcrumb_set != None:
            return breadcrumb_set

        dm = self.datamodel
        utool = getToolByName(self.context, 'portal_url')
        return utool.getBreadCrumbsInfo(
            context=self.context_obj(),
            only_parents=dm.get('parent', False), # might not be in schema
            show_root=dm['display_site_root'],
            restricted=True,
            show_hidden_folders=dm['display_hidden_folders'],
            first_item=dm['first_item'], title_size=50)

    def context_url(self):
        utool = getToolByName(self.context, 'portal_url')
        return utool.getRelativeUrl(self.context_obj())
