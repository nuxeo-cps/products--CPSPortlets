$Id$

Here, are defined the specific widgets to the different portlets.
Don't mess up this folder ! Define one widget in one module and then import
it properly from the __init__py from the CPSPortlets component.
Do the widget registration within the module holding the widget. (not
within the __init__.py)

If the widgets you wrote are generic enough to be used within documents then
move it to CPSSchemas.
