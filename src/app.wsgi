from wsgiref.types import WSGIEnvironment, StartResponse
from datastores import DataStore
from resources import Resources
from router import route
from settings import Settings


settings: Settings = Settings.get_settings()
res: Resources = Resources(settings)


def application(environ: WSGIEnvironment, start_response: StartResponse) -> list[bytes]:
    handler = route(environ)
    return handler.handle(res, start_response)
