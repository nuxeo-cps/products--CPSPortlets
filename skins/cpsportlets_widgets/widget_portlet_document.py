##parameters=context_obj=None, **kw

if context_obj is None:
    return

rendered = ''

ds = kw['datastructure']

# render the container
render_obj = context_obj.aq_inner.aq_explicit
if int(ds.get('render_container', 0)):
    if not render_obj.isPrincipiaFolderish:
        render_obj = context_obj.aq_parent.aq_inner

ti =  render_obj.getTypeInfo()
if ti is None:
    return rendered

if ti.getProperty('cps_is_portlet', 0):
    return rendered

getContent = getattr(render_obj, 'getContent', None)
if getContent is not None:
    doc = getContent()
    # find the 'render' method
    render = getattr(doc, 'render', None)
    if render is None:
        return rendered

    # render the document by cluster (if specified)
    if ds.has_key('cluster_id'):
        cluster_id = ds['cluster_id']
        # check whether the cluster exists.
        # XXX: this could be done in CPSDocument.FlexibleTypeInformation.py
        if ds.get('cluster_no_fallback'):
            found = 0
            for cluster in ti.getProperty('layout_clusters'):
                cl, v = cluster.split(':')
                if cl == cluster_id:
                    found = 1
                    break
            if not found:
                return ''
        rendered = render(proxy=context_obj, cluster=cluster_id)
    else:
        rendered = render(proxy=context_obj)

return rendered
