=========================
CPSPortlets Documentation
=========================

:Revision: $Id$

.. sectnum::    :depth: 4
.. contents::   :depth: 4


General Documentation
=====================

- `Goals <goals.html>`_
- `Assigning styles to portlets <portlet-styling.html>`_
- `Portlet creation guidelines <portlet-creation-guidelines.html>`_


Implementation
==============

Implementation notes:

- CPSPortlet: Base class for all portlets. Child of CPSDocument.
  It means you can use the schemas / layouts machinery with the
  portlets. Notice one portlet == one portal_type now.

  The FlexibleTypeInformation is patched and holds now a
  ``cps_is_portlet`` property so that it's easy to filter the
  portal_type defined to be portlets.

  It means for a portlet will have schemas and layouts (generics
  and specifics) with eventually specific widgets. (most of the
  time) Check the PortletWidgets sub-folder (``README.txt``)

- PortletsContainer: Container (BTreeFolder2) holding the
  portlets. Store, create, delete portlets. Simple API

  PortletsContainer are placeful. They are used to store local
  portlet configurations overriding or extending global portlet
  configuration. The id used within CPS for those is
  ``.cps_portlets``

- PortletsTool: Inherits PortletsContainer and redefines methods
  to cope with global and local portlets. Global portlets are
  stored within


Miscellaneous
=============

- Schemas / Layouts / Vocabularies / FTIs are defined within the
  skins.


Comments
========

- Notice CPSPortlets deals only with portlet content. CPSSkins
  take care of the way it is displayed the cache etc...


Internals
=========

- `RAM Cache <cpsportlets-cache.html>`_
- `Portability to CMF, Plone <cpsportlets-portability.html>`_
- `Installing portlets with CPSInstaller <cpsinstaller.html>`_



.. Local Variables:
.. mode: rst
.. End:
.. vim: set filetype=rst: