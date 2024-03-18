from wsgiref.types import StartResponse

from ..errors.error import ResistantHandler
from ...resources import Resources
from ...response_creators import HtmlCreator
from ...templates import render_template


class DrinkList(ResistantHandler):
    """Returns the drinks currently available in the application."""

    def _handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        content = render_template(res.jinjaenv,
                                  'drink_list/drink_list.jinja2',
                                  drinks=res.datastore.get_all_drinks())
        return HtmlCreator().with_content(content.encode()).serve(start_response)
