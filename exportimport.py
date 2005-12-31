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
"""Portlets I/O XML Adapter.
"""

from Acquisition import aq_base
from zope.app import zapi
from zope.component import adapts
from zope.interface import implements
import Products
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.CPSPortlets.interfaces import IPortletTool
from Products.CPSPortlets.interfaces import IPortletContainer
from Products.CPSPortlets.interfaces import IPortlet


_marker = object()

TOOL = 'portal_cpsportlets'
NAME = 'portlets'

def exportPortletTool(context):
    """Export portlet tool and portlets a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importPortletTool(context):
    """Import portlet tool and portlets from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)


class PortletToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                            PropertyManagerHelpers):
    """XML importer and exporter for portlet tool.
    """

    adapts(IPortletTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractCacheParameters())
        node.appendChild(self._extractObjects())
        self._logger.info("Portlet tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeCacheParameters()
            self._purgeObjects()
        self._initProperties(node)
        self._initCacheParameters(node)
        self._initObjects(node)
        self._logger.info("Portlet tool imported.")

    node = property(_exportNode, _importNode)

    def _extractCacheParameters(self):
        fragment = self._doc.createDocumentFragment()
        cache_params = self.context.getCacheParameters().items()
        cache_params.sort()
        for portlet_type, params in cache_params:
            node = self._doc.createElement('cache-parameters')
            node.setAttribute('type', portlet_type)
            for param in params:
                if not param:
                    continue
                paramnode = self._doc.createElement('parameter')
                textnode = self._doc.createTextNode(param)
                paramnode.appendChild(textnode)
                node.appendChild(paramnode)
            fragment.appendChild(node)
        return fragment

    def _purgeCacheParameters(self):
        self.context.initializeCacheParameters()

    def _initCacheParameters(self, node):
        tool = self.context
        cache_params = {}
        for child in node.childNodes:
            if child.nodeName != 'cache-parameters':
                continue
            portlet_type = str(child.getAttribute('type'))
            params = []
            for subchild in child.childNodes:
                if subchild.nodeName != 'parameter':
                    continue
                param = str(self._getNodeText(subchild))
                params.append(param)
            cache_params[portlet_type] = params
        tool.updateCacheParameters(cache_params)


class PortletContainerXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    """XML importer and exporter for a portlet container.
    """

    adapts(IPortletContainer, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractObjects())
        self._logger.info("%s portlets exported." %
                          '/'.join(self.context.getPhysicalPath()))
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeObjects()
        self._initObjects(node)
        self._logger.info("%s portlets imported." %
                          '/'.join(self.context.getPhysicalPath()))

    node = property(_exportNode, _importNode)


class PortletXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML importer and exporter for a portlet.
    """

    adapts(IPortlet, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        return self._getObjectNode('object', False)

    def _importNode(self, node):
        """Import the object from the DOM node.
        """

    node = property(_exportNode, _importNode)
