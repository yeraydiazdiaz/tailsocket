"""
Fixtures for test suites.

"""

import pytest

DEFAULT_FILENAME = 'test.log'
DEFAULT_TEXT = 'Start test log'


def _create_log_file(
        filename=None, write_initial_content=False, initial_content=None):
    """Setup fixture to create a new test log file.

    Args:
        filename (Optional[str]): Path to file to create, default: 'test.log'
        write_initial_content (Optional[bool]): Write some test content to the
            file.
        initial_content (Optional[str]): Content to be written.
    """
    filename = filename or DEFAULT_FILENAME
    with open(filename, 'w') as fd:
        if write_initial_content:
            print(initial_content or DEFAULT_TEXT, file=fd)


@pytest.fixture()
def create_initialised_log_file():
    return _create_log_file(write_initial_content=True)


@pytest.fixture()
def create_log_file():
    return _create_log_file()
