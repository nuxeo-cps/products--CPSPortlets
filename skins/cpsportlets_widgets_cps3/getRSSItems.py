##parameters=channel, max_items=0, max_words=0

channel = getattr(context.portal_rss, channel, None)

if channel is None:
    return []

data = channel.getData(max_items)

items = []

data_items = data['lines']
if max_words == 0:
    return data_items

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
    description = summarize(item['description'], max_words)
    data_items[pos].update({'description': description})
    pos += 1

return data_items
