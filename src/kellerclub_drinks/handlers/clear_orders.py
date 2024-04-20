from .drink_selector.client_order_store import ClientOrderStore
from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import ResponseCreator, RedirectCreator


class ClearOrders(ResistantHandler):
    def __init__(self, event_id: int, new_path: str):
        self.event_id = event_id
        self.new_path = new_path

    def _handle(self, res: Resources) -> ResponseCreator:
        creator = RedirectCreator(self.new_path)
        creator.add_header_modifier(ClientOrderStore(self.event_id).clear_orders_cookie)
        return creator

    @property
    def canonical_url(self) -> str:
        return '/clear_orders'
