"""Provides global resources to the application."""

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .datastores import datastore_factory
from .datastores.datastore import DataStore
from .settings import Settings


class Resources:
    def __init__(self, settings: Settings):
        self.datastore: DataStore = datastore_factory.from_settings(settings.data_store_settings)
        self.jinjaenv = Environment(loader=FileSystemLoader("kellerclub_drinks/handlers"),
                                    autoescape=True,
                                    undefined=StrictUndefined)
