from ..handlers.errors.error import ResistantHandler
from ..model.drinks import Drink
from ..resources import Resources
from ..response_creators import RedirectCreator, ResponseCreator


class AddDrink(ResistantHandler):
    """Receives a drink name and adds it to the data store."""

    def __init__(self, drink: Drink):
        self.drink = drink

    @property
    def canonical_url(self) -> str:
        return '/add_drink'

    def _handle(self, res: Resources) -> ResponseCreator:
        res.datastore.add_drink(self.drink)
        return RedirectCreator('/drinks')
