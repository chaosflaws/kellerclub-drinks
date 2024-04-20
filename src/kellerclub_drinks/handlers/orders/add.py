from functools import partial

from .client_order_store import ClientOrderStore
from ..errors.error import ResistantHandler
from ...resources import Resources
from ...response_creators import ResponseCreator, RedirectCreator


class AddOrder(ResistantHandler):
    """Adds an order to the client's order list.

    The order must be submitted to be persisted in the database.
    """

    def __init__(self, drink_name: str, event_id: int,
                 current_orders: list[str], redirect_url: str):
        self.drink_name = drink_name
        self.event_id = event_id
        self.order_list = current_orders
        self.new_path = redirect_url

    def _handle(self, res: Resources) -> ResponseCreator:
        creator = RedirectCreator(self.new_path)
        modifier = partial(ClientOrderStore(self.event_id).add_order,
                           self.order_list,
                           self.drink_name)
        creator.add_header_modifier(modifier)
        return creator

    @property
    def canonical_url(self) -> str:
        return '/orders/add'
