import unittest
from dataclasses import dataclass

from kellerclub_drinks.handlers.add_order import AddOrder
from kellerclub_drinks.handlers.drink_list.drink_list import DrinkList
from kellerclub_drinks.handlers.handler import Handler
from kellerclub_drinks.handlers.welcome_screen.welcome_screen import WelcomeScreen
from kellerclub_drinks.router import _route_get, _route_post


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
                self.assertIsInstance(_route_get(req.path, req.query), handler)

    def test_post_routes(self) -> None:
        route_to_handler: dict[PostRequest, type[Handler]] = {
            PostRequest('/add_order',
                        'application/x-www-form-urlencoded',
                        b'order=some_drink'): AddOrder,
            PostRequest('/api/add_order',
                        'application/json',
                        b'{"order":"some_drink"}'): AddOrder
        }

        for req, handler in route_to_handler.items():
            with self.subTest(req=req):
                result = _route_post(req.path, req.content_type, req.content)
                self.assertIsInstance(result, handler)
