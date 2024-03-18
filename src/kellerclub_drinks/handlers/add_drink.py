from wsgiref.types import StartResponse

from ..handlers.errors.error import ResistantHandler
from ..model.drinks import Drink
from ..resources import Resources
from ..response_creators import RedirectCreator


class AddDrink(ResistantHandler):
    """Receives a drink name and adds it to the data store."""

    def __init__(self, drink: Drink):
        self.drink = drink

    def _handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        res.datastore.add_drink(self.drink)
        return RedirectCreator('/drinks').serve(start_response)
