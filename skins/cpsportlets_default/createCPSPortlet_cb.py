##parameters=type_name, datamodel
# $Id$
"""
Callback to create an empty object with the context as a container.

Datamodel may be examined to create a suitable id.

Call notifyCPSDocumentCreation script

Returns the created object. In CPS, returns the proxy (which is
the only thing the user sees).
"""

folder = context

id = datamodel.get('Title')
if not id:
    id = 'my ' + type_name

language = datamodel.get('Language')
if not language:
    language = context.Localizer.get_selected_language()

id = context.computeId(compute_from=id)

# datamodel is passed so that flexti can initialize the object.
context.invokeFactory(type_name, id, datamodel=datamodel, language=language)
ob = getattr(context, id)

context.notifyCPSDocumentCreation(ob=ob)

return ob
