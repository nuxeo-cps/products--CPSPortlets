# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Julien Anguenot <ja@nuxeo.com>
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

"""Patch on CPSPortlet for File downloading

Here stands a patch for CPSDocument which is on ProxyBase within CPSCore
Thus it has to be on the document itself for Portlets since they are not proxies
"""

from zLOG import LOG, DEBUG

import Acquisition
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Image import File

from Products.CMFCore.permissions import View, ModifyPortalContent
from CPSPortlet import CPSPortlet

KEYWORD_DOWNLOAD_FILE = 'downloadFile'

def __getitem__(self, name):
        """Transparent traversal of the proxy to the real subobjects.

        Used for skins that don't take proxies enough into account.

        Parses URL revision switch of the form:
          mydoc/archivedRevision/n/...

        Parses URL translation switch of the form:
          mydoc/switchLanguage/<lang>/...

        Parses URLs for download of the form:
          mydoc/downloadFile/attrname/mydocname.pdf
        """
        ob = self
        if ob is None:
            raise KeyError(name)
        if name == KEYWORD_DOWNLOAD_FILE:
            downloader = FileDownloader(ob, self)
            return downloader.__of__(self)
        try:
            res = getattr(aq_base(ob), name)
        except AttributeError:
            try:
                #res = ob[name]
                res = None
            except (KeyError, IndexError, TypeError, AttributeError):
                raise KeyError, name
        if hasattr(res, '__of__'):
            # XXX Maybe incorrect if complex wrapping.
            res = aq_base(res).__of__(self)
        return res

CPSPortlet.__getitem__ = __getitem__

class FileDownloader(Acquisition.Explicit):
    """Intermediate object allowing for file download.

    Returned by a proxy during traversal of .../downloadFile/.

    Parses URLs of the form .../downloadFile/attrname/mydocname.pdf
    """

    ##__implements__ = (WriteLockInterface,)

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, ob, proxy):
        """
        Init the FileDownloader with the document and proxy to which it pertains.

        ob is the document that owns the file and proxy is the proxy of this
        same document
        """
        self.ob = ob
        self.proxy = proxy
        self.state = 0
        self.attrname = None
        self.file = None
        self.filename = None

    def __repr__(self):
        s = '<FileDownloader for %s' % `self.ob`
        if self.state > 0:
            s += '/'+self.attrname
        if self.state > 1:
            s += '/'+self.filename
        s += '>'
        return s

    def __bobo_traverse__(self, request, name):
        state = self.state
        ob = self.ob
        LOG('FileDownloader.getitem', DEBUG, "state=%s name=%s"
            % (state, name))
        if state == 0:
            # First call, swallow attribute
            if not hasattr(aq_base(ob), name):
                LOG('FileDownloader.getitem', DEBUG,
                    "Not a base attribute: '%s'" % name)
                raise KeyError(name)
            file = getattr(ob, name)
            if file is not None and not isinstance(file, File):
                LOG('FileDownloader.getitem', DEBUG,
                    "Attribute '%s' is not a File but %s" %
                    (name, `file`))
                raise KeyError(name)
            self.attrname = name
            self.file = file
            self.state = 1
            return self
        elif state == 1:
            # Got attribute, swallow filename
            self.filename = name
            self.state = 2
            self.meta_type = getattr(self.file, 'meta_type', '')
            return self
        elif name in ('index_html', 'absolute_url', 'content_type',
                      'HEAD', 'PUT', 'LOCK', 'UNLOCK',):
            return getattr(self, name)
        else:
            raise KeyError(name)

    security.declareProtected(View, 'absolute_url')
    def absolute_url(self):
        url = self.proxy.absolute_url() + '/' + KEYWORD_DOWNLOAD_FILE
        if self.state > 0:
            url += '/' + self.attrname
        if self.state > 1:
            url += '/' + self.filename
        return url

    security.declareProtected(View, 'content_type')
    def content_type(self):
        if self.state != 2:
            return None
        return self.file.content_type

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """Publish the file or image."""
        if self.state != 2:
            return None
        file = self.file
        if file is not None:
            return file.index_html(REQUEST, RESPONSE)
        else:
            RESPONSE.setHeader('Content-Type', 'text/plain')
            RESPONSE.setHeader('Content-Length', '0')
            return ''

    # Attribut checked by ExternalEditor to know if it can "WebDAV" on this
    # object.
    def EditableBody(self):
        if self.state != 2:
            return None
        file = self.file
        if file is not None:
            return str(self.file.data)

    security.declareProtected(View, 'HEAD')
    def HEAD(self, REQUEST, RESPONSE):
        """Retrieve the HEAD information for HTTP."""
        if self.state != 2:
            return None
        file = self.file
        if file is not None:
            return file.HEAD(REQUEST, RESPONSE)
        else:
            RESPONSE.setHeader('Content-Type', 'text/plain')
            RESPONSE.setHeader('Content-Length', '0')
            return ''

    security.declareProtected(ModifyPortalContent, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP (and presumably FTP?) PUT requests (WebDAV)."""
        LOG('FileDownloader', DEBUG, "PUT()")
        if self.state != 2:
            LOG('ProxyBase', DEBUG, "BadRequest: Cannot PUT with state != 2")
            raise 'BadRequest', "Cannot PUT with state != 2"
        document = self.proxy
        file = getattr(document, self.attrname)
        response = file.PUT(REQUEST, RESPONSE)
        # If the considered document is a CPSDocument we must use the edit()
        # method since this method does important things such as setting dirty
        # flags on modified fields.
        # XXX: Note that using edit() modifies the file attribute twice.
        # We shouldn't use the file.PUT() method but it is helpful to get the
        # needed response object.
        if getattr(aq_base(document), '_has_generic_edit_method', 0):
            document.edit({self.attrname: file})
        return response

    security.declareProtected(ModifyPortalContent, 'LOCK')
    def LOCK(self, REQUEST, RESPONSE):
        """Handle HTTP (and presumably FTP?) LOCK requests (WebDAV)."""
        LOG('FileDownloader', DEBUG, "LOCK()")
        if self.state != 2:
            LOG('ProxyBase', DEBUG, "BadRequest: Cannot LOCK with state != 2")
            raise 'BadRequest', "Cannot LOCK with state != 2"
        document = self.proxy
        file = getattr(document, self.attrname)
        return file.LOCK(REQUEST, RESPONSE)

    security.declareProtected(ModifyPortalContent, 'UNLOCK')
    def UNLOCK(self, REQUEST, RESPONSE):
        """Handle HTTP (and presumably FTP?) UNLOCK requests (WebDAV)."""
        LOG('FileDownloader', DEBUG, "UNLOCK()")
        if self.state != 2:
            LOG('ProxyBase', DEBUG, "BadRequest: Cannot UNLOCK with state != 2")
            raise 'BadRequest', "Cannot UNLOCK with state != 2"
        document = self.proxy
        file = getattr(document, self.attrname)
        return file.UNLOCK(REQUEST, RESPONSE)

    def wl_lockValues(self, killinvalids=0):
        """Handle HTTP (and presumably FTP?) wl_lockValues requests (WebDAV)."""
        LOG('FileDownloader', DEBUG, "wl_lockValues()")
        if self.state != 2:
            LOG('ProxyBase', DEBUG, "BadRequest: Cannot wl_lockValues with state != 2")
            raise 'BadRequest', "Cannot wl_lockValues with state != 2"
        document = self.proxy
        file = getattr(document, self.attrname)
        return file.wl_lockValues(killinvalids)

    def wl_isLocked(self):
        """Handle HTTP (and presumably FTP?) wl_isLocked requests (WebDAV)."""
        LOG('FileDownloader', DEBUG, "wl_isLocked()")
        if self.state != 2:
            LOG('ProxyBase', DEBUG, "BadRequest: Cannot wl_isLocked with state != 2")
            raise 'BadRequest', "Cannot wl_isLocked with state != 2"
        document = self.proxy
        file = getattr(document, self.attrname)
        return file.wl_isLocked()

InitializeClass(FileDownloader)
