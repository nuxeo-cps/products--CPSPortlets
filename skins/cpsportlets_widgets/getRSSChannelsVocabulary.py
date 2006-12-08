##parameters=key=None

items = []

portal_rss = getattr(context, 'portal_rss', None)
if portal_rss is not None:
    for channel in portal_rss.objectValues():
        channel_id = channel.getId()
        channel_title_or_id = channel.title_or_id()
        if key is not None and key == channel_id:
            return channel_title_or_id
        items.append((channel_id, channel_title_or_id))

return items
