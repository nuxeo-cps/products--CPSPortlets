##parameters=portlet=None, **kw

js_code = """
<script type="text/javascript"><!--
var rand = get_random(%s);
if (rand > 0) rand = rand + '_'; else rand = '';
showimage('%s_imagelink_' + rand + 'widget');
//--></script>
"""

if portlet is not None:
    return js_code % (portlet.nb_images-1, portlet.getId())
return ''
