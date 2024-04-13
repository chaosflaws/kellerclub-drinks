from .errors.error import ResistantHandler, ErrorHandler
from ..resources import Resources
from ..response_creators import ResponseCreator, RedirectCreator


class StartEvent(ResistantHandler):
    """Starts an event at the current time."""

    @property
    def canonical_url(self) -> str:
        return '/start_event'

    def _handle(self, res: Resources) -> ResponseCreator:
        try:
            res.datastore.start_event()
        except ValueError:
            return ErrorHandler(400, 'There is an ongoing event!').handle(res)

        return RedirectCreator('/')
