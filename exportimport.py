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
from ZODB.loglevels import BLATHER as VERBOSE
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.ZCatalog.exportimport import ZCatalogXMLAdapter
from Products.CPSDocument.exportimport import exportCPSObjects
from Products.CPSDocument.exportimport import importCPSObjects
from Products.CPSDocument.exportimport import CPSObjectManagerHelpers
from Products.CPSDocument.exportimport import CPSDocumentXMLAdapter
from Products.CPSPortlets.PortletsContainer import addPortletsContainer
from Products.CPSPortlets.PortletGuard import PortletGuard

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.CPSPortlets.interfaces import ICPSPortlet
from Products.CPSPortlets.interfaces import IPortletTool
from Products.CPSPortlets.interfaces import IPortletContainer


_marker = object()

NAME = 'portlets'

TOOL = 'portal_cpsportlets'
CATALOG_TOOL = 'portal_cpsportlets_catalog'
ROOT_PORTLETS = '.cps_portlets'

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

    # Export catalog
    catalog = getToolByName(site, CATALOG_TOOL, None)
    if catalog is not None:
        exportObjects(catalog, '', context)

    # Export root portlets
    root_portlets = getattr(site, ROOT_PORTLETS, None)
    if root_portlets is not None:
        exportCPSObjects(root_portlets, '', context)

def importPortletTool(context):
    """Import portlet tool and portlets from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)

    # Import catalog
    catalog = getToolByName(site, CATALOG_TOOL)
    importObjects(catalog, '', context)

    # Import root portlets
    if ROOT_PORTLETS not in site.objectIds():
        addPortletsContainer(site, ROOT_PORTLETS)
    root_portlets = getattr(site, ROOT_PORTLETS)
    importCPSObjects(root_portlets, '', context)


class CPSPortletXMLAdapter(CPSDocumentXMLAdapter):
    """XML importer and exporter for CPS Portlet

    add guard I/O to standard CPSDocumentXMLAdapter
    """
    adapts(ICPSPortlet, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractObjects())
        node.appendChild(self._extractDocumentFields())
        guard_node = self._extractPortletGuard()
        if guard_node is not None:
            node.appendChild(guard_node)
        msg = "Portlet %r exported." % self.context.getId()
        self._logger.log(VERBOSE, msg)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeObjects()
            self._purgeDocumentFields()
            self._purgePortletGuard()
        # Init fields before objects, as some None files may be objects
        # and need to be imported after their ini
        self._initDocumentFields(node)
        self._initObjects(node)
        self._initPortletGuard(node)
        msg = "Portlet %r imported." % self.context.getId()
        self._logger.log(VERBOSE, msg)

    def _extractPortletGuard(self):
        guard = self.context.getGuard()
        if guard is None:
            return
        node = self.createStrictTextElement("guard")
        node.setAttribute('roles', guard.getRolesText().encode('utf-8'))
        node.setAttribute('groups', guard.getGroupsText().encode('utf-8'))
        node.setAttribute('permissions',
                          guard.getPermissionsText().encode('utf-8'))
        self.setNodeText(node, guard.getExprText())
        return node

    def _initPortletGuard(self, node):
        ob = self.context
        guard_props = {}
        for child in node.childNodes:
            if not child.nodeName == 'guard':
                continue
            ob.guard = PortletGuard()
            guard_props['guard_permissions'] = child.getAttribute('permissions')
            guard_props['guard_roles'] = child.getAttribute('roles')
            guard_props['guard_groups'] = child.getAttribute('groups')
            guard_props['guard_expr'] = self.getNodeText(child)
            ob.guard.changeFromProperties(guard_props)

    def _purgePortletGuard(self):
        self.context.guard = None # XXX: or shall it be 'PortalGuard()'?


class PortletToolXMLAdapter(XMLAdapterBase, CPSObjectManagerHelpers,
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
                paramnode = self._doc.createElement('element')
                paramnode.setAttribute('value', param)
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
                if subchild.nodeName != 'element':
                    continue
                param = str(subchild.getAttribute('value'))
                params.append(param)
            cache_params[portlet_type] = params
        tool.updateCacheParameters(cache_params)


class PortletContainerXMLAdapter(XMLAdapterBase, CPSObjectManagerHelpers):
    """XML importer and exporter for a portlet container.
    """

    adapts(IPortletContainer, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME

    def __init__(self, context, environ):
        XMLAdapterBase.__init__(self, context, environ)
        # Don't keep initial dot in name, which hides it in the filesystem
        id = context.getId()
        if id[0] == '.':
            self.name = id[1:].replace(' ', '_')

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractObjects())
        msg = "Portlets %r exported."% '/'.join(self.context.getPhysicalPath())
        self._logger.log(VERBOSE, msg)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeObjects()
        self._initObjects(node)
        msg = "Portlets %r imported."% '/'.join(self.context.getPhysicalPath())
        self._logger.log(VERBOSE, msg)


class PortletCatalogToolXMLAdapter(ZCatalogXMLAdapter):
    adapts(IPortletContainer, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME
    name = 'portlets_catalog'
