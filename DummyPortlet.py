# (C) Copyright 2009 Georges Racinet
# Author: Georges Racinet <georges@racinet.fr>
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

"""A very simple object used to dump content in cases where the context
would expect a CPSPortlet instance.

Can be useful for various unit testing purposes,
as well as some special rendering modes (theme export, profiling pages without
the portlet rendering, etc.)
"""

class DummyPortlet:

    def __init__(self, obj_id, rendered, title=''):
        self.title = title
        self.id = obj_id
        self.rendered = rendered

    def getId(self):
        return self.id

    def Title(self):
        return self.title

    def title_or_id(self):
        return self.title or self.id

    def render_cache(self, **kw):
        return self.rendered
