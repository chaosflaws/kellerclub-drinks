from wsgiref.types import StartResponse

from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import RequestSource, AjaxCreator, RedirectCreator, ErrorCreator


class AddOrder(ResistantHandler):
    """Adds a time-stamped drink order to the datastore."""

    def __init__(self, drink_name: str, source: RequestSource):
        self.drink_name = drink_name
        self.source = source

    def _handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        res.datastore.add_order(self.drink_name)

        match self.source:
            case RequestSource.FORM:
                return RedirectCreator('/').serve(start_response)
            case RequestSource.AJAX:
                return AjaxCreator(200).with_content(b'').serve(start_response)
            case _:
                return ErrorCreator(400).serve(start_response)
