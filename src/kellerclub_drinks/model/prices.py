from dataclasses import dataclass
from datetime import datetime


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
