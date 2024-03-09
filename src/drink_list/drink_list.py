from wsgiref.types import StartResponse

from handlers import Handler
from resources import Resources
from response_creators import HtmlCreator


class DrinkList(Handler):
    def handle(self, res: Resources, start_response: StartResponse) -> list[bytes]:
        drinks = res.datastore.get_all_drinks()
        template = res.jinjaenv.get_template('drink_list/drink_list.html')
        content = template.render(drinks=drinks)
        return HtmlCreator(content.encode()).serve(start_response)
