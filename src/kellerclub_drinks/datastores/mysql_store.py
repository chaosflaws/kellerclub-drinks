from mysql.connector.pooling import MySQLConnectionPool

from .layout_factory import from_button_rows
from ..datastores.datastore import DataStore
from ..model.drinks import Drink
from ..model.layouts import Layout


class MysqlStore(DataStore):
    def __init__(self, host: str, user: str, password: str, db: str):
        self.pool = MySQLConnectionPool(host=host,
                                        user=user,
                                        password=password,
                                        database=db)

    def get_all_drinks(self) -> dict[str, Drink]:
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, display_name FROM Drink")
            return {row[0]: Drink(row[1]) for row in cursor}

    def add_drink(self, drink: str) -> None:
        pass

    def add_order(self, drink: str) -> None:
        pass

    def get_all_layouts(self) -> dict[str, Layout]:
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
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
