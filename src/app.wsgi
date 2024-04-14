from wsgiref.types import WSGIEnvironment, StartResponse
import locale

from kellerclub_drinks.resources import Resources
from kellerclub_drinks.routers.router import route
from kellerclub_drinks.settings import Settings


locale.setlocale(locale.LC_ALL, 'de_DE.utf8')


settings: Settings = Settings.get_settings()
res: Resources = Resources(settings)


def application(environ: WSGIEnvironment, start_response: StartResponse) -> list[bytes]:
    handler = route(environ)
    response_creator = handler.handle(res)
    return response_creator.serve(settings, start_response)
