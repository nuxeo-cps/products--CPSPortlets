##parameters=obj=None, categories=[]

actions = context.REQUEST.get('cpsskins_cmfactions', None)
if actions is None:
    actions = context.portal_actions.listFilteredActionsFor(obj)

actionitems = {}
for category in categories:
    if not actions.has_key(category):
        continue
    actions_by_cat = actions[category]
    items = []
    for action in actions_by_cat:
        items.append({'title': action['name'],
                      'url': action['url'],
                     })
    actionitems[category] = items

return actionitems
