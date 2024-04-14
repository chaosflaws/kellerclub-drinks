from datetime import datetime

from ..errors.error import ErrorHandler, ResistantHandler
from ...resources import Resources
from ...response_creators import HtmlCreator, ResponseCreator
from ...templates import render_template

SELECTOR_TEMPLATE = 'drink_selector/drink_selector.jinja2'


class DrinkSelector(ResistantHandler):
    """Provides an HTML interface to add lots of orders quickly."""

    def __init__(self, event_id: datetime, layout_name: str, autosubmit: bool):
        self.event_start = int(event_id.timestamp())
        self.layout_name = layout_name
        self.autosubmit = autosubmit

    @property
    def canonical_url(self) -> str:
        return f'/event/{self.event_start}/selector'

    def _handle(self, res: Resources) -> ResponseCreator:
        layouts = res.datastore.all_layouts()
        if self.layout_name not in layouts:
            handler = ErrorHandler(404, f'Layout "{self.layout_name}" not found!')
            return handler.handle(res)

        content = render_template(res.jinjaenv, SELECTOR_TEMPLATE,
                                  self.canonical_url,
                                  event_id=self.event_start,
                                  layout=layouts[self.layout_name],
                                  autosubmit=self.autosubmit)
        return HtmlCreator().with_content(content.encode())
