from datetime import datetime

from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import RequestSource, AjaxCreator, RedirectCreator, ErrorCreator, \
    ResponseCreator


class AddOrder(ResistantHandler):
    """Adds a time-stamped drink order to the datastore."""

    def __init__(self, drink_name: str, event_id: datetime,
                 source: RequestSource, redirect_url: str):
        self.drink_name = drink_name
        self.event_id = event_id
        self.source = source
        self.redirect_url = redirect_url

    @property
    def canonical_url(self) -> str:
        return '/add_order'

    def _handle(self, res: Resources) -> ResponseCreator:
        res.datastore.add_order(self.event_id, self.drink_name)

        match self.source:
            case RequestSource.FORM:
                return RedirectCreator(self.redirect_url)
            case RequestSource.AJAX:
                return AjaxCreator(200).with_content(b'')
            case _:
                return ErrorCreator(400)
