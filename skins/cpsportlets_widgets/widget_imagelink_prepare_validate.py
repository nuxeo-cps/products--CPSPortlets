##parameters=mode, datastructure, post_validate=1

if mode != 'validate':
    # we handle only validation
    return

if post_validate:
    # we do nothing on post validation
    return 1

return 1
