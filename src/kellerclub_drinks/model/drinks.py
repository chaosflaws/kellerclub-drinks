from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Drink:
    """A drink or bundle for purchase."""

    name: str
    display_name: str
    price_history: PriceHistory

    def __post_init__(self) -> None:
        if not Drink.valid_name(self.name):
            raise ValueError('Invalid drink name!')

    @property
    def price(self) -> int:
        return self.price_history.current

    @staticmethod
    def valid_name(name: str) -> bool:
        """True if name is a valid internal name, false otherwise."""

        return bool(re.match('^[a-zA-Z0-9_]+$', name))


@dataclass(frozen=True)
class PriceHistory:
    """History of prices for one drink."""

    base_price: int
    price_changes: dict[datetime, int]

    def price_at(self, time: datetime) -> int:
        """Price at a specific point in time."""

        for changepoint, price in self.price_changes.items():
            if time >= changepoint:
                return price
        return self.base_price

    @property
    def current(self) -> int:
        """Current price."""

        return next(iter(reversed(self.price_changes.values())), self.base_price)
