##parameters=**kw
"""Provide a fast and sane no-rendering default.

By default Content Portlets with render_method="" will actually call the
default CPSPortlet method (a template), of which we could actually not care
at all, because rendering is performed downstream by a custom template
attached to the Portlet View class

Instead of a miss, let's have a hopefully faster default void rendering.
"""
return ''
