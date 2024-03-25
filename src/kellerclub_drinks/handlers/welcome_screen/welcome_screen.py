from ..errors.error import ResistantHandler
from ...resources import Resources
from ...response_creators import HtmlCreator, ResponseCreator
from ...templates import render_template


class WelcomeScreen(ResistantHandler):
    def _handle(self, res: Resources) -> ResponseCreator:
        if event := res.datastore.current_event():
            content = render_template(res.jinjaenv,
                                      'welcome_screen/welcome_screen_running_event.jinja2',
                                      event=event)
        else:
            content = render_template(res.jinjaenv,
                                      'welcome_screen/welcome_screen_no_event.jinja2')

        return HtmlCreator().with_content(content.encode())
