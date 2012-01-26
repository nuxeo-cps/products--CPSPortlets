=========================
CPSPortlets Documentation
=========================

.. sectnum::    :depth: 4
.. contents::   :depth: 4

Updated for CPS 3.6

Introduction
============

What is a portlet ?
-------------------
In CPS, portlets are specialized renderers that can take care of

1. HTML page fragments. For instance, in the CPSDefault application, the
navigation menus, the breadcrumbs, the action menus, document
listings, and actually almost every dynamic area besides the main
content are portlets.

2. Whole data interchange responses, such as syndication formats or
server-side response to AJAX calls.

They are persistent and entirely meant to be managed by end users with
appropriate permissions. They can be local, i.e., attached to a folder
from the arboresence, including the portal itsef, or global (no
definition folder at all).

Configuration
-------------
They come in *types*. For example, the navigation menus are usually
Navigation Portlets, document listings are Content Portlets, and so on.

The configuration of a given portlet if totally flexible, depending on
its *type*, which plays the same role for configuration parameters
that document types play for user content. A typical portlet type will
define some parameters to control what to display and other to control
how.

From portlets to whole pages
----------------------------

Portlets meant for inclusion in HTML pages are organized in
*slots*, which are nothing but simple string markers. CPSPortlets
provides utilities to handle portlets from a given slot, filtered according
to *visibility rules*, but it is not CPSPortlets' job to decide to
render portlets from a slot, nor what to do with the renderings. These
are the responsibility of the theme engine (currently
CPSDesignerThemes, formerly CPSSkins).

Rendering kinds
---------------
A portlet type may have several rendering kinds. Up to CPS 3.5, this
used to be a feature provided by some portlet types, while it's been
made systematic within CPS 3.6.

In CPS 3.6, portlet renderings have been entirely refactored, and are
now implemented as ZTK-style views. In that move, care has been taken to keep
backwards compatibility; actually, as of CPS-3.6.0, most
CPSDefault's portlet types have not been ported to the new system yet.

A given portlet can also be rendered through several kinds : for
instance, the Content Portlet that lists published News Item documents
("Breaking news") does of course render an HTML fragment for inclusion
in the page, but also provides the corresponding Atom and RSS exports.

The application developer can create new rendering for all
portlet types. For example, one could develop podcast and XSPF
rendering kinds for Content Portlets. Of course these would work for
audio documents only. This also illustrates that some rendering kinds
may not be applicable according to other configuration parameters
(in that example, one would make it list audio documents only).

Performance
-----------
CPSPortlets provides a powerful and generic caching
engine for the renderings.
Invalidation is controlled by configuration, depending on the
portlet parameters and external conditions, such as the current virtual host,
or the authenticated user.

On top of that, there is also caching for the lookup logic.
All these caches are ZEO aware, meaning that invalidations will
propagate gracefully accross a whole ZEO cluser.

Table of contents
=================
TODO: review these pages, remove obsolete ones and write new ones.

- `Goals <goals.html>`_
- `Assigning styles to portlets <portlet-styling.html>`_
- `Portlet creation guidelines <portlet-creation-guidelines.html>`_
- `RAM Cache <cpsportlets-cache.html>`_
- `Portability to CMF, Plone <cpsportlets-portability.html>`_


.. Local Variables:
.. mode: rst
.. End:
.. vim: set filetype=rst:
