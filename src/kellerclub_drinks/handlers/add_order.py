from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import RequestSource, AjaxCreator, RedirectCreator, ErrorCreator, \
    ResponseCreator


class AddOrder(ResistantHandler):
    """Adds a time-stamped drink order to the datastore."""

    def __init__(self, drink_name: str, source: RequestSource):
        self.drink_name = drink_name
        self.source = source

    @property
    def canonical_url(self) -> str:
        return '/add_order'

    def _handle(self, res: Resources) -> ResponseCreator:
        res.datastore.add_order(self.drink_name)

        match self.source:
            case RequestSource.FORM:
                return RedirectCreator('/')
            case RequestSource.AJAX:
                return AjaxCreator(200).with_content(b'')
            case _:
                return ErrorCreator(400)
