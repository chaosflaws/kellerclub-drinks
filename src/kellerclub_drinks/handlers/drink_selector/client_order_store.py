from http.cookies import SimpleCookie
from wsgiref.handlers import format_date_time

from kellerclub_drinks.response_creators import HttpHeader
from kellerclub_drinks.settings import Settings


class ClientOrderStore:
    def __init__(self, event_id: int):
        self.event_id = event_id

    def clear_orders_cookie(self, header: HttpHeader, _: Settings) -> None:
        cookie = SimpleCookie()
        key = f'event-{self.event_id}-orders'
        cookie[key] = ''
        cookie[key]['samesite'] = 'Strict'
        cookie[key]['path'] = '/'
        cookie[key]['expires'] = format_date_time(0)
        header['Set-Cookie'] = cookie.output(header='').strip()
