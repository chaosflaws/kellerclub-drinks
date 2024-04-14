from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Settings:
    """Application settings that can be adjusted in a settings file."""

    data_store_settings: dict[str, Any]
    cache_age: int

    @staticmethod
    def get_settings() -> Settings:
        """Returns the settings in the currently evaluated settings file."""

        return Settings._from_file('settings.json')

    @staticmethod
    def _from_file(filename: str) -> Settings:
        try:
            settings_file = open(filename, 'r', encoding='utf8')
        except OSError as e:
            print("Could not read settings file!")
            raise e

        with settings_file:
            settings_json = json.load(settings_file)
            return Settings._parse_settings(settings_json)

    @staticmethod
    def _from_json_string(json_string: str) -> Settings:
        return Settings._parse_settings(json.loads(json_string))

    @staticmethod
    def _parse_settings(settings_json: dict[str, Any]) -> Settings:
        data_store_settings = settings_json['datastore']

        if 'cacheAge' in settings_json:
            cache_age = max(settings_json['cacheAge'], 0)
        else:
            cache_age = 60 * 60 * 24  # one day

        return Settings(data_store_settings, cache_age)
