##parameters=obj=None, categories=[], actions_order=[]
import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('cps_portlet_widgets.getActionItems')

DEFAULT_PRIORITY = 200

actions = context.REQUEST.get('cpsskins_cmfactions', None)

if actions is None:
    actions = context.portal_actions.listFilteredActionsFor(obj)

renderActionIcon = context.portal_cpsportlets.renderActionIcon

utool = context.portal_url
# Note: this will not work in CMF
base_url = utool.getBaseUrl()

atool = getToolByName(context, 'portal_actionicons', None)

actionitems = []
orderedActions = list(actions_order)
reorderedActions = []
unordereditems = []

for category in categories:
    if not actions.has_key(category):
        continue
    actions_by_cat = actions[category]
    logger.debug('Actions for category %r: %r', category, actions_by_cat)
    for action in actions_by_cat:
        item = {'title': action['title'],
                 'url': action['url'],
                 'icon_tag': renderActionIcon(action_id=action['id'],
                     category=category,
                     base_url=base_url,
                     alt=action['title']),
                }
        if 'onclick' in action:
            item['onclick'] = action['onclick']
        item['priority'] = DEFAULT_PRIORITY
        if atool is not None:
            info = atool.queryActionInfo(category, action['id'])
            if info is not None:
                item['priority'] = info[1]

        if not action['id'] in actions_order:
            actionitems.append(item)
        else:
            # replace the action id in the preordered list with the action
            # vocabulary
            orderedActions[actions_order.index(action['id'])] = item

for action in orderedActions:
    # keep only actions that really exist (have been replaced with an item)
    if not isinstance(action, basestring):
        reorderedActions.append(action)

# Sort the unsorted ones:
actionitems.sort( lambda x, y: cmp( x.get( 'priority', 0 )
                                       , y.get( 'priority', 0 )
                                       ) )

return reorderedActions + actionitems
