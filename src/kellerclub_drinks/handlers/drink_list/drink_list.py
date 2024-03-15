from wsgiref.types import StartResponse

from kellerclub_drinks.handlers.common_handlers import Handler
from kellerclub_drinks.resources import Resources
from kellerclub_drinks.response_creators import HtmlCreator


class DrinkList(Handler):
    """Returns the drinks currently available in the application."""

    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        drinks = res.datastore.get_all_drinks()
        template = res.jinjaenv.get_template('kellerclub_drinks/drink_list/drink_list.jinja2')
        content = template.render(drinks=drinks)
        return HtmlCreator(content.encode()).serve(start_response)
