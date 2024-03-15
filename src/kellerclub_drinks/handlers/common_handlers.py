"""Contains commonly used request handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from wsgiref.types import StartResponse

from ..resources import Resources
from ..response_creators import ErrorCreator, SuccessCreator, RedirectCreator


class Handler(ABC):
    """Handles HTTP requests it receives from the router."""

    @abstractmethod
    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        """
        Receives a single HTTP request and must process it by passing
        appropriate headers to start_response and providing a response body.
        """


class StaticHandler(Handler):
    """A handler that serves static files."""

    def __init__(self, request_path: str, content_type: str):
        self.request_path = request_path
        self.content_type = content_type

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        try:
            file_path = Path(self.request_path.removeprefix('/'))
            with open(f'kellerclub_drinks/handlers/{file_path}', 'rb') as file:
                content = file.read()
            return SuccessCreator(self.content_type, content).serve(start_response)
        except OSError:
            return ErrorCreator(404).serve(start_response)


class RedirectHandler(Handler):
    """A handler that redirects the client to another resource."""

    def __init__(self, new_path: str):
        self.new_path = new_path

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        return RedirectCreator(self.new_path).serve(start_response)


class ErrorHandler(Handler):
    """
    A handler that serves a generic error message according to the selected
    status code.
    """

    def __init__(self, status_code: int):
        self.status_code = status_code

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        return ErrorCreator(self.status_code).serve(start_response)
