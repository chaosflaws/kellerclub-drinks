from __future__ import annotations

import re
from dataclasses import dataclass

from .prices import PriceHistory


@dataclass(frozen=True)
class Drink:
    """A drink or bundle for purchase."""

    name: str
    display_name: str
    prices: dict[str, PriceHistory]

    def __post_init__(self) -> None:
        if not Drink.valid_name(self.name):
            raise ValueError('Invalid drink name!')

    def price(self, pricing_model: str) -> int:
        return self.prices[pricing_model].current

    @staticmethod
    def valid_name(name: str) -> bool:
        """True if name is a valid internal name, false otherwise."""

        return bool(re.match('^[a-zA-Z0-9_]+$', name))
