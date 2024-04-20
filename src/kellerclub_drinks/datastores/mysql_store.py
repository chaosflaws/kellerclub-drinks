import traceback
from datetime import datetime
from typing import Optional

from mysql.connector import Error
from mysql.connector.cursor import MySQLCursor
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection

from .layout_factory import from_button_rows
from ..datastores.datastore import DataStore
from ..model.drinks import Drink, PriceHistory
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

    def all_drinks(self) -> dict[str, Drink]:
        conn = self.pool.get_connection()
        try:
            cursor: MySQLCursor = conn.cursor()
            cursor.execute("SELECT name, display_name, base_price FROM Drink")
            return {row[0]: Drink(row[0], row[1], PriceHistory(row[2], {})) for row in cursor}
        finally:
            conn.close()

    def add_drink(self, drink: Drink) -> None:
        conn = self.pool.get_connection()
        try:
            cursor: MySQLCursor = conn.cursor()
            sql_template = "INSERT INTO Drink(name, display_name, base_price) VALUES (%s, %s, 1)"
            cursor.execute(sql_template, (drink.name, drink.display_name))
            conn.commit()
        finally:
            conn.close()

    def start_event(self, start_time: Optional[datetime] = None,
                    name: Optional[str] = None) -> None:
        conn = self.pool.get_connection()
        try:
            cursor: MySQLCursor = conn.cursor()
            if self._current_event(conn):
                raise ValueError("At least one event is still running!")

            insert_template = "INSERT INTO Event(start_time, name) VALUES (%s, %s)"
            cursor.execute(insert_template, (start_time, name))

            conn.commit()
        finally:
            conn.close()

    def stop_current_event(self, end_time: Optional[datetime] = None) -> bool:
        conn = self.pool.get_connection()
        try:
            cursor: MySQLCursor = conn.cursor()
            current_event = self._current_event(conn)
            if current_event:
                event_id, _ = current_event
                cursor.execute("UPDATE Event SET end_time = %s WHERE start_time = %s",
                               (end_time or datetime.now(), event_id))
                conn.commit()
                return True
            else:
                return False
        finally:
            conn.close()

    def current_event(self) -> Optional[Event]:
        conn = self.pool.get_connection()
        try:
            result = self._current_event(conn)
            if result:
                return Event(result[1], result[0], None)
            else:
                return None
        finally:
            conn.close()

    @staticmethod
    def _current_event(conn: PooledMySQLConnection) -> Optional[tuple[datetime, Optional[str]]]:
        cursor: MySQLCursor = conn.cursor()
        cursor.execute(MysqlStore._any_unfinished_events_template)
        return cursor.fetchone()

    _any_unfinished_events_template = """
SELECT start_time, name FROM Event WHERE end_time IS NULL LIMIT 1
"""

    def submit_order(self, event_id: datetime, drinks: list[str]) -> list[int]:
        conn = self.pool.get_connection()
        try:
            cursor: MySQLCursor = conn.cursor()
            sql_template_begin = "INSERT INTO PurchaseOrder(drink_name, event) VALUES "
            values = ", ".join('(%s, %s)' for _ in drinks)
            sql_template_end = " RETURNING id"
            sql_template = sql_template_begin + values + sql_template_end
            params: list[str | datetime] = []
            for drink in drinks:
                params.append(drink)
                params.append(event_id)
            cursor.execute(sql_template, tuple(params))
            ids = [row[0] for row in cursor.fetchall()]
            conn.commit()
            return ids
        finally:
            conn.close()

    def all_layouts(self) -> dict[str, Layout]:
        conn = self.pool.get_connection()
        try:
            cursor: MySQLCursor = conn.cursor()
            cursor.execute(self._get_all_order_buttons_template)
            order_rows = list(cursor)
            cursor.execute(self._get_all_link_buttons_template)
            link_rows = list(cursor)
            return from_button_rows(order_rows, link_rows)
        finally:
            conn.close()

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
