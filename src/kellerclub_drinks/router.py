"""Methods to deliver an HTTP request to the appropriate handler."""
import json
import re
from typing import Optional
from urllib.parse import parse_qs
from wsgiref.types import WSGIEnvironment

from .handlers.errors.error import ErrorHandler
from .handlers.add_drink import AddDrink
from .handlers.drink_list.drink_list import DrinkList
from .handlers.add_order import AddOrder
from .handlers.drink_selector.drink_selector import DrinkSelector
from .handlers.common_handlers import StaticHandler
from .handlers.handler import Handler
from .handlers.welcome_screen.welcome_screen import WelcomeScreen
from .model.drinks import Drink
from .response_creators import RequestSource


def route(environ: WSGIEnvironment) -> Handler:
    """Delivers an HTTP request to the appropriate handler."""

    method: str = environ['REQUEST_METHOD']
    path: str = environ['PATH_INFO']
    query: Optional[str] = environ.get('QUERY_STRING', None)
    content_type: Optional[str] = environ.get('CONTENT_TYPE', None)
    content: bytes = _get_content(environ)

    if method.lower() == 'get':
        return _route_get(path, query)
    elif method.lower() == 'post':
        return _route_post(path, content_type, content)
    else:
        return ErrorHandler(400, 'Unsupported HTTP method!')


def _get_content(environ: WSGIEnvironment):
    if 'CONTENT_LENGTH' not in environ:
        return b''

    try:
        content_length = int(environ['CONTENT_LENGTH'])
    except ValueError:
        return b''

    return environ['wsgi.input'].read(content_length)


def _route_get(path: str, query: Optional[str]) -> Handler:
    # catch the funky stuff
    if not _valid_path(path):
        print(f'Invalid path {path}!')
        return ErrorHandler(400, "Invalid path!")

    stripped_path = path.rstrip('/')
    if stripped_path == '':
        return WelcomeScreen()
    if stripped_path == '/selector':
        if query is None or query == '':
            return DrinkSelector()

        try:
            params = FormParser(layout=1).parse(query or '')
            return DrinkSelector(params['layout'][0])
        except ValueError as e:
            return ErrorHandler(400, str(e))
    elif stripped_path == '/drinks':
        return DrinkList()
    elif path.endswith('.css'):
        return StaticHandler(path, 'text/css')
    elif path.endswith('.js') or path.endswith('.mjs'):
        return StaticHandler(path, 'text/javascript')
    else:
        return ErrorHandler(404, f"Unknown GET route {path}!")


def _valid_path(path: str) -> bool:
    return bool(re.match(r'^[a-zA-Z/_]*(\.[a-z]+)?$', path))


def _valid_layout(path: str) -> bool:
    return bool(re.match(r'^[a-zA-Z_]+$', path))


def _route_post(path: str, content_type: Optional[str], content: bytes) -> Handler:
    if path == '/add_order':
        try:
            parser = FormParser(order=1)
            parsed_query = parser.parse(content.decode(), content_type=content_type)
            return AddOrder(parsed_query['order'][0], RequestSource.FORM)
        except ValueError as e:
            return ErrorHandler(400, str(e))
    elif path == '/add_drink':
        try:
            parser = FormParser(drink=1, display_name=1)
            parsed_query = parser.parse(content.decode(), content_type=content_type)
            name = parsed_query['drink'][0]
            display_name = parsed_query['display_name'][0]
            return AddDrink(Drink(name, display_name))
        except ValueError as e:
            return ErrorHandler(400, str(e))
    elif path == '/api/add_order':
        try:
            parsed_json = json.loads(content.decode())
            if 'order' not in parsed_json:
                return ErrorHandler(400, "Key 'order' not present!")
            elif not isinstance(parsed_json['order'], str):
                return ErrorHandler(400, "'order' is not a string!")
            else:
                return AddOrder(parsed_json['order'], RequestSource.AJAX)
        except ValueError:
            return ErrorHandler(400, f"Malformed JSON {content.decode()}!")
    else:
        return ErrorHandler(400, f"Unknown POST route {path}!")


class FormParser:
    """Parser for a query string formatted as HTML form data."""

    def __init__(self, **valid_params: int):
        self.valid_params = valid_params

    def parse(self, query: str, /, content_type: Optional[str] = None) -> dict[str, list[str]]:
        if content_type not in [None, 'application/x-www-form-urlencoded']:
            raise ValueError('Wrong Content Type!')

        payload = parse_qs(query)

        if len(payload) != len(self.valid_params):
            raise ValueError('Argument list has wrong length!')

        for param, count in self.valid_params.items():
            if param not in payload:
                raise ValueError(f'Param {param} not valid!')
            if len(payload[param]) != count:
                raise ValueError(f'Param {param} has wrong number of values!')

        return payload
