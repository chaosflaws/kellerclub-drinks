from __future__ import annotations

import unittest
from dataclasses import dataclass
from http.cookies import SimpleCookie

from kellerclub_drinks.handlers.add_drink import AddDrink
from kellerclub_drinks.handlers.submit_order import SubmitOrder
from kellerclub_drinks.handlers.common_handlers import StaticHandler
from kellerclub_drinks.handlers.drink_list.drink_list import DrinkList
from kellerclub_drinks.handlers.drink_selector.drink_selector import DrinkSelector
from kellerclub_drinks.handlers.errors.error import ErrorHandler
from kellerclub_drinks.handlers.handler import Handler
from kellerclub_drinks.handlers.welcome_screen.welcome_screen import WelcomeScreen
from kellerclub_drinks.routers.router import _route_get, _route_post


EMPTY_COOKIE = SimpleCookie()


@dataclass(frozen=True)
class GetRequest:
    path: str
    query: str

    @staticmethod
    def from_url(url: str) -> GetRequest:
        if '?' in url:
            path, query = url.split('?', 1)
            return GetRequest(path, query)
        else:
            return GetRequest(url, '')


@dataclass(frozen=True)
class PostRequest:
    path: str
    content_type: str
    content: bytes


class TestRouter(unittest.TestCase):
    def test_get_routes(self) -> None:
        route_to_handler: dict[str, type[Handler]] = {
            '/': WelcomeScreen,
            '/drinks': DrinkList
        }

        for url, handler in route_to_handler.items():
            with self.subTest(req=url):
                req = GetRequest.from_url(url)
                self.assertIsInstance(_route_get(req.path, req.query, EMPTY_COOKIE), handler)

    def test_post_routes(self) -> None:
        route_to_handler: dict[PostRequest, type[Handler]] = {
            PostRequest('/submit_order',
                        'application/x-www-form-urlencoded',
                        b'order=some_drink&event=100'): SubmitOrder,
            PostRequest('/api/submit_order',
                        'application/json',
                        b'{"order":"some_drink","event":100}'): SubmitOrder
        }

        for req, handler in route_to_handler.items():
            with self.subTest(req=req):
                result = _route_post(req.path, '', req.content_type, req.content)
                self.assertIsInstance(result, handler)

    def test_invalid_routes(self) -> None:
        invalid_urls = ['..', '-']

        for url in invalid_urls:
            with self.subTest(url=url):
                req = GetRequest.from_url(url)
                handler = _route_get(req.path, req.query, EMPTY_COOKIE)
                self.assertIsInstance(handler, ErrorHandler)

    def test_static_routes(self) -> None:
        static_urls = ['/base.css', '/font.woff2']

        for url in static_urls:
            with self.subTest(url=url):
                handler = _route_get(url, None, EMPTY_COOKIE)
                self.assertIsInstance(handler, StaticHandler)

    def test_drink_selector_route(self) -> None:
        valid_route = '/event/100000/selector'
        self.assertIsInstance(_route_get(valid_route, None, EMPTY_COOKIE),
                              DrinkSelector)

        non_digit_event_id = '/event/100a/selector'
        self.assertIsInstance(_route_get(non_digit_event_id, None, EMPTY_COOKIE),
                              ErrorHandler)

        valid_layout_query = 'layout=default'
        self.assertIsInstance(_route_get(valid_route, valid_layout_query, EMPTY_COOKIE),
                              DrinkSelector)

        invalid_layout_query = 'layout?=default'
        self.assertIsInstance(_route_get(valid_route, invalid_layout_query, EMPTY_COOKIE),
                              ErrorHandler)

    def test_valid_add_drink_route(self) -> None:
        path = '/add_drink'

        valid_query = b'drink=test_drink&display_name=Test+Drink'

        result = _route_post(path, '', 'application/x-www-form-urlencoded', valid_query)

        self.assertIsInstance(result, AddDrink)

    def test_add_drink_route_with_two_drinks(self) -> None:
        path = '/add_drink'

        valid_query = b'drink=test_drink&display_name=Test+Drink&drink=some_drink'

        result = _route_post(path, '', 'application/x-www-form-urlencoded', valid_query)

        self.assertIsInstance(result, ErrorHandler)
