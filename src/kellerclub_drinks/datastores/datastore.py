"""Interface for datastores that can be used with this application."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ..model.drinks import Drink
from ..model.events import Event
from ..model.layouts import Layout


class DataStore(ABC):
    """A resource that provides persistence functionality for the application."""

    @abstractmethod
    def handle_exception(self, e: Exception) -> Optional[str]:
        """
        Catches all exceptions that could be thrown by the datastore and prints
        a meaningful error message.
        """

    @abstractmethod
    def all_drinks(self) -> dict[str, Drink]:
        """
        Returns a mapping from drink names to drinks for all drinks added to the
        application.
        """

    @abstractmethod
    def add_drink(self, drink: Drink) -> None:
        """
        Adds the drink with the given name to the list of drinks the application
        can process.
        """

    @abstractmethod
    def start_event(self, start_time: Optional[datetime] = None,
                    name: Optional[str] = None) -> None:
        """Starts a new event.

        Raises a ValueError if another event is still running.
        """

    @abstractmethod
    def stop_current_event(self, end_time: Optional[datetime] = None) -> bool:
        """Stop the currently running event, if there is one.

        The end time of the event is set to the specified time, or the current
        time of no end time is supplied.

        Only one event can be running at a given time.

        Returns true if an event has been stopped and returns false otherwise.
        """

    @abstractmethod
    def current_event(self) -> Optional[Event]:
        """Returns the current event, if there is one, and None otherwise."""

    @abstractmethod
    def submit_order(self, event_id: datetime, drinks: list[str]) -> list[int]:
        """Adds orders with the current timestamp to the list of orders for the
        given event.

        Returns integers identifying the inserted orders."""

    @abstractmethod
    def all_layouts(self) -> dict[str, Layout]:
        """Returns all persisted layouts, identified by their names."""
