import unittest

from kellerclub_drinks.handlers.orders.client_order_store import ClientOrderStore


class TestClientOrderStore(unittest.TestCase):
    def test_clear_orders__clears_cookie(self) -> None:
        store = ClientOrderStore(100)

        header: dict[str, str] = {}
        store.clear_orders(header, None)

        self.assertEqual(1, len(header))
        self.assertTrue('event-100-orders=""' in header['Set-Cookie'])

    def test_add_order__adds_drink_to_cookie(self) -> None:
        store = ClientOrderStore(100)

        header: dict[str, str] = {}
        store.add_order([], 'test_drink', header, None)

        self.assertEqual(1, len(header))
        self.assertTrue('event-100-orders=test_drink' in header['Set-Cookie'])
