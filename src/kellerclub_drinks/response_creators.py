"""
Interface and implementations of response creators.
"""

import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Self
from wsgiref.types import StartResponse

from kellerclub_drinks.settings import Settings

RequestSource = Enum('RequestSource', ['FORM', 'AJAX'])


_STATUS_MESSAGES = {
    200: 'OK',
    303: 'See Other',
    400: 'Bad Request',
    404: 'Not Found'
}


def _get_status_string(status_code: int):
    return f'{status_code} {_STATUS_MESSAGES[status_code]}'


class ResponseCreator(ABC):
    """Sends a response back to the WSGI server."""

    @abstractmethod
    def serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        """
        Sets appropriate headers when calling start_response and returns the
        response body.
        """


class RedirectCreator(ResponseCreator):
    """Serves an HTTP response containing a generic redirect."""

    def __init__(self, new_path: str):
        self.new_path = new_path

    def serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        status = _get_status_string(303)
        response_headers = [('Location', self.new_path)]
        start_response(status, response_headers)
        return []


class CustomContentCreator(ResponseCreator, ABC):
    """Response creator with a non-empty response body that is supplied by a handler."""

    _content: bytes

    def with_content(self, content: bytes) -> Self:
        """Content to be served."""

        self._content = content

        return self

    def serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        if self._content is None:
            raise ValueError("Response creator expected content!")

        return self._serve(settings, start_response)

    @abstractmethod
    def _serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        pass


class ErrorCreator(CustomContentCreator):
    """
    Serves an error page for the given status code, if that status code is
    registered. Otherwise, sends a generic code 400 error message.
    """

    def __init__(self, status_code: int):
        self.status_code = status_code if 400 <= status_code < 500 else 400

    def _serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        status = _get_status_string(self.status_code)
        response_headers = [('Content-type', 'text/html; charset=utf-8'),
                            ('Content-Length', str(len(self._content)))]
        start_response(status, response_headers)
        return [self._content]


class SuccessCreator(CustomContentCreator):
    """Delivers the given content as a successful HTTP response."""

    def __init__(self, content_type: str, use_cache: bool):
        self.content_type = content_type
        self.use_cache = use_cache

    def _serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        status = _get_status_string(200)
        cache_control = str(settings.cache_age) if self.use_cache else 'no-cache'
        response_headers = [('Content-type', self.content_type),
                            ('Content-Length', str(len(self._content))),
                            ('Cache-Control', cache_control)]
        start_response(status, response_headers)
        return [self._content]


class StaticCreator(SuccessCreator):
    """Serves static content as cachable content."""

    def __init__(self, content_type: str):
        super().__init__(content_type, True)


class HtmlCreator(SuccessCreator):
    """Serves HTML content as a successful HTTP response."""
    def __init__(self):
        super().__init__('text/html; charset=utf-8', False)


class AjaxCreator(CustomContentCreator):
    """Serves an ajax response."""

    def __init__(self, status_code: int):
        self.status_code = status_code

    def with_json_content(self, content: Any):
        """
        Encode the content object as a json string and set it as the response
        content.
        """

        self.with_content(json.dumps(content).encode())

    def _serve(self, settings: Settings, start_response: StartResponse) -> list[bytes]:
        status = _get_status_string(self.status_code)
        response_headers = [('Content-Type', 'application/json'),
                            ('Content-Length', str(len(self._content)))]
        start_response(status, response_headers)
        return [self._content]
