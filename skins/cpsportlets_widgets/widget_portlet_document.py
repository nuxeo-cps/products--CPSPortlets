##parameters=context_obj=None, **kw

if context_obj is None:
    return

rendered = ''

ti =  context_obj.getTypeInfo()
if ti is None:
    return rendered

if ti.getProperty('cps_is_portlet', 0):
    return rendered

ds = kw['datastructure']

getContent = getattr(context_obj.aq_explicit, 'getContent', None)
if getContent is not None:
    doc = getContent()
    # find the 'render' method
    render = getattr(doc, 'render', None)
    if render is None:
        return rendered

    # render the document by cluster (if specified)
    if ds.has_key('cluster_id'):
        rendered = render(proxy=context_obj, cluster=ds['cluster_id'])
    else:
        rendered = render(proxy=context_obj)

return rendered
