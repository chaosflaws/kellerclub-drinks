from urllib.parse import urlunparse, ParseResult, parse_qs, urlencode

from kellerclub_drinks.handlers.errors.error import ResistantHandler
from kellerclub_drinks.resources import Resources
from kellerclub_drinks.response_creators import ResponseCreator, RedirectCreator


class DrinkSelectorSettings(ResistantHandler):
    def __init__(self, autosubmit: bool, url_parts: ParseResult):
        self.autosubmit = autosubmit
        self.url_parts = url_parts

    @property
    def canonical_url(self) -> str:
        return '/settings/drink_selector'

    def _handle(self, res: Resources) -> ResponseCreator:
        query = self.url_parts.query
        query_dict = parse_qs(query)
        if self.autosubmit:
            query_dict.pop('autosubmit', None)
        else:
            query_dict['autosubmit'] = ['false']
        url_parts = (self.url_parts.scheme,
                     self.url_parts.netloc,
                     self.url_parts.path,
                     self.url_parts.params,
                     urlencode(query_dict, doseq=True),
                     self.url_parts.fragment)
        return RedirectCreator(urlunparse(url_parts))
