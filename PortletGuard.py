# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Nuxeo SAS <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology
#               <http://www.chalmers.se>
# Authors:
# Hervé Cauwelier <hc@nuxeo.com>
# Jean-Marc Orliaguet <jmo@ita.chalmers.se>
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
# $Id$
"""Portlet Guard
"""

import logging

import sys
import types
from Globals import DTMLFile
from Globals import InitializeClass
from Products.PageTemplates.Expressions import getEngine
try:
    from zope.tales.tales import CompilerError
except ImportError:
    # BBB: Zope < 2.10
    from Products.PageTemplates.TALES import CompilerError
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.Guard import Guard

logger = logging.getLogger('Products.CPSPortlets.PortletGuard')

def createExpressionContext(sm, portlet, context):
    """Create a name space for TALES expressions."""
    utool = getToolByName(context, 'portal_url')
    portal = utool.getPortalObject()
    request = getattr(context, 'REQUEST', None)
    published = ''
    if request is not None:
        published_obj = request.get('PUBLISHED')
        if published_obj is not None:
            try:
                if isinstance(published_obj, types.MethodType):
                    # z3 view?
                    if published_obj.im_func.func_name == 'view_html':
                        # Convention for default view method name
                        # XXX Could check request['URL'] too
                        ob = request['PARENTS'][1]
                        published = ob.getTypeInfo().queryMethodID('view', '')
                else:
                    published = published_obj.getId()
            except AttributeError:
                pass
    data = {
        'portlet': portlet,
        'here': context,
        'portal': portal,
        'request': request,
        'published': published,
        'rpath_slash': utool.getRpath(context) + '/',
        'user': sm.getUser(),
        'nothing': None,
        }
    return getEngine().getContext(data)

class PortletGuard(Guard):
    """DCWorkflow Guard with a portlet-specific name space and an improved form.
    """

    guardForm = DTMLFile('zmi/guard', globals())

    def check(self, sm, portlet, context):
        """Checks conditions in this guard."""
        pp = self.permissions
        if pp:
            found = 0
            for p in pp:
                if sm.checkPermission(p, context):
                    found = 1
                    break
            if not found:
                return 0
        roles = self.roles
        if roles:
            # Require at least one of the given roles.
            found = 0
            u_roles = sm.getUser().getRolesInContext(context)
            for role in roles:
                if role in u_roles:
                    found = 1
                    break
            if not found:
                return 0
        expr = self.expr
        if expr is not None:
            econtext = createExpressionContext(sm, portlet, context)
            try:
                res = expr(econtext)
            except (NameError, CompilerError, AttributeError), e:
                utool = getToolByName(context, 'portal_url')
                logger.warn("Problem for portlet at %s, \"%s\" => %s: %s",
                            utool.getRpath(portlet),
                            expr.text.strip(), sys.exc_info()[0], e)
                return 0
            if not res:
                return 0
        return 1

    def dictExport(self):
        """Export the guard structure"""
        dict = {
            'guard_permissions': self.getPermissionsText(),
            'guard_roles': self.getRolesText(),
            'guard_group': self.getGroupsText(),
            'guard_expr': self.getExprText(),
            }
        return dict.items()

InitializeClass(PortletGuard)
