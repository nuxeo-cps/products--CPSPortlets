def no_view(*a):
    """This is used as a baseline marker for view lookups.

    Namely, registering this as an adapter for Interface with specific
    arguments will prevent being caught in general adapters that aren't views
    For instance, this is used on DataModel in order not to get the
    CPSDesignerThemes negociator for a (dm, request) pair while lookin up
    a view.

    This is of course much faster and robust than going through an inadequate
    adapter's __init__ and checking IBrowserView afterwards.
    """
    return
