from ..errors.error import ResistantHandler
from ...resources import Resources
from ...response_creators import HtmlCreator, ResponseCreator
from ...templates import render_template


class DrinkList(ResistantHandler):
    """Returns the drinks currently available in the application."""

    @property
    def canonical_url(self) -> str:
        return '/drinks'

    def _handle(self, res: Resources) -> ResponseCreator:
        content = render_template(res.jinjaenv,
                                  'drink_list/drink_list.jinja2',
                                  drinks=res.datastore.all_drinks())
        return HtmlCreator().with_content(content.encode())
