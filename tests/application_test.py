"""
Test suite for the Tornado application.

"""

import os
import sys
import asyncio
import selectors
from unittest import mock

import tornado
from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
from tornado.options import options

from tailsocket import application, log
from tests import conftest


class ApplicationTests(AsyncHTTPTestCase):

    def get_app(self):
        options.access_log_file_path = 'test.access.log'
        options.application_log_file_path = 'test.application.log'
        options.logging = 'debug'
        log.setup_logging()
        return application.TailSocketApplication()

    def get_new_ioloop(self):
        """Override the creation of the IOLoop mimicking that of application.

        The result needs to be a Tornado IOLoop instance, we first configure
        the asyncio loop and then call IOLoop configure to use it.

        """
        if sys.platform == 'linux':
            selector = selectors.SelectSelector()
            loop = asyncio.SelectorEventLoop(selector)
            asyncio.set_event_loop(loop)

        IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
        return IOLoop.current()

    def tearDown(self):
        if os.path.exists(tornado.options.options.access_log_file_path):
            os.remove(tornado.options.options.access_log_file_path)
        if os.path.exists(tornado.options.options.application_log_file_path):
            os.remove(tornado.options.options.application_log_file_path)

    def test_home_page_returns_200_and_content_and_logs(self):
        response = self.fetch('/')
        assert response.code == 200
        assert response.body is not None
        assert os.stat(
            tornado.options.options.access_log_file_path).st_size > 0

    @tornado.testing.gen_test
    def test_websocket_returns_contents_of_existing_file(self):
        conftest._create_log_file(write_initial_content=True)
        ws_url = "ws://localhost:{}/websocket/test_name".format(
            self.get_http_port())
        ws_client = yield tornado.websocket.websocket_connect(ws_url)
        ws_client.write_message(conftest.DEFAULT_FILENAME)

        response = yield ws_client.read_message()
        assert conftest.DEFAULT_TEXT in response

    @tornado.testing.gen_test
    def test_websocket_returns_file_empty_message_on_empty_existing_file(self):
        conftest._create_log_file()
        ws_url = "ws://localhost:{}/websocket/test_name".format(
            self.get_http_port())
        ws_client = yield tornado.websocket.websocket_connect(ws_url)
        ws_client.write_message(conftest.DEFAULT_FILENAME)

        response = yield ws_client.read_message()
        assert 'empty' in response.lower()

    @tornado.testing.gen_test
    def test_websocket_returns_error_message_on_non_existing_file(self):
        conftest._create_log_file()
        ws_url = "ws://localhost:{}/websocket/test_name".format(
            self.get_http_port())
        ws_client = yield tornado.websocket.websocket_connect(ws_url)
        ws_client.write_message("some-file")

        response = yield ws_client.read_message()
        assert 'error' in response.lower()

    @tornado.testing.gen_test
    @mock.patch('tailsocket.reader_registries.loop_reader_registry.ReaderRegistry.add_handler_to_filename')
    def test_websocket_opening_connection_does_not_add_handler(
            self, add_handler_to_filename):
        ws_url = "ws://localhost:{}/websocket/test_name".format(
            self.get_http_port())
        yield tornado.websocket.websocket_connect(ws_url)
        add_handler_to_filename.assert_not_called()

    @tornado.testing.gen_test
    @mock.patch('tailsocket.reader_registries.loop_reader_registry.ReaderRegistry.remove_handler_from_filename')
    def test_websocket_closing_connection_does_not_call_registry(
            self, remove_handler_from_filename):
        ws_url = "ws://localhost:{}/websocket/test_name".format(
            self.get_http_port())
        ws_client = yield tornado.websocket.websocket_connect(ws_url)
        ws_client.close()
        remove_handler_from_filename.assert_not_called()

    @tornado.testing.gen_test
    @mock.patch('tailsocket.reader_registries.loop_reader_registry.ReaderRegistry.remove_handler_from_filename')
    def test_websocket_closing_connection_does_not_call_registry(
            self, remove_handler_from_filename):
        ws_url = "ws://localhost:{}/websocket/test_name".format(
            self.get_http_port())
        ws_client = yield tornado.websocket.websocket_connect(ws_url)
        ws_client.close()
        remove_handler_from_filename.assert_not_called()

    @tornado.testing.gen_test
    @mock.patch('tailsocket.reader_registries.loop_reader_registry.ReaderRegistry.remove_handler_from_filename')
    def test_websocket_closing_connection_removes_handler(
            self, remove_handler_from_filename):
        conftest._create_log_file()
        ws_url = "ws://localhost:{}/websocket/test_name".format(
            self.get_http_port())
        ws_client = yield tornado.websocket.websocket_connect(ws_url)
        ws_client.write_message(conftest.DEFAULT_FILENAME)
        ws_client.close()
        assert len(self._app.registry.readers) == 0
