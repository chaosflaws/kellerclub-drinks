"""
Interface and implementations of response creators.
"""
import json
from abc import ABC, abstractmethod
from typing import Any
from wsgiref.types import StartResponse


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
    def serve(self, start_response: StartResponse) -> list[bytes]:
        """
        Sets appropriate headers when calling start_response and returns the
        response body.
        """


class ErrorCreator(ResponseCreator):
    """
    Serves an error page for the given status code, if that status code is
    registered. Otherwise, sends a generic code 400 error message.
    """

    def __init__(self, status_code: int):
        self.status_code = status_code if 400 <= status_code < 500 else 400

    def serve(self, start_response: StartResponse) -> list[bytes]:
        with open(f'./kellerclub_drinks/{self.status_code}.html', 'rb') as error_file:
            content = error_file.read()

        status = _get_status_string(self.status_code)
        response_headers = [('Content-type', 'text/html; charset=utf-8'),
                            ('Content-Length', str(len(content)))]
        start_response(status, response_headers)
        return [content]


class SuccessCreator(ResponseCreator):
    """Delivers the given content as a successful HTTP response."""

    def __init__(self, content_type: str, content: bytes):
        self.content_type = content_type
        self.content = content

    def serve(self, start_response: StartResponse) -> list[bytes]:
        status = _get_status_string(200)
        response_headers = [('Content-type', self.content_type),
                            ('Content-Length', str(len(self.content)))]
        start_response(status, response_headers)
        return [self.content]


class HtmlCreator(SuccessCreator):
    """Serves HTML content as a successful HTTP response."""
    def __init__(self, content: bytes):
        super().__init__('text/html; charset=utf-8', content)


class AjaxCreator(ResponseCreator):
    """Serves an ajax response."""

    def __init__(self, status_code: int, response: Any):
        self.status_code = status_code
        self.response = json.dumps(response)

    def serve(self, start_response: StartResponse) -> list[bytes]:
        status = _get_status_string(self.status_code)
        response_headers = [('Content-Type', 'application/json'),
                            ('Content-Length', str(len(self.response)))]
        start_response(status, response_headers)
        return [self.response.encode()]


class RedirectCreator(ResponseCreator):
    """Serves an HTTP response containing a generic redirect."""

    def __init__(self, new_path: str):
        self.new_path = new_path

    def serve(self, start_response: StartResponse) -> list[bytes]:
        status = _get_status_string(303)
        response_headers = [('Location', self.new_path)]
        start_response(status, response_headers)
        return []
