##parameters=portlet=None, random_int=0, **kw

js_code = """
<script type="text/javascript"><!--
showimage('%s');
//--></script>
"""

widget_id = 'imagelink'
if random_int:
    widget_id += '_%s' % str(random_int)

selector_id = '%s_%s_widget' % (portlet.getId(), widget_id)

return js_code % selector_id
