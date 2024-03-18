from abc import ABC, abstractmethod
from wsgiref.types import StartResponse

from ..resources import Resources


class Handler(ABC):
    """Handles HTTP requests it receives from the router."""

    @abstractmethod
    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        """
        Receives a single HTTP request and must process it by passing
        appropriate headers to start_response and providing a response body.
        """
