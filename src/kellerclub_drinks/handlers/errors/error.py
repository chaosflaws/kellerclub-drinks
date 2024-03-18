from wsgiref.types import StartResponse

from kellerclub_drinks.handlers.common_handlers import Handler
from kellerclub_drinks.resources import Resources
from kellerclub_drinks.response_creators import ErrorCreator


class ErrorHandler(Handler):
    """
    A handler that serves a generic error message according to the selected
    status code.
    """

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        template = res.jinjaenv.get_template(f'errors/{self.status_code}.jinja2')
        content = template.render(message=self.message)

        return (ErrorCreator(self.status_code)
                .with_content(content.encode())
                .serve(start_response))
