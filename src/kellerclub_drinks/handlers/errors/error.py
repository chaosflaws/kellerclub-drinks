from abc import abstractmethod

from jinja2 import TemplateError

from ..handler import Handler
from ...resources import Resources
from ...response_creators import ErrorCreator, ResponseCreator


class ResistantHandler(Handler):
    """Delegates work to another handler, but catches common exceptions."""

    def handle(self, res: Resources) -> ResponseCreator:
        try:
            return self._handle(res)
        except TemplateError as e:
            print(f'Template Error: {e}')
            return ErrorHandler(400, 'Template Error').handle(res)
        except Exception as e:
            # see if datastore can do something about it
            if result := res.datastore.handle_exception(e):
                return ErrorHandler(400, f'Database Error: {result}').handle(res)

            raise e

    @abstractmethod
    def _handle(self, res: Resources) -> ResponseCreator:
        pass


class ErrorHandler(Handler):
    """
    A handler that serves a generic error message according to the selected
    status code.
    """

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    @property
    def canonical_url(self) -> str:
        return f'/{self.status_code}'

    def handle(self, res: Resources) -> ResponseCreator:
        try:
            template = res.jinjaenv.get_template(f'errors/{self.status_code}.jinja2')
            content = template.render(message=self.message)

            return ErrorCreator(self.status_code).with_content(content.encode())
        except TemplateError:
            print()
            with open('kellerclub_drinks/handlers/errors/400_jinja_error.html', 'rb') as error_file:
                return ErrorCreator(400).with_content(error_file.read())
