# -*- coding: iso-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Author : Julien Anguenot <ja@nuxeo.com>
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
"""Patch on the FlexibleTypeInformation from CMF

Adds property for being able to know if the Type is a portlet or not.
"""

from Products.CPSDocument.FlexibleTypeInformation import FlexibleTypeInformation \
     as FTI

if 'cps_is_portlet' not in [prop['id'] for prop in FTI._properties]:
    FTI._properties = FTI._properties + (
        {'id':'cps_is_portlet', 'type': 'boolean', 'mode':'w',
         'label':'CPS Portlet'},
        )
    FTI.cps_is_portlet = 0
