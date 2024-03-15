from wsgiref.types import StartResponse

from kellerclub_drinks.handlers.common_handlers import Handler
from kellerclub_drinks.resources import Resources
from kellerclub_drinks.response_creators import RedirectCreator


class AddOrder(Handler):
    """Adds a time-stamped drink order to the datastore."""

    def __init__(self, drink_name: str):
        self.drink_name = drink_name

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        res.datastore.add_order(self.drink_name)

        return RedirectCreator('/').serve(start_response)
