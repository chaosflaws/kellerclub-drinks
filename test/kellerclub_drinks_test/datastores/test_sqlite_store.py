# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import sqlite3
import time
import unittest

from kellerclub_drinks.datastores.sqlite_store import SqliteStore
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
        self.assertEqual(0, len(store.get_all_drinks()))

    def test_add_order__no_timestamp__uses_current_timestamp(self):
        drink_name = 'tap_beer'
        display_name = 'Tap Beer .4l'
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            sql_template = "INSERT INTO DRINK(name, display_name) VALUES (?, ?)"
            db.execute(sql_template, (drink_name, display_name))

        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        store.add_order(drink_name)

        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            timestamp = db.execute("SELECT time FROM PurchaseOrder").fetchone()[0]
            self.assertAlmostEqual(timestamp, int(time.time_ns()) // 1e9, delta=1)

    def test_get_all_layouts__no_layouts_returns_empty_map(self):
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        self.assertEqual(0, len(store.get_all_layouts()))

    def test_get_all_layouts__simple_layout__succeeds(self):
        drink_name = 'tap_beer'
        display_name = 'Tap Beer .4l'
        layout_name = 'simple_layout'
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            insert_drink_template = "INSERT INTO DRINK(name, display_name) VALUES (?, ?)"
            db.execute(insert_drink_template, (drink_name, display_name))
            insert_layout_template = "INSERT INTO SelectorLayout(name) VALUES (?)"
            db.execute(insert_layout_template, (layout_name,))
            insert_button_template = "INSERT INTO SelectorButton(layout_name, xpos, ypos, display_name) VALUES (?, ?, ?, ?) RETURNING id"
            inserted_row_id, = db.execute(insert_button_template, (layout_name, 0, 0, 'beer')).fetchone()
            insert_order_button_template = "INSERT INTO OrderButton(button_id, drink_name) VALUES (?, ?)"
            db.execute(insert_order_button_template, (inserted_row_id, drink_name))

        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        layouts = store.get_all_layouts()

        self.assertEqual(1, len(layouts))
        self.assertIsInstance(layouts[layout_name].buttons[0][0], OrderButton)
