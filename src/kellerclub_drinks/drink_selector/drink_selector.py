from wsgiref.types import StartResponse

from ..handlers import Handler
from ..resources import Resources
from ..response_creators import HtmlCreator


class DrinkSelector(Handler):
    """Provides an HTML interface to add lots of orders quickly."""

    def __init__(self, layout: str = 'drink_selector'):
        self.layout = layout

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        with open(f'kellerclub_drinks/drink_selector/{self.layout}.html', 'rb') as file:
            return HtmlCreator(file.read()).serve(start_response)
