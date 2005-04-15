##parameters=obj=None, categories=[]

actions = context.REQUEST.get('cpsskins_cmfactions', None)
if actions is None:
    actions = context.portal_actions.listFilteredActionsFor(obj)

renderActionIcon = context.portal_cpsportlets.renderActionIcon

# XXX get base url from the request
base_url = context.getBaseUrl()

actionitems = {}
for category in categories:
    if not actions.has_key(category):
        continue
    actions_by_cat = actions[category]
    items = []
    for action in actions_by_cat:
        items.append(
            {'title': action['name'],
             'url': action['url'],
             'icon_tag': renderActionIcon(action_id=action['id'],
                 category=category,
                 base_url=base_url,
                 alt=''),
            })
    actionitems[category] = items

return actionitems
