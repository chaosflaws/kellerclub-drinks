"""Interface for datastores that can be used with this application."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..model.drinks import Drink
from ..model.layouts import Layout


class DataStore(ABC):
    """A resource that provides persistence functionality for the application."""

    @abstractmethod
    def get_all_drinks(self) -> dict[str, Drink]:
        """
        Returns a mapping from drink names to drinks for all drinks added to the
        application.
        """

    @abstractmethod
    def add_drink(self, drink: str) -> None:
        """
        Adds the drink with the given name to the list of drinks the application
        can process.
        """

    @abstractmethod
    def add_order(self, drink: str) -> None:
        """Adds an order with the current timestamp to the list of orders."""

    @abstractmethod
    def get_all_layouts(self) -> dict[str, Layout]:
        """Returns all persisted layouts, identified by their names."""
