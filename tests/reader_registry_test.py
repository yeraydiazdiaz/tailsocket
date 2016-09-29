"""
Test suite for ReaderRegistry

"""

import os
import sys
import asyncio
import selectors
from unittest import mock

import pytest

from tailsocket.reader_registries import get_registry
from tests import conftest


DEFAULT_FILENAME = conftest.DEFAULT_FILENAME


@pytest.fixture
def safe_event_loop():
    """Fixture to fallback to `select` in Linux.

    """
    if sys.platform == 'linux':
        selector = selectors.SelectSelector()
        loop = asyncio.SelectorEventLoop(selector)
        asyncio.set_event_loop(loop)
        return loop

    return asyncio.get_event_loop_policy().new_event_loop()


@pytest.yield_fixture
def event_loop():
    """Pytest-asyncio fixture to inject a safe event loop in marked tests.

    """
    loop = safe_event_loop()
    yield loop
    loop.close()


def create_reader_and_add_handler(filename=None, handler=None, **kwargs):
    """Creates a ReaderRegistry instance watching a particular filename.

    Args:
        filename (str): Optional path to file to create, default: 'test.log'
        handler (Optional[mocked WebSocketHandler instance]):  WebSocketHandler
            instance, default to a mock with a stub of `write_message`.
        args (Optional[iterable]): Iterable of args to be passed to registry
            constructor.

    Returns:
        tuple: A ReaderRegistry instance and the (possibly new) handler
    """
    filename = filename or DEFAULT_FILENAME
    registry = get_registry(**kwargs)
    if handler is None:
        handler = mock.MagicMock()
        handler.write_message.return_value = None
    registry.add_handler_to_filename(handler, filename)
    return registry, handler


@asyncio.coroutine
def noop():
    """Convenience coroutine to force a event loop cycle.

    """
    yield from asyncio.sleep(0.0001)


def test_a_new_registry_incudes_a_readers_dictionary(
        safe_event_loop, create_log_file):
    registry = get_registry()
    assert registry.readers == {}


def test_registry_can_add_handlers_to_filenames(
        safe_event_loop, create_initialised_log_file):
    registry, handler = create_reader_and_add_handler()
    assert os.path.abspath(DEFAULT_FILENAME) in registry.readers


def test_adding_a_handler_can_optionally_not_send_first_lines(
        safe_event_loop, create_initialised_log_file):
    registry, handler = create_reader_and_add_handler(
        initial_lines_from_file=0)
    handler.write_message.assert_called_with(
        '<< File is empty, tail started >>')


def test_adding_a_handler_sends_first_lines(safe_event_loop):
    initial_content = (
        "A very long line that spans more than seventy "
        "four characters in length"
    )
    conftest._create_log_file(
        write_initial_content=True,
        initial_content="\n".join([initial_content] * 10)
    )
    registry, handler = create_reader_and_add_handler(
        initial_lines_from_file=1)
    handler.write_message.assert_called_with(initial_content)


def test_removing_the_last_handler_for_a_filename_removes_the_filename(
        safe_event_loop, create_log_file):
    registry, handler = create_reader_and_add_handler()

    assert registry.remove_handler_from_filename(handler, DEFAULT_FILENAME)
    assert DEFAULT_FILENAME not in registry.readers
    assert len(registry.readers.keys()) == 0


def test_removing_a_handler_for_a_filename_that_is_not_registered(
        safe_event_loop, create_log_file):
    registry, handler = create_reader_and_add_handler()

    assert registry.remove_handler_from_filename(
        handler, 'not-registered.log') is False


def test_removing_a_handler_that_is_not_registered(
        safe_event_loop, create_log_file):
    registry, handler = create_reader_and_add_handler()

    another_handler = mock.MagicMock()
    assert registry.remove_handler_from_filename(
        another_handler, DEFAULT_FILENAME) is False


def test_removing_one_of_many_handlers(safe_event_loop, create_log_file):
    registry, handler = create_reader_and_add_handler()
    another_handler = mock.MagicMock()
    another_handler.write_message.return_value = None
    filename = os.path.abspath(DEFAULT_FILENAME)
    registry.add_handler_to_filename(another_handler, filename)

    assert handler in registry.readers[filename]['handlers']
    assert another_handler in registry.readers[filename]['handlers']

    registry.remove_handler_from_filename(handler, filename)
    assert another_handler in registry.readers[filename]['handlers']


# Note the `event_loop` fixture is injected automatically

@pytest.mark.asyncio
def test_reader_method_is_called_on_write_event(create_log_file):
    registry, handler = create_reader_and_add_handler()
    test_log_line = 'Test log line'
    with open(DEFAULT_FILENAME, 'a') as fd:
        print(test_log_line, file=fd)

    yield from noop()

    assert handler.write_message.call_count == 2  # empty message plus new one
    handler.write_message.assert_called_with(test_log_line)


@pytest.mark.asyncio
def test_reader_method_is_called_on_successive_write_events(
        create_log_file):
    registry, handler = create_reader_and_add_handler()
    calls = []
    for i in range(5):
        test_log_line = 'Test log line {}'.format(i)
        calls.append(mock.call(test_log_line))
        with open(DEFAULT_FILENAME, 'a') as fd:
            print(test_log_line, file=fd)

        yield from noop()

    assert handler.write_message.call_count == 6  # including empty message
    handler.write_message.assert_has_calls(calls)


@pytest.mark.asyncio
def test_reader_method_detects_file_rotation(create_log_file):
    registry, handler = create_reader_and_add_handler()
    calls = []
    for i in range(10):
        test_log_line = '{} rotation log line {}'.format(
            'Before' if i < 5 else 'After', i)
        calls.append(mock.call(test_log_line))

        # on the fifth line rotate the log file
        with open(DEFAULT_FILENAME, 'a' if i != 5 else 'w') as fd:
            print(test_log_line, file=fd)

        yield from noop()

    assert handler.write_message.call_count == 11  # including empty message
    handler.write_message.assert_has_calls(calls)


def test_registry_fails_if_filename_does_not_exist(
        safe_event_loop, create_log_file):
    with pytest.raises(OSError):
        registry, handler = create_reader_and_add_handler('not-a-file.log')
