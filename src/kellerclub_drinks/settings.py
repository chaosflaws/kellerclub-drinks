from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Settings:
    data_store_settings: dict[str, Any]

    @staticmethod
    def get_settings() -> Settings:
        return Settings.from_file('settings.json')

    @staticmethod
    def from_file(filename: str) -> Settings:
        try:
            settings_file = open(filename, 'r')
        except OSError as e:
            print("Could not read settings file!")
            raise e
        else:
            with settings_file:
                settings_json = json.load(settings_file)
                return Settings._parse_settings(settings_json)

    @staticmethod
    def from_json_string(json_string: str) -> Settings:
        return Settings._parse_settings(json.loads(json_string))

    @staticmethod
    def _parse_settings(settings_json) -> Settings:
        data_store_settings = settings_json['datastore']
        return Settings(data_store_settings)
