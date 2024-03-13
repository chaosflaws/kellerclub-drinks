import multiprocessing
import os
import shutil
import sys
from typing import Any
from threading import Event
from wsgiref.simple_server import make_server
from wsgiref.types import WSGIApplication

should_exit = Event()


def main():
    os.chdir('src')
    sys.path.append('.')
    shutil.copy('../settings.json', 'settings.json')

    proc = None
    try:
        proc = multiprocessing.Process(target=start_server, args=())
        proc.start()

        while not should_exit.is_set():
            mtime = os.stat('app.wsgi').st_mtime
            should_exit.wait(1)

            if mtime != os.stat('app.wsgi').st_mtime:
                print('Restarting server...')
                proc.terminate()
                proc = multiprocessing.Process(target=start_server, args=())
                proc.start()

        proc.terminate()
    finally:
        if proc is not None:
            proc.terminate()
        os.remove('settings.json')


def get_compiled_app() -> WSGIApplication:
    with open('app.wsgi', 'rb') as app_file:
        app_globals: dict[str, Any] = {}
        exec(app_file.read(), app_globals)
        return app_globals['application']


def start_server():
    with make_server('', 8000, get_compiled_app()) as s:
        s.serve_forever()


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT,
                  lambda _, __: should_exit.set())

    main()
