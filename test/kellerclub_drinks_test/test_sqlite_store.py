import sqlite3
import time
import unittest

from kellerclub_drinks.datastores import SqliteStore


class TestSqliteStore(unittest.TestCase):
    def setUp(self):
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            with open('../../src/init.sql', 'r') as sql_file:
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

    def test_get_all_drinks__no_drinks__returns_empty_list(self):
        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        self.assertEqual(0, len(store.get_all_drinks()))

    def test_add_order__no_timestamp__uses_current_timestamp(self):
        drink_name = 'tap_beer'
        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            db.execute("INSERT INTO DRINK(name) VALUES (?)", (drink_name,))

        store = SqliteStore('file:drinks.db?mode=memory&cache=shared')
        store.add_order(drink_name)

        with sqlite3.connect('file:drinks.db?mode=memory&cache=shared', uri=True) as db:
            timestamp = db.execute("SELECT time FROM PurchaseOrder").fetchone()[0]
            self.assertAlmostEqual(timestamp, int(time.time_ns()) // 1e9, delta=1)
