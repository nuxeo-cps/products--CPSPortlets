# -*- coding: iso-8859-15 -*-
# (C) Copyright 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: treenodeview.py 32919 2006-02-17 09:44:05Z tziade $
"""
  Z3-style helper to render a portlet
"""
# from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class PortletView(BrowserView):

    def render(self, portlet_id):
        portlets = getToolByName(self.context, 'portal_cpsportlets')
        if portlet_id in portlets.objectIds():
            return portlets[portlet_id].render(context_obj=self.context)

        portlets = getToolByName(self.context, '.cps_portlets')
        if portlet_id in portlets.objectIds():
            return portlets[portlet_id].render(context_obj=self.context)

        raise KeyError(portlet_id)
