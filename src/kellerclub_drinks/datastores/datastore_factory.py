from pathlib import Path
from typing import Any

from ..datastores.datastore import DataStore
from ..datastores.sqlite_store import SqliteStore


def from_settings(settings: dict[str, Any]) -> DataStore:
    """Creates a datastore based on the settings file."""

    if settings['type'] == 'sqlite':
        try:
            path = Path(settings['path'])
        except KeyError as e:
            raise ValueError('SQLite database path not specified!') from e
        return SqliteStore(path)

    if settings['type'] == 'mysql':
        raise NotImplementedError()

    raise ValueError('Unrecognized data store type!')
