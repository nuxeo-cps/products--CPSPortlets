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

# render the container
render_obj = context_obj.aq_inner.aq_explicit
if int(ds.get('render_container', 0)):
    if not render_obj.isPrincipiaFolderish:
        render_obj = context_obj.aq_parent.aq_inner

getContent = getattr(render_obj, 'getContent', None)
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
