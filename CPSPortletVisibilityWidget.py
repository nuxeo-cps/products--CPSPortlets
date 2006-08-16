# -*- coding: iso-8859-15 -*-
# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 Chalmers University of Technology
#               <http://www.chalmers.se>
# Author: Jean-Marc Orliaguet <jmo@ita.chalmers.se>
# Original author: Florent Guillaume <fg@nuxeo.com>
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
"""CPS Portlet Visibility Widget

A widget for setting portlet visibility ranges.
"""

from Globals import InitializeClass
from cgi import escape

from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.Widget import widgetRegistry

from Products.CPSSchemas.BasicWidgets import renderHtmlTag, CPSSelectWidget

##################################################

class CPSPortletVisibilityWidget(CPSSelectWidget):
    """CPS Portlet Visibility widget."""
    meta_type = 'CPS Portlet Visibility Widget'

    field_types = ('CPS Couple Field',)

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]

        # value is formatted as 'start-end'
        # where 'start' and 'end' are integers.
        v = value.split('-')
        start = None
        end = None

        err = 0
        if len(v) <= 1:
            err = 1

        # convert 'start' to int
        if not err:
            try:
                start = int(v[0])
            except ValueError:
                err = 1

        # convert 'end' to int
        if not err:
            try:
                end = int(v[1])
            except ValueError:
                err = 1

        # check value boundaries
        if start is not None and end is not None:
            if (end < 0) or (start < 0) or (end > 0 and end < start):
                err = 1

        if err:
            datastructure.setError(widget_id, "cpsschemas_err_select")
            return 0
        vocabulary = self._getVocabulary(datastructure)
        if not vocabulary.has_key(value):
            datastructure.setError(widget_id, "cpsschemas_err_select")
            return 0

        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = [start, end]
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        vocabulary = self._getVocabulary(datastructure)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.translation_service
        charset = portal.default_charset
        if mode == 'view':
            if getattr(self, 'translated', None):
                value = cpsmcat(vocabulary.getMsgid(value, value))
                if charset != 'unicode':
                    value = value.encode(charset, 'ignore')
                return escape(value)
            else:
                return escape(vocabulary.get(value, value))
        elif mode == 'edit':
            res = renderHtmlTag('select',
                                name=self.getHtmlWidgetId())
            in_selection = 0
            for k, v in vocabulary.items():
                if getattr(self, 'translated', None):
                    v = cpsmcat(vocabulary.getMsgid(k, k))
                    if charset != 'unicode':
                        v = v.encode(charset, 'ignore')
                    kw = {'value': k, 'contents': v}
                else:
                    kw = {'value': k, 'contents': v}
                if '%s-%s' % (value[0], value[1]) == k:
                    kw['selected'] = 'selected'
                    in_selection = 1
                res += renderHtmlTag('option', **kw)
            if value and not in_selection:
                kw = {'value': value, 'contents': 'invalid: '+repr(value),
                      'selected': 'selected'}
                res += renderHtmlTag('option', **kw)
            res += '</select>'
            return res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSPortletVisibilityWidget)

widgetRegistry.register(CPSPortletVisibilityWidget)
