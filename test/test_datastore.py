import unittest

from datastores import DataStore, SqliteStore


class TestDatastore(unittest.TestCase):
    def test_create__type_sqlite__returns_sqlite_store(self):
        settings = {
            'type': 'sqlite',
            'path': 'db.sqlite'
        }

        self.assertIsInstance(DataStore.create(settings), SqliteStore)
