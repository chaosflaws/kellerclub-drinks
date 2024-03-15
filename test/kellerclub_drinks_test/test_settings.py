# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from json import JSONDecodeError

from kellerclub_drinks.settings import Settings


class TestSettings(unittest.TestCase):
    def test_parse__invalid_json__raises(self):
        with self.assertRaises(JSONDecodeError):
            Settings._from_json_string('{')
