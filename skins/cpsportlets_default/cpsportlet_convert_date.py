##parameters=datetime='', fmt=''


if not fmt:
    return datetime

datetime = DateTime(datetime)

if fmt == 'W3CDTF':
    dfmt = '%Y-%m-%dT%H:%M:%SZ'

elif fmt == 'rfc822':
    return datetime.rfc822()

return datetime.strftime(dfmt)
