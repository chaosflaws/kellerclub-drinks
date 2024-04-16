"""
Interface and implementations of response creators.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Callable
from wsgiref.types import StartResponse

from kellerclub_drinks.settings import Settings


HttpHeader = dict[str, str]


HeaderModifier = Callable[[HttpHeader, Settings], None]


_STATUS_MESSAGES = {
    200: 'OK',
    303: 'See Other',
    400: 'Bad Request',
    404: 'Not Found'
}


def _get_status_string(status_code: int) -> str:
    return f'{status_code} {_STATUS_MESSAGES[status_code]}'


class ResponseCreator(ABC):
    """Sends a response back to the WSGI server."""

    @abstractmethod
    def serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        """
        Sets appropriate headers when calling start_response and returns the
        response body.
        """


class ComposableCreator(ResponseCreator, ABC):
    def __init__(self) -> None:
        self._header_modifiers: list[HeaderModifier] = []

    @property
    @abstractmethod
    def content(self) -> list[bytes]:
        """Content of the HTTP response."""

    @property
    @abstractmethod
    def status_code(self) -> int:
        """Status code of the HTTP response."""

    def serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        headers: dict[str, str] = {}
        for mod in self._header_modifiers:
            mod(headers, settings)

        start_response(_get_status_string(self.status_code), list(headers.items()))

        return self.content

    def add_header_modifier(self, modifier: HeaderModifier) -> None:
        self._header_modifiers.append(modifier)

    @staticmethod
    def _serve_internal_error(start_response: StartResponse, error: str) -> list[bytes]:
        status = _get_status_string(500)
        start_response(status, [('Content-type', 'text/plain; charset=utf-8'),
                                ('Content-Length', str(len(error)))])
        return [error.encode()]


class LocationModifier:
    def __init__(self, new_path: str) -> None:
        self.new_path = new_path

    def __call__(self, header: HttpHeader, settings: Settings) -> None:
        header['Location'] = self.new_path


class CacheControlModifier:
    def __call__(self, header: HttpHeader, settings: Settings) -> None:
        header['Cache-Control'] = f'max-age={settings.cache_age}'


class ContentHeaderModifier:
    def __init__(self, content: bytes, content_type: str) -> None:
        self.content = content
        self.content_type = content_type

    def __call__(self, header: HttpHeader, settings: Settings) -> None:
        header['Content-type'] = self.content_type
        header['Content-Length'] = str(len(self.content))


class RedirectCreator(ComposableCreator):
    """Serves an HTTP response containing a generic redirect."""

    def __init__(self, new_path: str):
        super().__init__()
        self.add_header_modifier(LocationModifier(new_path))

    @property
    def content(self) -> list[bytes]:
        return []

    @property
    def status_code(self) -> int:
        return 303


class ErrorCreator(ComposableCreator):
    """
    Serves an error page for the given status code, if that status code is
    registered. Otherwise, sends a generic code 400 error message.
    """

    def __init__(self, content: bytes, status_code: int) -> None:
        super().__init__()
        self._content = content
        self._status_code = status_code
        self.add_header_modifier(ContentHeaderModifier(content, 'text/html; charset=utf-8'))

    @property
    def content(self) -> list[bytes]:
        return [self._content]

    @property
    def status_code(self) -> int:
        return self._status_code if 400 <= self._status_code < 500 else 400


class SuccessCreator(ComposableCreator):
    """Delivers the given content as a successful HTTP response."""

    def __init__(self, content: bytes, content_type: str, use_cache: bool) -> None:
        super().__init__()
        self._content = content
        self.add_header_modifier(ContentHeaderModifier(content, content_type))
        if use_cache:
            self.add_header_modifier(CacheControlModifier())

    @property
    def content(self) -> list[bytes]:
        return [self._content]

    @property
    def status_code(self) -> int:
        return 200


class StaticCreator(SuccessCreator):
    """Serves static content as cachable content."""

    def __init__(self, content: bytes, content_type: str):
        super().__init__(content, content_type, True)


class HtmlCreator(SuccessCreator):
    """Serves HTML content as a successful HTTP response."""
    def __init__(self, content: bytes) -> None:
        super().__init__(content, 'text/html; charset=utf-8', False)


class AjaxCreator(ComposableCreator):
    """Serves an ajax response."""

    def __init__(self, content: Any, status_code: int):
        super().__init__()
        self._content = json.dumps(content).encode()
        self._status_code = status_code
        self.add_header_modifier(ContentHeaderModifier(self._content, 'application/json'))

    @property
    def content(self) -> list[bytes]:
        return [self._content]

    @property
    def status_code(self) -> int:
        return self._status_code
