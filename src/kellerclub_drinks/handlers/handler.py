from abc import ABC, abstractmethod

from ..resources import Resources
from ..response_creators import ResponseCreator


class Handler(ABC):
    """Handles HTTP requests it receives from the router."""

    @property
    @abstractmethod
    def canonical_url(self) -> str:
        """The canonical URL of this handler instance.

        A handler instance may be reachable via multiple URLs, one of which is
        the canonical one. It is used by navigation bars to identify if a link
        points to the current page.
        """

    @abstractmethod
    def handle(self, res: Resources) -> ResponseCreator:
        """
        Receives a single HTTP request and must process it by passing
        appropriate headers to start_response and providing a response body.
        """
