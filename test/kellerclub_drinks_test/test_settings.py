import unittest
from json import JSONDecodeError

from kellerclub_drinks.settings import Settings


class TestSettings(unittest.TestCase):
    def test_parse__invalid_json__throws(self):
        with self.assertRaises(JSONDecodeError):
            Settings.from_json_string('{')
