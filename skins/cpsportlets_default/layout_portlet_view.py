##parameters=layout=None, **kw

rendered = []
for row in layout['rows']:
    for cell in row:
        rendered.append(cell['widget_rendered'])

return ''.join(rendered)
