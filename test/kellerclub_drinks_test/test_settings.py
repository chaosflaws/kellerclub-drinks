# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import unittest
from json import JSONDecodeError
from typing import Any

from kellerclub_drinks.settings import Settings


class TestSettings(unittest.TestCase):
    def test_parse_settings__invalid_json__raises(self) -> None:
        with self.assertRaises(JSONDecodeError):
            Settings._from_json_string('{')

    def test_parse_settings__cache_age_not_set__default_one_day(self) -> None:
        settings_param: dict[str, Any] = {'datastore': {}}

        settings = Settings._from_json_string(json.dumps(settings_param))

        self.assertEqual(60 * 60 * 24, settings.cache_age)

    def test_parse__read_from_file__succeeds(self) -> None:
        Settings._from_file('src/settings.json')
