##parameters=datastructure, mode, **kw

rendered = ''
widget_infos = kw.get('widget_infos')

images = []
for k, v in widget_infos.items():
    # find all Image Link widgets
    if k.startswith('imagelink'):
        images.append(v['widget'])
    # change widget view modes from 'hidden' to 'view'
    v['widget_mode'] = 'view'

nb_images = len(images)
# there is only one image
if nb_images == 1:
    rendered = images[0].render(mode=mode,
                                datastructure=datastructure,
                                widget_infos=widget_infos)
# there is more than one image
# do a client-side random rotation
elif nb_images > 1:
    # XXX
    rendered = 'not implemented yet'

return rendered
