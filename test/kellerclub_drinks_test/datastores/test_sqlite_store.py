# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import sqlite3
import time
import unittest
from typing import Optional

from kellerclub_drinks.datastores.sqlite_store import SqliteStore
from kellerclub_drinks.model.drinks import Drink
from kellerclub_drinks.model.layouts import OrderButton


class TestSqliteStore(unittest.TestCase):
    def setUp(self):
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            with open('../src/init-sqlite3.sql', 'r', encoding='utf8') as sql_file:
                sql = sql_file.read()
                db.executescript(sql)

    def tearDown(self):
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            db.execute("PRAGMA writable_schema = 1")
            db.execute("DELETE FROM sqlite_master")
            db.execute("PRAGMA writable_schema = 0")
            db.commit()
            db.execute("VACUUM")
            db.execute("PRAGMA integrity_check")

    def test_get_all_drinks__no_drinks__returns_empty_map(self):
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        self.assertEqual(0, len(store.all_drinks()))

    def test_add_order__no_timestamp__uses_current_timestamp(self):
        drink_name = 'tap_beer'
        display_name = 'Tap Beer .4l'
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        store.add_drink(Drink(drink_name, display_name))

        store.add_order(drink_name)

        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            timestamp = db.execute("SELECT time FROM PurchaseOrder").fetchone()[0]
            self.assertAlmostEqual(timestamp, int(time.time_ns()) // 1e9, delta=1)

    def test_get_all_layouts__no_layouts__returns_empty_map(self):
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        self.assertEqual(0, len(store.all_layouts()))

    def test_get_all_layouts__simple_layout__succeeds(self):
        drink_name = 'tap_beer'
        display_name = 'Tap Beer .4l'
        layout_name = 'simple_layout'
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        store.add_drink(Drink(drink_name, display_name))
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            self._add_layout(db, layout_name)
            self._add_order_button(db, layout_name, 0, 0, drink_name)

        layouts = store.all_layouts()

        self.assertEqual(1, len(layouts))
        self.assertIsInstance(layouts[layout_name].buttons[0][0], OrderButton)

    def test_get_all_layouts__empty_order_button_display_name__uses_drink_name(self):
        drink_name = 'tap_beer'
        display_name = 'Tap Beer .4l'
        layout_name = 'simple_layout'
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        store.add_drink(Drink(drink_name, display_name))
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            self._add_layout(db, layout_name)
            self._add_order_button(db, layout_name, 0, 0, drink_name)

        layouts = store.all_layouts()

        self.assertEqual(display_name, layouts[layout_name].buttons[0][0].display_name)

    def test_start_event__unfinished_event_exists__raises(self):
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            db.execute("INSERT INTO Event DEFAULT VALUES")
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')

        self.assertRaises(ValueError, store.start_event)

    @staticmethod
    def _add_layout(conn: sqlite3.Connection, name: str) -> None:
        insert_layout_template = "INSERT INTO SelectorLayout(name) VALUES (?)"
        conn.execute(insert_layout_template, (name,))

    @staticmethod
    def _add_order_button(conn: sqlite3.Connection, layout_name: str, xpos: int,
                          ypos: int, drink_name: str,
                          display_name: Optional[str] = None) -> None:
        inserted_row_id, = conn.execute(TestSqliteStore._insert_button_template,
                                        (layout_name, xpos, ypos, display_name)).fetchone()
        conn.execute(TestSqliteStore._insert_order_button_template,
                     (inserted_row_id, drink_name))

    _insert_button_template = """
    INSERT INTO SelectorButton(layout_name, xpos, ypos, display_name)
    VALUES (?, ?, ?, ?)
    RETURNING id
    """

    _insert_order_button_template = """
    INSERT INTO OrderButton(button_id, drink_name)
    VALUES (?, ?)
    """
