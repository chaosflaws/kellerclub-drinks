from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import ResponseCreator, RedirectCreator, HttpHeader
from ..settings import Settings


class AddOrderToClient(ResistantHandler):
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
        creator.add_header_modifier(self._add_order_to_cookie)
        return creator

    @property
    def canonical_url(self) -> str:
        return '/add_order'

    def _add_order_to_cookie(self, header: HttpHeader, _: Settings) -> None:
        new_orders = self.order_list + [self.drink_name]
        print(f'event-{self.event_id}-orders={",".join(new_orders)}')
        header['Set-Cookie'] = f'event-{self.event_id}-orders={",".join(new_orders)}'
