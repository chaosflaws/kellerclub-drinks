from abc import ABC, abstractmethod

from ..resources import Resources
from ..response_creators import ResponseCreator


class Handler(ABC):
    """Handles HTTP requests it receives from the router."""

    @abstractmethod
    def handle(self, res: Resources) -> ResponseCreator:
        """
        Receives a single HTTP request and must process it by passing
        appropriate headers to start_response and providing a response body.
        """
