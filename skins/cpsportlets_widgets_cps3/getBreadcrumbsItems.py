##parameters=**kw

if not context.isPrincipiaFolderish:
    kw['parent'] = 1

return context.getBreadCrumbs(**kw)
