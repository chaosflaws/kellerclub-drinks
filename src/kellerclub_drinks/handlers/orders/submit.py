from datetime import datetime

from .client_order_store import ClientOrderStore
from ..errors.error import ResistantHandler
from ...resources import Resources
from ...response_creators import AjaxCreator, RedirectCreator, ResponseCreator
from ...routers.request_source import RequestSource


class Submit(ResistantHandler):
    """Persists a time-stamped drink order in the datastore."""

    def __init__(self, drink_names: list[str], event_id: datetime,
                 source: RequestSource, redirect_url: str):
        self.drink_names = drink_names
        self.event_id = event_id
        self.source = source
        self.redirect_url = redirect_url

    @property
    def canonical_url(self) -> str:
        return '/orders/submit'

    def _handle(self, res: Resources) -> ResponseCreator:
        res.datastore.submit_order(self.event_id, self.drink_names)

        match self.source:
            case RequestSource.FORM:
                creator = RedirectCreator(self.redirect_url)
                modifier = ClientOrderStore(int(self.event_id.timestamp())).clear_orders
                creator.add_header_modifier(modifier)
                return creator
            case RequestSource.AJAX:
                return AjaxCreator(None, 200)
            case _:
                raise ValueError("Unsupported RequestSource!")
