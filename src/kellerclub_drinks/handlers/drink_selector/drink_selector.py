from wsgiref.types import StartResponse

from kellerclub_drinks.handlers.common_handlers import Handler
from kellerclub_drinks.resources import Resources
from kellerclub_drinks.response_creators import HtmlCreator


LAYOUT_NOT_FOUND_TEMPLATE = 'kellerclub_drinks/drink_selector/layout_not_found.jinja2'
SELECTOR_TEMPLATE = 'kellerclub_drinks/drink_selector/drink_selector.jinja2'


class DrinkSelector(Handler):
    """Provides an HTML interface to add lots of orders quickly."""

    def __init__(self, layout: str = 'default'):
        self.layout = layout

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        layouts = res.datastore.get_all_layouts()
        if self.layout not in layouts:
            template = res.jinjaenv.get_template(LAYOUT_NOT_FOUND_TEMPLATE)
            content = template.render(layout=self.layout)
            return HtmlCreator(content.encode()).serve(start_response)

        layout = layouts[self.layout]
        template = res.jinjaenv.get_template(SELECTOR_TEMPLATE)
        content = template.render(layout=layout)
        return HtmlCreator(content.encode()).serve(start_response)
