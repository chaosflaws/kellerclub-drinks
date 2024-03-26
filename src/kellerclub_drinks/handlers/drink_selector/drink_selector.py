from kellerclub_drinks.handlers.errors.error import ErrorHandler, ResistantHandler
from kellerclub_drinks.resources import Resources
from kellerclub_drinks.response_creators import HtmlCreator, ResponseCreator
from kellerclub_drinks.templates import render_template

SELECTOR_TEMPLATE = 'drink_selector/drink_selector.jinja2'


class DrinkSelector(ResistantHandler):
    """Provides an HTML interface to add lots of orders quickly."""

    def __init__(self, layout_name: str = 'default'):
        self.layout_name = layout_name

    def _handle(self, res: Resources) -> ResponseCreator:
        layouts = res.datastore.all_layouts()
        if self.layout_name not in layouts:
            handler = ErrorHandler(404, f'Layout "{self.layout_name}" not found!')
            return handler.handle(res)

        content = render_template(res.jinjaenv, SELECTOR_TEMPLATE, layout=layouts[self.layout_name])
        return HtmlCreator().with_content(content.encode())
