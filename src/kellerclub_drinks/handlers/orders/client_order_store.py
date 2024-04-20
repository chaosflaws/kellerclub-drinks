from http.cookies import SimpleCookie
from wsgiref.handlers import format_date_time

from kellerclub_drinks.response_creators import HttpHeader
from kellerclub_drinks.settings import Settings


class ClientOrderStore:
    def __init__(self, event_id: int):
        self.key = f'event-{event_id}-orders'

    def clear_orders(self, header: HttpHeader, _: Settings) -> None:
        cookie = _cookie(self.key)
        cookie[self.key] = ''
        cookie[self.key]['expires'] = format_date_time(0)
        _add_header(header, cookie)

    def add_order(self, order_list: list[str], drink_name: str,
                  header: HttpHeader, _: Settings) -> None:
        cookie = _cookie(self.key)
        cookie[self.key] = ','.join(order_list + [drink_name])
        _add_header(header, cookie)


def _cookie(key: str) -> SimpleCookie:
    cookie = SimpleCookie()
    cookie[key] = ''
    cookie[key]['samesite'] = 'Strict'
    cookie[key]['path'] = '/'
    return cookie


def _add_header(header: HttpHeader, cookie: SimpleCookie) -> None:
    header['Set-Cookie'] = cookie.output(header='').strip()
