##parameters=layout=None, **kw

rendered = ''
for row in layout['rows']:
    for cell in row:
        rendered += cell['widget_rendered']

return rendered
