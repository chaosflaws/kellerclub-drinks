from wsgiref.types import WSGIEnvironment, StartResponse
from kellerclub_drinks.resources import Resources
from kellerclub_drinks.router import route
from kellerclub_drinks.settings import Settings


settings: Settings = Settings.get_settings()
res: Resources = Resources(settings)


def application(environ: WSGIEnvironment, start_response: StartResponse) -> list[bytes]:
    handler = route(environ)
    response_creator = handler.handle(res)
    return response_creator.serve(settings, start_response)
