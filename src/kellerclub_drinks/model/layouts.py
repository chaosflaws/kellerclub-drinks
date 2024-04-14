from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Iterable, Iterator

Row = list[Optional['Button']]


@dataclass(frozen=True)
class Layout(Iterable[Row]):
    """A 5x5 grid of buttons that can be used to record orders."""

    id: str
    buttons: list[Row]

    def __iter__(self) -> Iterator[Row]:
        return self.buttons.__iter__()

    def __getitem__(self, index: int) -> Row:
        if not isinstance(index, int):
            raise TypeError

        return self.buttons[index]


@dataclass(frozen=True)
class Button(ABC):
    """A button in a layout."""

    display_name: str

    @property
    @abstractmethod
    def is_order_button(self) -> bool:
        """True if the button records an order, false otherwise."""

    @property
    @abstractmethod
    def is_link(self) -> bool:
        """True if the button links to another layout, false otherwise."""


@dataclass(frozen=True)
class OrderButton(Button):
    """A button that records a purchase when clicked."""

    drink_name: str

    @property
    def is_order_button(self) -> bool:
        return True

    @property
    def is_link(self) -> bool:
        return False


@dataclass(frozen=True)
class LinkButton(Button):
    """A button that changes the currently visible layout."""

    layout: Layout

    @property
    def is_order_button(self) -> bool:
        return False

    @property
    def is_link(self) -> bool:
        return True
