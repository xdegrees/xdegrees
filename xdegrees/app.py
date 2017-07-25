#!/usr/bin/env python

import logging
import os

import tornado
from tornado.options import parse_command_line, define, options

from .http.handlers import MainHandler, SeparationsSearchHandler, VersionHandler

LOGGER = logging.getLogger(__name__)

define('port', type=int, default=1792, help='The port to listen on')
define('debug', type=bool, default=False, help='Whether to run in debug mode')
define('search_url', type=str, default='http://localhost:3000/v1/separations',
       help='The WhitePages API wrapper')
define('search_timeout_seconds', type=int, default=21.1,
       help='The WhitePages API wrapper connection timeout')


class Application(tornado.web.Application):
    """
    Build an Application from Tornado's options singleton.
    Args:
        search_url (str): the WhitePages search URL
        search_timeout_seconds (int): the connect and read timeout
        debug: tornado's "debug" mode (enables autoreload, serve_traceback, etc.)
    """
    def __init__(self, search_url, search_timeout_seconds, debug=False):
        settings = dict(
            debug=debug,
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'templates')
        )

        search_handler_settings = dict(
            search_url=search_url,
            search_timeout_seconds=search_timeout_seconds
        )
        handlers = [
            (r"/", MainHandler),
            (r'/version', VersionHandler),
            (r'/separations', SeparationsSearchHandler, search_handler_settings)
        ]

        super(Application, self).__init__(handlers, **settings)


def main():
    # TODO use tornado.options.parse_config_file("/etc/server.conf") instead?
    parse_command_line()
    LOGGER.info('search_url: %s', options.search_url)
    LOGGER.info('search_timeout_seconds: %s', options.search_timeout_seconds)

    app = Application(options.search_url, options.search_timeout_seconds, debug=options.debug)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)

    LOGGER.info('Accepting requests')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
