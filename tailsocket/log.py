import logging

from tornado.options import define, options

loggers = {
    'access': logging.getLogger('tornado.access'),
    'application': logging.getLogger('tornado.application'),
}

define(
    'access_log_file_path', default='tailsocket.access.log',
    help="The path to the app's access log")


define(
    'application_log_file_path', default='tailsocket.application.log',
    help="The path to the app's application log")


# Tornado's logging accepts debug|info|warning|error|none map to logging consts
LOGGING_MAPPING = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'none': logging.NOTSET,
}


def setup_logging():
    """Setup logging for the application based on the Tornado options.

    """
    for name, logger in loggers.items():
        logger.setLevel(LOGGING_MAPPING.get(options.logging, logging.DEBUG))
        handler = logging.FileHandler(
            getattr(options, '{}_log_file_path'.format(name))
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
