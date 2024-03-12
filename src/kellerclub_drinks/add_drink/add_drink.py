from wsgiref.types import StartResponse

from ..handlers import Handler
from ..resources import Resources
from ..response_creators import RedirectCreator


class AddDrink(Handler):
    """Receives a drink name and adds it to the data store."""

    def __init__(self, drink_name: str):
        self.drink_name = drink_name

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        res.datastore.add_drink(self.drink_name)
        return RedirectCreator('/drinks').serve(start_response)
