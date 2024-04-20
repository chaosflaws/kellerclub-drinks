from datetime import datetime

from ..orders.client_order_store import ClientOrderStore
from ..errors.error import ErrorHandler, ResistantHandler
from ...datastores.datastore import DataStore
from ...resources import Resources
from ...response_creators import HtmlCreator, ResponseCreator
from ...templates import render_template

SELECTOR_TEMPLATE = 'drink_selector/drink_selector.jinja2'


class DrinkSelector(ResistantHandler):
    """Provides an HTML interface to add lots of orders quickly."""

    def __init__(self, event_start: datetime, layout_name: str, autosubmit: bool,
                 stored_orders: list[str]):
        self.event_start = event_start
        self.event_id = int(event_start.timestamp())
        self.layout_name = layout_name
        self.autosubmit = autosubmit
        self.stored_orders = stored_orders

    @property
    def canonical_url(self) -> str:
        return f'/event/{self.event_id}/selector'

    def _handle(self, res: Resources) -> ResponseCreator:
        all_drinks = res.datastore.all_drinks()
        layouts = res.datastore.all_layouts()

        if self.autosubmit:
            self._store_dangling_orders(res.datastore)

        if self.layout_name not in layouts:
            handler = ErrorHandler(404, f'Layout "{self.layout_name}" not found!')
            return handler.handle(res)

        stored_drinks = [all_drinks[name] for name in self.stored_orders if name in all_drinks]
        content = render_template(res.jinjaenv, SELECTOR_TEMPLATE,
                                  self.canonical_url,
                                  event_id=self.event_id,
                                  layout=layouts[self.layout_name],
                                  autosubmit=self.autosubmit,
                                  stored_drinks=stored_drinks)

        creator = HtmlCreator(content.encode())
        if self.autosubmit:
            modifier = ClientOrderStore(self.event_id).clear_orders
            creator.add_header_modifier(modifier)
        return creator

    def _store_dangling_orders(self, datastore: DataStore):
        if self.stored_orders:
            datastore.submit_order(self.event_start, self.stored_orders)
