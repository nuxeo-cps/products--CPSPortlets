##parameters=**kw

bcs = context.breadcrumbs()

result = []
for name, url in bcs:
    result.append( { 'id': name,
                     'title': name,
                     'url': url
                   }
                 )
return result

