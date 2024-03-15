import random
import sqlite3
import time
from collections import defaultdict
from pathlib import Path
from sqlite3 import IntegrityError
from typing import Optional

from .datastore import DataStore
from .layout_factory import from_button_rows
from ..model.drinks import Drink
from ..model.layouts import Button, Layout, OrderButton, LinkButton


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
        with sqlite3.connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            order_button_rows = conn.execute(self._get_all_order_buttons_template)
            link_button_rows = conn.execute(self._get_all_link_buttons_template)

        return from_button_rows(list(order_button_rows), list(link_button_rows))

    _get_all_order_buttons_template = """
SELECT
    layout_name, xpos, ypos,
    coalesce(SelectorButton.display_name, Drink.display_name) AS display_name,
    drink_name
FROM OrderButton
JOIN SelectorButton ON OrderButton.button_id = SelectorButton.id
JOIN Drink ON OrderButton.drink_name = Drink.name
"""

    _get_all_link_buttons_template = """
SELECT layout_name, xpos, ypos, display_name, linked_layout
FROM LinkButton
JOIN SelectorButton ON LinkButton.button_id = SelectorButton.id
"""
