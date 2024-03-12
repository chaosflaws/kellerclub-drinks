"""Methods to deliver an HTTP request to the appropriate handler."""

import re
from typing import Optional
from urllib.parse import parse_qs
from wsgiref.types import WSGIEnvironment

from .add_drink.add_drink import AddDrink
from .drink_list.drink_list import DrinkList
from .add_order.add_order import AddOrder
from .drink_selector.drink_selector import DrinkSelector
from .handlers import Handler, ErrorHandler, StaticHandler


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
        return ErrorHandler(400)


def _get_content(environ: WSGIEnvironment):
    if 'CONTENT_LENGTH' not in environ:
        return b''

    try:
        content_length = int(environ['CONTENT_LENGTH'])
    except ValueError:
        return b''

    return environ['wsgi.input'].read(content_length)


def _route_get(path: str, query: Optional[str]):
    # catch the funky stuff
    if not _valid_path(path):
        print(f'Invalid path {path}!')
        return ErrorHandler(400)
    if path == '/' or path == '':
        payload = parse_qs(query)

        if not payload:
            return DrinkSelector()

        if 'layout' not in payload:
            return ErrorHandler(400)

        if len(payload['layout']) != 1:
            return ErrorHandler(400)

        if not _valid_layout(payload['layout'][0]):
            return ErrorHandler(400)

        return DrinkSelector(payload['layout'][0])
    elif path.startswith('/drinks'):
        return DrinkList()
    elif path.endswith('.css'):
        return StaticHandler(path, 'text/css')
    elif path.endswith('.js'):
        return StaticHandler(path, 'text/javascript')
    elif path.endswith('.mjs'):
        return StaticHandler(path, 'text/javascript')
    else:
        return ErrorHandler(404)


def _valid_path(path: str) -> bool:
    return bool(re.match(r'^[a-zA-Z/_]*(\.[a-z]+)?$', path))


def _valid_layout(path: str) -> bool:
    return bool(re.match(r'^[a-zA-Z_]+$', path))


def _route_post(path: str, content_type: Optional[str], content: bytes):
    if path == '/add_order':
        if content_type != 'application/x-www-form-urlencoded':
            return ErrorHandler(400)

        payload = parse_qs(content.decode())
        if 'order' not in payload:
            return ErrorHandler(400)

        if len(payload['order']) != 1:
            return ErrorHandler(400)

        return AddOrder(payload['order'][0])
    elif path == '/add_drink':
        if content_type != 'application/x-www-form-urlencoded':
            return ErrorHandler(400)

        payload = parse_qs(content.decode())
        if 'drink' not in payload:
            return ErrorHandler(400)

        if len(payload['drink']) != 1:
            return ErrorHandler(400)

        return AddDrink(payload['drink'][0])
    else:
        return ErrorHandler(400)
