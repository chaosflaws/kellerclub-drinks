"""
Interface and implementations for datastores that can be used with this
application.
"""

from __future__ import annotations

import random
import sqlite3
import time
from abc import ABC, abstractmethod
from pathlib import Path
from sqlite3 import IntegrityError
from typing import Any


class DataStore(ABC):
    """A resource that provides persistence functionality for the application."""

    @staticmethod
    def create(settings: dict[str, Any]) -> DataStore:
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
    def get_all_drinks(self) -> list[str]:
        """Returns the list of drinks added to the application."""

    @abstractmethod
    def add_drink(self, drink: str) -> None:
        """
        Adds the drink with the given name to the list of drinks the application
        can process.
        """

    @abstractmethod
    def add_order(self, drink: str) -> None:
        """Adds an order with the current timestamp to the list of orders."""


class SqliteStore(DataStore):
    """A datastore using sqlite."""

    def __init__(self, path: Path | str):
        self.path = path

    def get_all_drinks(self) -> list[str]:
        with sqlite3.connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            return [row[0] for row in conn.execute("SELECT name FROM Drink").fetchall()]

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
