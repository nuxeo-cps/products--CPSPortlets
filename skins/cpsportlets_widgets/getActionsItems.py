##parameters=obj=None, categories=[], actions_order=[]

actions = context.REQUEST.get('cpsskins_cmfactions', None)
if actions is None:
    actions = context.portal_actions.listFilteredActionsFor(obj)

renderActionIcon = context.portal_cpsportlets.renderActionIcon

utool = context.portal_url
# Note: this will not work in CMF
base_url = utool.getBaseUrl()

actionitems = []
orderedActions = list(actions_order)
reorderedActions = []

for category in categories:
    if not actions.has_key(category):
        continue
    actions_by_cat = actions[category]
    for action in actions_by_cat:
        item = {'title': action['name'],
                 'url': action['url'],
                 'icon_tag': renderActionIcon(action_id=action['id'],
                     category=category,
                     base_url=base_url,
                     alt=action['name']),
                }
        # if action is not in the preordered list, append it as usual
        if not action['id'] in actions_order:
            actionitems.append(item)
        else:
            # replace the action id in the preordered list with the action 
            # vocabulary
            orderedActions[actions_order.index(action['id'])] = item

for action in orderedActions:
    # keep only actions that really exist (have been replaced with an item)
    if not isinstance(action, str):
        reorderedActions.append(action)

return reorderedActions + actionitems
