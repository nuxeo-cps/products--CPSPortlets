##parameters=channel, first_item=1, max_items=0, max_words=0

channel = getattr(context.portal_rss, channel, None)

if channel is None:
    return []

data = channel.getData(max_items + first_item -1)
items = []

data_items = data['lines']
if first_item > 1:
    data_items = data_items[first_item-1:]

def summarize(text='', max_words=20):
    """summarize the text by returning the first max_words
    """
    split_text = text.split(' ', max_words)[0:max_words]
    res = ''
    if split_text:
        res = ' '.join(split_text) + ' ...'
    return res

# summarize the descriptions
pos = 0
for item in data_items:
    description = item['description']
    modified = item['modified']
    if max_words > 0:
        description = summarize(description, max_words)
    data_items[pos].update(
        {'description': description,
         'metadata':
            {'creator': item['author'],
             'date': modified,
             'created': modified,
            }
        })
    pos += 1

return data_items
