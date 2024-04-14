from datetime import datetime

from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import ResponseCreator, RedirectCreator


class AddOrderToClient(ResistantHandler):
    """Adds an order to the client's order list.

    The order must be submitted to be persisted in the database.
    """

    def __init__(self, drink_name: str, event_id: datetime, redirect_url: str):
        self.drink_name = drink_name
        self.event_id = event_id
        self.new_path = redirect_url

    def _handle(self, res: Resources) -> ResponseCreator:
        return RedirectCreator(self.new_path)

    @property
    def canonical_url(self) -> str:
        return '/add_order'
