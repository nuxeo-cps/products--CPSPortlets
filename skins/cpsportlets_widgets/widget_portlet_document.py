##parameters=context_obj=None, **kw

if context_obj is None:
    return

rendered = ''

ti =  context_obj.getTypeInfo()
if ti is None:
    return rendered

if ti.getProperty('cps_is_portlet', 0):
    return rendered

getContent = getattr(context_obj.aq_explicit, 'getContent', None)
if getContent is not None:
    doc = getContent()
    rendered = doc.render(proxy=context_obj)

return rendered

