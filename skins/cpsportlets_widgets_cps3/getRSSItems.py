##parameters=channel, max_items=None

channel = getattr(context.portal_rss, channel, None)

if channel is None:
    return []

data = channel.getData(max_items)
return data['lines']
