##parameters=context_obj=None, **kw

if context_obj is None:
    return

rendered = []

ti =  context_obj.getTypeInfo()
if ti is None:
    return ''

if ti.getProperty('cps_is_portlet', 0):
    return ''

ds = kw['datastructure']
layout_ids = ds.get('layout_ids')

getContent = getattr(context_obj.aq_explicit, 'getContent', None)
if getContent is not None:
    doc = getContent()
    # find the 'render' method
    render = getattr(doc, 'render', None)
    if render is None:
        return ''

    if len(layout_ids) > 0:
        # try to render the specified layouts
        try:
            for layout_id in layout_ids:
                rendered.append(
                    render(proxy=context_obj, layout_id=layout_id)
                )
        except ValueError:
            return ''
    else:
        rendered.append(render(proxy=context_obj))

return ''.join(rendered)
