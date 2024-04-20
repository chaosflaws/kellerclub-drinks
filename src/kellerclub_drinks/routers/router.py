"""Methods to deliver an HTTP request to the appropriate handler."""
import json
import re
from datetime import datetime
from http.cookies import SimpleCookie
from typing import Optional
from urllib.parse import urlparse
from wsgiref.types import WSGIEnvironment

from .form_parser import FormParser, SingleValueParam, BooleanParam, CheckboxParam, Param
from .request_source import RequestSource
from ..handlers.add_order import AddOrderToClient
from ..handlers.drink_selector.settings import DrinkSelectorSettings
from ..handlers.errors.error import ErrorHandler
from ..handlers.add_drink import AddDrink
from ..handlers.drink_list.drink_list import DrinkList
from ..handlers.submit_order import SubmitOrder
from ..handlers.drink_selector.drink_selector import DrinkSelector
from ..handlers.common_handlers import StaticHandler
from ..handlers.handler import Handler
from ..handlers.start_event import StartEvent
from ..handlers.stop_event import StopEvent
from ..handlers.welcome_screen.welcome_screen import WelcomeScreen
from ..model.drinks import Drink


def route(environ: WSGIEnvironment) -> Handler:
    """Delivers an HTTP request to the appropriate handler."""

    method: str = environ['REQUEST_METHOD']
    path: str = environ['PATH_INFO']
    referer: Optional[str] = environ.get('HTTP_REFERER', None)
    query: Optional[str] = environ.get('QUERY_STRING', None)
    content_type: Optional[str] = environ.get('CONTENT_TYPE', None)
    content: bytes = _get_content(environ)
    cookie = SimpleCookie(environ.get('HTTP_COOKIE', ''))

    if method.lower() == 'get':
        return _route_get(path, query, cookie)
    elif method.lower() == 'post':
        return _route_post(path, referer, content_type, content, cookie)
    else:
        return ErrorHandler(400, 'Unsupported HTTP method!')


def _get_content(environ: WSGIEnvironment) -> bytes:
    if 'CONTENT_LENGTH' not in environ:
        return b''

    try:
        content_length = int(environ['CONTENT_LENGTH'])
    except ValueError:
        return b''

    return environ['wsgi.input'].read(content_length)


def _route_get(path: str, query: Optional[str], cookie: SimpleCookie) -> Handler:
    # catch the funky stuff
    if not _valid_path(path):
        print(f'Invalid path {path}!')
        return ErrorHandler(400, "Invalid path!")

    # paths without variables
    stripped_path = path.rstrip('/')
    if stripped_path == '':
        return WelcomeScreen()
    elif stripped_path == '/drinks':
        return DrinkList(RequestSource.NAV)

    # event-related URLs
    if (parts := path.split('/'))[1] == 'event':
        if len(parts) == 4 and parts[2].isdigit() and parts[3] == 'selector':
            event_id = int(parts[2])
            return _get_drink_selector(event_id, query, cookie)

    # API paths without variables
    if stripped_path == '/api/drinks':
        return DrinkList(RequestSource.AJAX)

    # paths to static files
    if path.endswith('.css'):
        return StaticHandler(path, 'text/css')
    elif path.endswith('.js'):
        return StaticHandler(path, 'text/javascript')
    elif path.endswith('.woff2'):
        return StaticHandler(path, 'font/woff2')

    # give up
    return ErrorHandler(404, f"Unknown GET route {path}!")


def _get_drink_selector(event_id: int, query: Optional[str],
                        cookie: SimpleCookie) -> Handler:

    try:
        parser = FormParser(SingleValueParam('layout', default=['default']),
                            BooleanParam('autosubmit', default=['true']))
        params = parser.parse(query or '')
        return DrinkSelector(datetime.fromtimestamp(event_id),
                             params['layout'][0],
                             params['autosubmit'][0],
                             _get_orders(cookie, event_id))
    except ValueError as e:
        return ErrorHandler(400, str(e))


def _valid_layout(path: str) -> bool:
    return bool(re.match(r'^[a-zA-Z_]+$', path))


def _get_orders(cookie: SimpleCookie, event_id: int) -> list[str]:
    if (morsel := cookie.get(f'event-{event_id}-orders')) is not None:
        return [value
                for value in morsel.value.split(',')
                if Drink.valid_name(value)]
    else:
        return []


def _route_post(path: str, referer: Optional[str], content_type: Optional[str],
                content: bytes, cookie: SimpleCookie) -> Handler:
    # catch the funky stuff
    if not _valid_path(path):
        print(f'Invalid path {path}!')
        return ErrorHandler(400, "Invalid path!")

    # constant paths
    stripped_path = path.rstrip('/')
    if stripped_path == '/add_order':
        try:
            parser = FormParser(SingleValueParam('order'),
                                SingleValueParam('event'))
            parsed_query = parser.parse(content.decode(), content_type=content_type)
            event_id = int(parsed_query['event'][0])
            return AddOrderToClient(parsed_query['order'][0],
                                    event_id,
                                    _get_orders(cookie, event_id),
                                    referer or '/')
        except ValueError as e:
            return ErrorHandler(400, str(e))
    elif stripped_path == '/submit_order':
        try:
            parser = FormParser(Param('order', 1),
                                SingleValueParam('event'))
            parsed_query = parser.parse(content.decode(), content_type=content_type)
            return SubmitOrder(parsed_query['order'],
                               datetime.fromtimestamp(int(parsed_query['event'][0])),
                               RequestSource.FORM, referer or '')
        except ValueError as e:
            return ErrorHandler(400, str(e))
    elif stripped_path == '/add_drink':
        try:
            parser = FormParser(SingleValueParam('drink'),
                                SingleValueParam('display_name'))
            parsed_query = parser.parse(content.decode(), content_type=content_type)
            name = parsed_query['drink'][0]
            display_name = parsed_query['display_name'][0]
            return AddDrink(Drink(name, display_name))
        except ValueError as e:
            return ErrorHandler(400, str(e))
    elif stripped_path == '/start_event':
        return StartEvent()
    elif stripped_path == '/stop_event':
        return StopEvent()
    elif stripped_path == '/settings/drink_selector':
        parser = FormParser(CheckboxParam('autosubmit'))
        parsed_query = parser.parse(content.decode(), content_type=content_type)
        referer_url = urlparse(referer)
        return DrinkSelectorSettings(parsed_query['autosubmit'][0], referer_url)

    # constant API paths
    if stripped_path == '/api/submit_order':
        try:
            parsed_json = json.loads(content.decode())
            if 'orders' not in parsed_json:
                return ErrorHandler(400, "Key 'orders' not present!")
            elif not isinstance(parsed_json['orders'], list):
                return ErrorHandler(400, "'orders' is not a string!")
            elif any(not isinstance(item, str) for item in parsed_json['orders']):
                msg = f"{parsed_json['orders']} contains an item that is not a string!"
                return ErrorHandler(400, msg)
            else:
                if 'event' not in parsed_json:
                    return ErrorHandler(400, "Key 'event' not present!")
                elif not isinstance(parsed_json['event'], int):
                    return ErrorHandler(400, "'event' is not a number!")
                else:
                    return SubmitOrder(parsed_json['orders'],
                                       datetime.fromtimestamp(parsed_json['event']),
                                       RequestSource.AJAX, referer or '/')
        except ValueError:
            return ErrorHandler(400, f"Malformed JSON {content.decode()}!")

    # give up
    return ErrorHandler(400, f"Unknown POST route {path}!")


def _valid_path(path: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9/_]*(\.[a-z0-9]+)?$', path))
