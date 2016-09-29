"""
Tailsocket's entry point module.

Starts up the Tornado application, defines logging, routing and handlers.

"""
import os
import asyncio
import logging
import selectors

from tornado import options, websocket
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.web import RequestHandler, Application, url

from tailsocket.reader_registries import get_registry
from tailsocket.log import setup_logging

logger = logging.getLogger('tornado.application')

options.define(
    "ip", default='0.0.0.0',
    help="IP address to attach the server to", type=str)
options.define(
    "port", default=os.environ.get('PORT', 8888),
    help="Port number to run the server on", type=int)
options.define(
    "policy", default='default',
    help="IOLoop policy to use, choices are 'default' or 'select'.",)
options.define(
    "ws_host_port", default=os.environ.get('WS_HOST_PORT', None),
    help="Port number to run the server on", type=str)
options.define(
    "debug", default=True,
    help="Start application in debug mode?", type=bool)
options.define(
    "webpackdevserver", default=None,
    help="Optional route to the Webpack dev server assets", type=str)


class HomePageHandler(RequestHandler):
    """Home page handler, simply render the template with the frontend.

    """

    def get(self):
        self.render(
            "templates/base.html",
            ws_host_port=options.options.ws_host_port,
            logging=options.options.logging,
            webpackdevserver=options.options.webpackdevserver,
            initial_text_value=options.options.access_log_file_path
        )


class TailWebSocketHandler(websocket.WebSocketHandler):
    """Websocket connection handler.

    """

    def __init__(self, *args, **kwargs):
        logger.debug('Init {} websocket'.format(self.__class__.__name__))
        self.app = kwargs.pop('app')
        self.filename = None
        super().__init__(*args, **kwargs)

    def check_origin(self, origin):
        """Security measure from Tornado to avoid cross domain referencing.

        """
        return True

    def open(self, name, *args, **kwargs):
        logger.info('Open websocket with: {}'.format(name))
        self.name = name

    def on_close(self):
        logger.info("Closed {} websocket".format(self.__class__.__name__))
        if self.filename is not None:
            self.app.registry.remove_handler_from_filename(self, self.filename)

    def on_message(self, message):
        """Handles messages from the websocket. The application expects full
        paths to be sent and will attempt to create readers for these files.

        Args:
            message (str): Message sent from the client.
        """
        logger.info('[{}]: Recieved message from websocket: {}'.format(
            self.name, message))
        try:
            self.app.registry.add_handler_to_filename(self, message)
            self.filename = message
        except Exception as e:
            # TODO: write an object with a message type for the frontend
            # to display in different ways?
            self.write_message("An error occurred: {}".format(e))
            logger.exception(e)


class TailSocketApplication(Application):
    """Simple main application, handles basic routes and configuration.

    """

    def __init__(self):
        self.registry = get_registry()

        handlers = [
            url(r"/", HomePageHandler, {}, 'home'),
            url(
                r"/websocket/([\w-]+)",
                TailWebSocketHandler, {"app": self}, 'websocket'),
        ]

        settings = {
            'debug': options.options.debug,
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
        }

        super(TailSocketApplication, self).__init__(handlers, **settings)


def main():
    options.parse_command_line()

    if options.options.policy == 'select':
        selector = selectors.SelectSelector()
        loop = asyncio.SelectorEventLoop(selector)
        asyncio.set_event_loop(loop)

    AsyncIOMainLoop().install()

    setup_logging()

    app = TailSocketApplication()
    app.listen(options.options.port, address=options.options.ip)
    print("Starting server on http://{}:{}".format(
        options.options.ip, options.options.port))

    asyncio.get_event_loop().run_forever()

    return app


if __name__ == '__main__':
    app = main()
