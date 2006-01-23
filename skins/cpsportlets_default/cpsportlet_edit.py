##parameters=REQUEST, **kw

doc = context

doc.cpsdocument_edit(REQUEST=REQUEST, **kw)

# update cache parameters
ptype_id = doc.getPortletType()
doc.resetCacheTimeout()
doc.resetInterestingEvents(ptype_id)
doc.expireCache()

if REQUEST is not None:
    url = context.absolute_url() + '/cpsportlet_edit_form'
    return REQUEST.RESPONSE.redirect(url)
