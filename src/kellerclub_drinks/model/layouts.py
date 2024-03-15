from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Iterable

Row = list[Optional['Button']]


@dataclass(frozen=True)
class Layout(Iterable):
    """A 5x5 grid of buttons that can be used to record orders."""

    id: str
    buttons: list[Row]

    def __iter__(self):
        return self.buttons.__iter__()

    def __getitem__(self, index: int):
        if not isinstance(index, int):
            raise TypeError

        return self.buttons[index]


@dataclass(frozen=True)
class Button(ABC):
    """A button in a layout."""

    display_name: str

    @property
    @abstractmethod
    def is_order_button(self):
        pass

    @property
    @abstractmethod
    def is_link(self):
        pass


@dataclass(frozen=True)
class OrderButton(Button):
    """A button that records a purchase when clicked."""
    
    drink_name: str

    @property
    def is_order_button(self):
        return True

    @property
    def is_link(self):
        return False


@dataclass(frozen=True)
class LinkButton(Button):
    """A button that changes the currently visible layout."""

    layout: Layout

    @property
    def is_order_button(self):
        return False

    @property
    def is_link(self):
        return True
