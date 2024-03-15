from pathlib import Path
from typing import Any

from .mysql_store import MysqlStore
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

    elif settings['type'] == 'mysql':
        host = settings['host']
        user = settings['user']
        password = settings['password']
        db = settings['db']
        return MysqlStore(host, user, password, db)

    raise ValueError('Unrecognized data store type!')
