# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest

from kellerclub_drinks.datastores.datastore_factory import from_settings
from kellerclub_drinks.datastores.sqlite_store import SqliteStore


class TestDatastore(unittest.TestCase):
    def test_from_settings__type_sqlite__returns_sqlite_store(self):
        settings = {
            'type': 'sqlite',
            'path': 'db.sqlite'
        }

        self.assertIsInstance(from_settings(settings), SqliteStore)
