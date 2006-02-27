
from Globals import InitializeClass

from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.BasicWidgets import CPSProgrammerCompoundWidget
from Products.CPSSchemas.Widget import widgetRegistry

from Products.CPSSkins.MainContent import MainContent

class CMFMainContentWidget(CPSProgrammerCompoundWidget):
    """Widget for rendering the main content area of a page.
    (cf. CMF main_template.pt's fill-slot="main")
    """
    meta_type = 'CMF Main Content Widget'
    render_method = 'renderMainContent'
    prepare_validate_method = ''

    def renderMainContent(self, template=None, options=None, **kw):
        """Render the main content area by switching to a 'macroless' skin
        inside the request.
        """
        rendered = ''
        if template is None:
            return self.widget_portlet_maincontent()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.changeSkin('CPSSkins-macroless')
        rendered = template.pt_render(extra_context={'options':options or {}})
        portal.changeSkin('CPSSkins')
        return rendered

InitializeClass(CMFMainContentWidget)

widgetRegistry.register(CMFMainContentWidget)

