# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from json import JSONDecodeError

from kellerclub_drinks.settings import Settings


class TestSettings(unittest.TestCase):
    def test_parse__invalid_json__throws(self):
        with self.assertRaises(JSONDecodeError):
            Settings.from_json_string('{')
