##parameters=layout=None, **kw
rendered = []
for row in layout['rows']:
    for cell in row:
        rendered.append(cell['widget_rendered'])

result = ''.join(rendered)
if result == '':
    return ''

if result.startswith("<?xml"):
    return result
else:
    return '<div id="%s">%s</div>' % (context.getId(), result)
