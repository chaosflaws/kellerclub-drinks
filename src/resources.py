from jinja2 import Environment, FileSystemLoader

from datastores import DataStore
from settings import Settings


class Resources:
    def __init__(self, settings: Settings):
        self.datastore: DataStore = DataStore.create(settings.data_store_settings)
        self.jinjaenv = Environment(loader=FileSystemLoader("."), autoescape=True)
