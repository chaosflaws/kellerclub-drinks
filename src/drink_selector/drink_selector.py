from typing import Optional
from wsgiref.types import StartResponse

from handlers import Handler
from resources import Resources
from response_creators import HtmlCreator


class DrinkSelector(Handler):
    def __init__(self, layout: str = 'drink_selector'):
        self.layout = layout

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        with open(f'drink_selector/{self.layout}.html', 'rb') as file:
            return HtmlCreator(file.read()).serve(start_response)
