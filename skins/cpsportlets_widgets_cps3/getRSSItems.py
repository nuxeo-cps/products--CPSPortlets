##parameters=**kw

rsstool = context.portal_rss

channel_id = kw.get('channel')
channel = getattr(rsstool.aq_inner.aq_explicit, channel_id, None)

if channel is None:
    return []

first_item = int(kw.get('first_item', 1))
max_items = int(kw.get('max_items', 0))
max_words = int(kw.get('max_words', 0))

DEFAULT_RSS_ITEM_DISPLAY = 'cpsportlet_rssitem_display'
render_method = kw.get('render_method') or DEFAULT_RSS_ITEM_DISPLAY
render_method = getattr(context, render_method, None)

data = channel.getData(max_items + first_item -1)
items = []

data_items = data['lines']
if first_item > 1:
    data_items = data_items[first_item-1:]

def summarize(text='', max_words=20):
    """summarize the text by returning the first max_words
    """
    if not max_words:
        return text
    if not text:
        return ''
    split_text = text.split(' ', max_words)[0:max_words]
    res = ''
    if split_text:
        res = ' '.join(split_text) + ' ...'
    return res

order = 0
for item in data_items:
    description = item['description']
    modified = item['modified']
    author = item['author']
    if not author:
        author = 'unknown'

    # Item rendering and display
    rendered = ''

    # render the item using a custom display method (.zpt, .py, .dtml)
    if render_method is not None:
        item['summary'] = summarize(description, max_words)
        kw.update({'item': item,
                   'order': order,
                  })
        rendered = apply(render_method, (), kw)

    # this information is used by custom templates that call getRSSItems()
    # directly.
    data_items[order].update(
        {'description': description,
         'rendered': rendered,
         'metadata':
            {'creator': author,
             'contributor': author,
             'date': modified,
             'issued': modified,
             'created': modified,
            },
        })
    order += 1

return data_items
