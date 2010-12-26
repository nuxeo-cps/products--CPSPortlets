# Copyright (c) 2004-2009 Nuxeo SA <http://nuxeo.com>
# Copyright (c) 2004-2009 Chalmers University of Technology <http://www.chalmers.se>
# Authors:
# Julien Anguenot <ja@nuxeo.com>
# Jean-Marc Orliaguet <jmo@ita.chalmers.se>
# M.-A. Darche <madarche@nuxeo.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# $Id$

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

"""Portlets Container
"""

from logging import getLogger

from zope.interface import implements

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
from Products.CMFCore.utils import getToolByName

from Products.CPSUtil.id import generateId
from Products.CPSPortlets.interfaces import IPortletContainer


logger = getLogger(__name__)

class PortletsContainer(CMFBTreeFolder):
    """ Portlets Container
    """

    implements(IPortletContainer)

    meta_type = 'CPS Placeful Portlets Container'
    portal_type = meta_type

    security = ClassSecurityInfo()

    def __init__(self, id=None):
        """
        """
        if id is None:
            id = self.id
        CMFBTreeFolder.__init__(self, id)

    def _get_id(self, id):
        """Override OFS.CopySupport._get_id to generate
           unique portlet ids with the 'portlet_' prefix.

           # Allow containers to override the generation of
           # object copy id by attempting to call its _get_id
           # method, if it exists.
        """
        ptltool = getToolByName(self, 'portal_cpsportlets')

        ok = 0
        while not ok:
            new_id = self.generateId(prefix='portlet_',
                                     suffix='',
                                     rand_ceiling=999999999)
            ok = ptltool.checkIdentifier(new_id)
        return new_id

    ####################################################################

    def getPortletById(self, id):
        """Return a portlet object given an id
        """
        return self.get(id)

    def listPortlets(self):
        """Return the list of portlet objects
        """

        portlets = []
        ids = self.listPortletIds()
        for id in ids:
            portlets.append(self.getPortletById(id))
        return portlets

    def listPortletIds(self):
        """Return the list of all portlet ids contained within the tool
        """
        ids = []
        for k, v in self.items():
            portlet = self.getPortletById(k)
            if not hasattr(aq_base(portlet), 'isCPSPortlet'):
                continue
            if not portlet.isCPSPortlet():
                continue
            ids.append(k)
        return ids

    ####################################################################

    def _createPortlet(self, ptype_id, **kw):
        """Create a new portlet given its portal_type

        If the given (or computed if none given) identifier is not unique,
        None is returned and the portlet is not created. The reason is that
        updates would otherwise be wrong afterward.
        """
        #logger.debug("kw = %s" % str(kw))
        ptltool = getToolByName(self, 'portal_cpsportlets')
        tstool = getToolByName(self, 'translation_service')
        portlet_id = ''

        if kw.has_key('identifier'):
            # In this case a new identifier must not be computed.
            # It is OK or NOT with the given identifier.
            portlet_id = kw.get('identifier')
            unique = ptltool.checkIdentifier(portlet_id)
            if not unique:
                return None

        if kw.has_key('Title'):
            portlet_id = kw.get('Title')
            # Defaulting to the default language of the translation service
            # which should be the default language of the portal to find out
            # which words are meaningless to not put those words in the portlet IDs.
            meaningless_words = tstool.translateDefault('words_meaningless',
                                                        target_language=None).split()
            portlet_id = generateId(portlet_id, max_chars=24,
                                    lower=True,
                                    meaningless_words=meaningless_words)
        while True:
            if portlet_id:
                unique = ptltool.checkIdentifier(portlet_id)
                if unique:
                    break
            portlet_id = self.generateId(prefix=portlet_id,
                                         suffix='',
                                         rand_ceiling=999999999)

        # Then creating the portlet
        self.invokeFactory(ptype_id, portlet_id)
        new_portlet = getattr(self, portlet_id)
        # Setting the portlet's internal identifier.
        # It is used to identify portlets uniquely no matter which container
        # they are located in, for instance when you do copy and paste between
        # containers, unique ids per container are not enough. the id is similar
        # to the document id in portal_repository except that it is stored in
        # the portlet's catalog portlets are also documents so they need a Zope
        # id (which is more cosmetic than anything else).
        kw['identifier'] = portlet_id
        # Setting the portlet's guard
        if kw.has_key('guard'):
            new_portlet.setGuardProperties(props=kw.get('guard'))
            del kw['guard']
        new_portlet.edit(kw)
        # Rebuilding the portlet to add javascript and cache parameters
        new_portlet._rebuild()
        return portlet_id

    def _deletePortlet(self, portlet_id):
        """Delete a portlet given its id
        """
        if portlet_id in self.listPortletIds():
            self._delObject(portlet_id)
            return 0
        return 1

    #####################################################################

    def listPortletSlots(self):
        """Return all the portlets slots
        """

        slots = []
        portlet_ids = self.listPortletIds()

        for id in portlet_ids:
            portlet = self.getPortletById(id)
            if getattr(aq_base(portlet), 'isCPSPortlet', None) is None:
                continue
            if not portlet.isCPSPortlet():
                continue
            slot = portlet.getSlot()
            if slot and slot not in slots:
                slots.append(slot)

        return slots

InitializeClass(PortletsContainer)

def addPortletsContainer(dispatcher, id='', REQUEST=None):
    """Add a CPS Portlets Container.
    """
    if not id:
        id = dispatcher.portal_cpsportlets.getPortletContainerId()
    ob = PortletsContainer(id)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
