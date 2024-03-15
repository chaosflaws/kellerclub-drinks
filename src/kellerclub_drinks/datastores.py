"""
Interface and implementations for datastores that can be used with this
application.
"""

from __future__ import annotations

import random
import sqlite3
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from sqlite3 import IntegrityError
from typing import Any, Optional

from .model.drinks import Drink
from .model.layouts import Layout, Button, OrderButton, LinkButton


class DataStore(ABC):
    """A resource that provides persistence functionality for the application."""

    @staticmethod
    def from_settings(settings: dict[str, Any]) -> DataStore:
        """Creates a datastore based on the settings file."""

        if settings['type'] == 'sqlite':
            try:
                path = Path(settings['path'])
            except KeyError as e:
                raise ValueError('SQLite database path not specified!') from e
            return SqliteStore(path)

        if settings['type'] == 'mysql':
            raise NotImplementedError()

        raise ValueError('Unrecognized data store type!')

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


class SqliteStore(DataStore):
    """A datastore using sqlite."""

    def __init__(self, path: Path | str):
        self.path = path

    def get_all_drinks(self) -> dict[str, Drink]:
        with sqlite3.connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            sql_template = "SELECT name, display_name FROM Drink"
            return {row[0]: Drink(row[1]) for row in conn.execute(sql_template).fetchall()}

    def add_drink(self, drink: str) -> None:
        with sqlite3.connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("INSERT INTO Drink(name) VALUES (?)", (drink,))

    def add_order(self, drink: str) -> None:
        with sqlite3.connect(self.path, uri=True) as conn:
            try:
                conn.execute("PRAGMA foreign_keys = ON;")
                conn.execute("INSERT INTO PurchaseOrder(drink_name) VALUES (?)", (drink,))
            except IntegrityError as e:
                if e.sqlite_errorname == 'SQLITE_CONSTRAINT_PRIMARYKEY':
                    self._add_order_with_random_time_delta(drink, conn)
                else:
                    raise e

    @staticmethod
    def _add_order_with_random_time_delta(drink: str, conn: sqlite3.Connection):
        randomized_timestamp = SqliteStore._now_plus_random_milliseconds(1_000)
        sql_template = "INSERT INTO PurchaseOrder(time, drink_name) VALUES (?, ?)"
        conn.execute(sql_template, (randomized_timestamp, drink))

    @staticmethod
    def _now_plus_random_milliseconds(max_diff_millis: int) -> float:
        random_millis = random.randint(1, max_diff_millis)
        current_nanos = time.time_ns()
        current_millis = current_nanos // 1e6
        updated_millis = current_millis + random_millis
        updated_sec = updated_millis / 1e3
        return updated_sec

    def get_all_layouts(self) -> dict[str, Layout]:
        layout_name: str
        xpos: int
        ypos: int
        display_name: str
        drink_name: str
        linked_layout: str

        with sqlite3.connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            order_button_rows = conn.execute(self._get_all_order_buttons_template)
            link_button_rows = conn.execute(self._get_all_link_buttons_template)

        buttons_to_layouts: dict[str, list[list[Optional[Button]]]] = defaultdict(lambda: self._empty_grid(5, 5))

        for row in order_button_rows:
            layout_name, xpos, ypos, display_name, drink_name = row
            buttons_to_layouts[layout_name][xpos][ypos] = OrderButton(display_name, drink_name)

        for row in link_button_rows:
            layout_name, xpos, ypos, display_name, linked_layout = row
            buttons_to_layouts[layout_name][xpos][ypos] = LinkButton(display_name, linked_layout)

        layouts = {k: Layout(k, v) for k, v in buttons_to_layouts.items()}
        for layout in layouts:
            for rows in layout:
                for button in rows:
                    if isinstance(button, LinkButton):
                        setattr(button, 'layout', layouts[button.layout])

        return layouts

    _get_all_order_buttons_template = """
SELECT layout_name, xpos, ypos, display_name, drink_name
FROM OrderButton
JOIN SelectorButton ON OrderButton.button_id == SelectorButton.id
"""

    _get_all_link_buttons_template = """
SELECT layout_name, xpos, ypos, display_name, linked_layout
FROM LinkButton
JOIN SelectorButton ON LinkButton.button_id == SelectorButton.id
"""

    @staticmethod
    def _empty_grid(x: int, y: int) -> list[list[Optional[Button]]]:
        result: list[list[Optional[None]]] = []
        for _ in range(y):
            result.append([None] * x)
        return result
