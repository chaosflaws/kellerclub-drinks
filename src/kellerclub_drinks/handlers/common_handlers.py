"""Contains commonly used request handlers."""

from pathlib import Path

from .errors.error import ResistantHandler, ErrorHandler
from ..resources import Resources
from ..response_creators import RedirectCreator, StaticCreator, ResponseCreator


class StaticHandler(ResistantHandler):
    """A handler that serves static files."""

    def __init__(self, request_path: str, content_type: str):
        self.request_path = request_path
        self.content_type = content_type

    def _handle(self, res: Resources) -> ResponseCreator:
        try:
            file_path = Path(self.request_path.removeprefix('/'))
            with open(f'kellerclub_drinks/handlers/{file_path}', 'rb') as file:
                content = file.read()
            return StaticCreator(self.content_type).with_content(content)
        except OSError:
            return ErrorHandler(404, f'Static file "{file_path}" not found!').handle(res)


class RedirectHandler(ResistantHandler):
    """A handler that redirects the client to another resource."""

    def __init__(self, new_path: str):
        self.new_path = new_path

    def _handle(self, res: Resources) -> ResponseCreator:
        return RedirectCreator(self.new_path)
