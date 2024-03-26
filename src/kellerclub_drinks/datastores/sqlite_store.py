import traceback
from datetime import datetime
from pathlib import Path
from sqlite3 import IntegrityError, Error, connect, Connection
from typing import Optional

from .datastore import DataStore, _now_plus_random_milliseconds
from .layout_factory import from_button_rows
from ..model.drinks import Drink
from ..model.events import Event
from ..model.layouts import Layout


class SqliteStore(DataStore):
    """A datastore using sqlite."""

    def __init__(self, path: Path | str):
        self.path = path

    def handle_exception(self, e: Exception) -> Optional[str]:
        if isinstance(e, Error):
            print(f"SQLite3 Error: [{e.sqlite_errorcode}] {e.sqlite_errorname}")
            traceback.print_exc()
            return "Some error, consult logs!"

        return None

    def all_drinks(self) -> dict[str, Drink]:
        with connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            sql_template = "SELECT name, display_name FROM Drink"
            return {row[0]: Drink(row[0], row[1]) for row in conn.execute(sql_template).fetchall()}

    def add_drink(self, drink: Drink) -> None:
        with connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            sql_template = "INSERT INTO Drink(name, display_name) VALUES (?, ?)"
            conn.execute(sql_template, (drink.name, drink.display_name))

    def start_event(self, start_time: Optional[datetime] = None,
                    name: Optional[str] = None) -> None:
        with connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

            conn.execute("BEGIN")

            if self._current_event(conn):
                raise ValueError("At least one event is still running!")

            if start_time:
                insert_template = "INSERT INTO Event(start_time, name) VALUES (?, ?)"
                conn.execute(insert_template, (start_time, name))
            else:
                insert_template = "INSERT INTO Event(name) VALUES (?)"
                conn.execute(insert_template, (name,))

            conn.commit()

    def stop_current_event(self, end_time: Optional[datetime] = None) -> bool:
        with connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            current_event = self._current_event(conn)
            if current_event:
                event_id, _ = current_event
                conn.execute("UPDATE Event SET end_time = ? WHERE start_time = ?",
                             (end_time or datetime.now(), event_id))
                return True
            else:
                return False

    def current_event(self) -> Optional[Event]:
        with connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            result = self._current_event(conn)
            if result:
                return Event(result[1], datetime.fromtimestamp(result[0]), None)
            else:
                return None

    @staticmethod
    def _current_event(conn: Connection) -> Optional[tuple[int, Optional[str]]]:
        template = SqliteStore._current_event_template
        return conn.execute(template).fetchone()

    _current_event_template = """
SELECT start_time, name FROM Event WHERE end_time IS NULL LIMIT 1
"""

    def add_order(self, drink: str) -> None:
        with connect(self.path, uri=True) as conn:
            try:
                conn.execute("PRAGMA foreign_keys = ON;")
                conn.execute("INSERT INTO PurchaseOrder(drink_name) VALUES (?)", (drink,))
            except IntegrityError as e:
                if e.sqlite_errorname == 'SQLITE_CONSTRAINT_PRIMARYKEY':
                    self._add_order_with_random_time_delta(drink, conn)
                else:
                    raise e

    @staticmethod
    def _add_order_with_random_time_delta(drink: str, conn: Connection):
        randomized_timestamp = _now_plus_random_milliseconds(1_000)
        sql_template = "INSERT INTO PurchaseOrder(time, drink_name) VALUES (?, ?)"
        conn.execute(sql_template, (randomized_timestamp, drink))

    def all_layouts(self) -> dict[str, Layout]:
        with connect(self.path, uri=True) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

            conn.execute("BEGIN")
            order_button_rows = conn.execute(self._get_all_order_buttons_template)
            link_button_rows = conn.execute(self._get_all_link_buttons_template)
            conn.commit()

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
