# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""Portlet interfaces.
"""

from zope.interface import Interface, Attribute
from Products.CMFCore.interfaces import ICatalogTool
from Products.CPSSchemas.interfaces import IWidget
from Products.CPSDocument.interfaces import ICPSDocument
from Products.CPSSchemas.interfaces import IDataModel

class ICPSPortlet(ICPSDocument):
    """A portlet is a CPSDocument with a guard attribute
    """
    guard = Attribute("Guard parameters or None")

class IPortletWidget(IWidget):
    """The main widget doing the rendering for a portlet.
    """

class IPortletContainer(Interface):
    """Portlet Container.
    """

class IPortletTool(IPortletContainer):
    """Portlet Tool.
    """

class IPortletCatalogTool(ICatalogTool):
    """Porlet Catalog Tool.
    """

## marker interfaces for concrete portlet types

class IBreadcrumbsPortletModel(IDataModel):
    """Breadcrumbs portlet."""

class IContentPortletModel(IDataModel):
    """Content portlet."""

class INavigationPortletModel(IDataModel):
    """Navigation portlet."""

class IDocumentPortletModel(IDataModel):
    """Document portlet."""

class ITextPortletModel(IDataModel):
    """Text portlet."""
