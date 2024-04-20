import unittest
from datetime import datetime

from kellerclub_drinks.model.drinks import PriceHistory


class TestDrinks(unittest.TestCase):
    def test_price_at__before_changepoint__returns_base(self) -> None:
        history = PriceHistory(1, {datetime.fromtimestamp(10_000): 2,
                                   datetime.fromtimestamp(20_000): 3})

        self.assertEqual(1, history.price_at(datetime.fromtimestamp(9_999)))

    def test_price_at__at_changepoint__returns_new_price(self) -> None:
        history = PriceHistory(1, {datetime.fromtimestamp(10_000): 2,
                                   datetime.fromtimestamp(20_000): 3})

        self.assertEqual(2, history.price_at(datetime.fromtimestamp(10_000)))

    def test_current__returns_latest_price(self) -> None:
        history = PriceHistory(1, {datetime.fromtimestamp(10_000): 2,
                                   datetime.fromtimestamp(20_000): 3})

        self.assertEqual(3, history.current)
