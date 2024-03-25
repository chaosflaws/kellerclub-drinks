import traceback
from datetime import datetime
from typing import Optional

from mysql.connector import IntegrityError, Error
from mysql.connector.cursor import MySQLCursor
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection

from .layout_factory import from_button_rows
from ..datastores.datastore import DataStore, _now_plus_random_milliseconds
from ..model.drinks import Drink
from ..model.events import Event
from ..model.layouts import Layout


class MysqlStore(DataStore):
    """A datastore using a MySQL database."""

    def __init__(self, host: str, user: str, password: str, db: str):
        self.pool = MySQLConnectionPool(host=host,
                                        user=user,
                                        password=password,
                                        database=db)

    def handle_exception(self, e: Exception) -> Optional[str]:
        if isinstance(e, Error):
            print(f"MySQL Error: [{e.errno}, {e.sqlstate}] {e.msg}")
            traceback.print_exc()
            return "Some error, consult logs!"

        return None

    def get_all_drinks(self) -> dict[str, Drink]:
        with self.pool.get_connection() as conn:
            cursor: MySQLCursor = conn.cursor()
            cursor.execute("SELECT name, display_name FROM Drink")
            return {row[0]: Drink(row[0], row[1]) for row in cursor}

    def add_drink(self, drink: Drink) -> None:
        with self.pool.get_connection() as conn:
            cursor: MySQLCursor = conn.cursor()
            sql_template = "INSERT INTO Drink(name, display_name) VALUES (%s, %s)"
            cursor.execute(sql_template, (drink.name, drink.display_name))
            conn.commit()

    def start_event(self, start_time: Optional[datetime] = None,
                    name: Optional[str] = None) -> None:
        with self.pool.get_connection() as conn:
            cursor: MySQLCursor = conn.cursor()
            if self._current_event(conn):
                raise ValueError("At least one event is still running!")

            insert_template = "INSERT INTO Event(start_time, name) VALUES (%s, %s)"
            cursor.execute(insert_template, (start_time, name))

            conn.commit()

    def current_event(self) -> Optional[Event]:
        with self.pool.get_connection() as conn:
            result = self._current_event(conn)
            if result:
                return Event(result[1], result[0], None)
            else:
                return None

    @staticmethod
    def _current_event(conn: PooledMySQLConnection) -> tuple[datetime, Optional[str]]:
        cursor: MySQLCursor = conn.cursor()
        cursor.execute(MysqlStore.any_unfinished_events_template)
        return cursor.fetchone()

    any_unfinished_events_template = """
SELECT start_time, name FROM Event WHERE end_time IS NULL LIMIT 1
"""

    def add_order(self, drink: str) -> None:
        with self.pool.get_connection() as conn:
            cursor: MySQLCursor = conn.cursor()
            try:
                sql_template = "INSERT INTO PurchaseOrder(drink_name) VALUES (%s)"
                cursor.execute(sql_template, (drink,))
                conn.commit()
            except IntegrityError as e:
                if e.errno == 1062:
                    self._add_order_with_random_time_delta(drink, conn)
                else:
                    raise e

    @staticmethod
    def _add_order_with_random_time_delta(drink: str, conn: PooledMySQLConnection):
        randomized_timestamp = _now_plus_random_milliseconds(1_000)
        sql_template = "INSERT INTO PurchaseOrder(time, drink_name) VALUES (from_unixtime(%s), %s)"
        cursor = conn.cursor()
        cursor.execute(sql_template, (randomized_timestamp, drink))
        conn.commit()

    def get_all_layouts(self) -> dict[str, Layout]:
        with self.pool.get_connection() as conn:
            cursor: MySQLCursor = conn.cursor()
            cursor.execute(self._get_all_order_buttons_template)
            order_rows = list(cursor)
            cursor.execute(self._get_all_link_buttons_template)
            link_rows = list(cursor)
        return from_button_rows(order_rows, link_rows)

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
