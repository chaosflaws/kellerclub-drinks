from .errors.error import ResistantHandler
from ..resources import Resources
from ..response_creators import ResponseCreator, RedirectCreator


class StopEvent(ResistantHandler):
    """Stops the currently running event."""

    @property
    def canonical_url(self) -> str:
        return '/stop_event'

    def _handle(self, res: Resources) -> ResponseCreator:
        res.datastore.stop_current_event()
        return RedirectCreator('/')
