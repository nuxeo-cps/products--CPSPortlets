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
"""CPS Portlets Permissions

Here it's defined the specific permissions for the CPS Portlets

'Add Global Portlet': Permission to add new portlet at global scope (within portal)
'Add Local Portlet' : Perrmissions to add new portlet at local scrope

"""

from Products.CMFCore.CMFCorePermissions import setDefaultRoles

addGlobalPortlet = 'Add Global Portlet'
setDefaultRoles(addGlobalPortlet, ('Manager', 'Owner', 'Theme Manager',))

addLocalPortlet = 'Add Local Portlet'
setDefaultRoles(addLocalPortlet, ('Manager', 'Owner',))
