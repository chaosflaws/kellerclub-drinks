from ..errors.error import ResistantHandler
from ...resources import Resources
from ...response_creators import HtmlCreator, ResponseCreator, AjaxCreator
from ...routers.request_source import RequestSource
from ...templates import render_template


class DrinkList(ResistantHandler):
    """Returns the drinks currently available in the application."""

    def __init__(self, source: RequestSource):
        self.source = source

    @property
    def canonical_url(self) -> str:
        return '/drinks'

    def _handle(self, res: Resources) -> ResponseCreator:
        drink_list = res.datastore.all_drinks()
        match self.source:
            case RequestSource.NAV:
                content = render_template(res.jinjaenv,
                                          'drink_list/drink_list.jinja2',
                                          self.canonical_url,
                                          drinks=drink_list)
                return HtmlCreator(content.encode())
            case RequestSource.AJAX:
                content = {key: (value.display_name, value.price('default'))
                           for key, value in drink_list.items()}
                return AjaxCreator(content, 200)
            case _:
                raise ValueError("Unsupported RequestSource!")
