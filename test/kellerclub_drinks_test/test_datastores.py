# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest

from kellerclub_drinks.datastores import DataStore, SqliteStore


class TestDatastore(unittest.TestCase):
    def test_create__type_sqlite__returns_sqlite_store(self):
        settings = {
            'type': 'sqlite',
            'path': 'db.sqlite'
        }

        self.assertIsInstance(DataStore.from_settings(settings), SqliteStore)
