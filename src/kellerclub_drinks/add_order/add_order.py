from wsgiref.types import StartResponse

from ..handlers import Handler
from ..resources import Resources
from ..response_creators import RedirectCreator


class AddOrder(Handler):
    def __init__(self, drink_name: str):
        self.drink_name = drink_name

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        res.datastore.add_order(self.drink_name)

        return RedirectCreator('/').serve(start_response)
