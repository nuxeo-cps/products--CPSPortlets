##parameters=permalink='', datetime=''

"""<link rel="alternate"> is always the permalink of the entry
http://diveintomark.org/archives/2004/05/28/howto-atom-id - article
about constructing id
"""

import re

urlregexp = r"^(http://|https://)([^/:]+):?(\d+)?(/.*)$"
m = re.search(urlregexp, permalink)
if m:
    location, port, path = m.groups()[1:]
    path = path.split('?')[0]
    uid = 'tag:' + location + ',' + DateTime(datetime).strftime('%Y-%m-%d') + ':' + path
    return uid
return permalink
