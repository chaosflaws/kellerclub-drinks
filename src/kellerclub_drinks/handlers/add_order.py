from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import ResponseCreator, RedirectCreator


class AddOrderToClient(ResistantHandler):
    """Adds an order to the client's order list.

    The order must be submitted to be persisted in the database.
    """

    def __init__(self, new_path: str):
        self.new_path = new_path

    def _handle(self, res: Resources) -> ResponseCreator:
        return RedirectCreator(self.new_path)

    @property
    def canonical_url(self) -> str:
        return '/add_order'
