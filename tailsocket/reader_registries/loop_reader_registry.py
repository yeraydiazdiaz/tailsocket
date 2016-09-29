"""
ReaderRegistry definition and application instance.

"""

import os
import asyncio
import logging
from functools import partial

from tailsocket.errors import ExcessiveEmptyMessagesError

logger = logging.getLogger('tornado.application')


class ReaderRegistry():
    """Handles the creation of a reader functions against filenames requested
    by WebSocketHandler instances.

    Saves a dict with file names as keys and another dict as values storing
    the file descriptor being watched for read events, the latest stat
    info of the file and an array of the handlers to be notified.

    Args:
        initial_lines_from_file (Optional[int]): Lines to read from file on
            creation of a reader, defaults to 10.

    """

    def __init__(self, initial_lines_from_file=10):
        self.readers = {}
        self.initial_lines_from_file = initial_lines_from_file
        self.empty_msg_count = 0

    def read_last_lines_from_file(self, n, fd, offset=None):
        """Reads n lines from f with an offset of offset lines.  The return
        value is a tuple in the form ``(lines, has_more)`` where `has_more` is
        an indicator that is `True` if there are more lines in the file.

        Taken from http://stackoverflow.com/a/692616/3020799

        """
        avg_line_length = 74
        to_read = n + (offset or 0)

        while True:
            try:
                fd.seek(-(int(avg_line_length) * to_read), 2)
            except IOError:
                # woops.  apparently file is smaller than what we want
                # to step back, go to the beginning instead
                fd.seek(0)

            pos = fd.tell()
            lines = fd.read().splitlines()
            if len(lines) >= to_read or pos == 0:
                return (
                    [line.decode() for line in
                        lines[-to_read:offset and -offset or None]],
                    len(lines) > to_read or pos > 0
                )
            avg_line_length *= 1.3

    def create_reader(self, filename, read_last_n_lines=10):
        """Opens the specified file and creates the reader callback.

        Optionally returns the last few lines of content.

        Args:
            filename (str): Path of the file to create reader for.
            read_last_n_lines (Optional[int]): Optional number of lines of
                content to be returned

        Returns:
            tuple: A file descriptor and possibly empty string of content

        """
        logger.debug('Creating reader for {}'.format(filename))
        fd = open(filename, 'rb')
        if read_last_n_lines:
            logger.debug('Reading last {} lines'.format(read_last_n_lines))
            content, _ = self.read_last_lines_from_file(
                read_last_n_lines, fd)
            content = '\n'.join(content)
        else:
            fd.seek(0, os.SEEK_END)
            content = ''

        loop = asyncio.get_event_loop()
        # TODO: fileno() is required for epoll or uvloop policies
        loop.add_reader(fd, partial(self.reader, fd))
        return fd, content

    def add_handler_to_filename(self, ws_handler, filename):
        """Adds a WebSocketHandler instance to a filename path, creating a
        reader if necessary.

        Args:
            ws_handler (WebSocketHandler): WebSocketHandler to attach a file
                reader to.
            filename (str): Path to file to create the reader for.

        """
        logger.debug('Adding handler for {}'.format(filename))
        filename = os.path.abspath(filename)
        if filename not in self.readers:
            logger.debug(
                '{} not in readers, adding descriptor'.format(filename))
            fd, content = self.create_reader(
                filename, self.initial_lines_from_file)
            self.readers[filename] = {
                'descriptor': fd,
                'previous_stat': os.stat(filename),
                'handlers': [ws_handler]
            }
            if content:
                ws_handler.write_message(content)
            else:
                ws_handler.write_message('<< File is empty, tail started >>')
        else:
            logger.debug('{} already in readers, adding handler'.format(
                filename))
            self.readers[filename]['handlers'].append(ws_handler)

    def remove_handler_from_filename(self, ws_handler, filename):
        """Removes a WebSocketHandler instance from a filename path entry.

        If a filename has no more handler it will be removed from the registry.

        Args:
            ws_handler (WebSocketHandler): WebSocketHandler to remove.
            filename (str): Path to file which should exist in the registry.

        Returns:
            bool: True if handler was removed correctly.

        """
        filename = os.path.abspath(filename)
        logger.debug('Removing handler for {}'.format(filename))
        try:
            if ws_handler not in self.readers[filename]['handlers']:
                logger.warning(
                    'Attempted to remove a handler not present in the registry'
                    ' for filename {}'.format(filename))
                return False
        except KeyError:
            logger.warning(
                'Attempted to remove a handler from a filename {} not present'
                ' in the registry'.format(filename))
            return False

        self.readers[filename]['handlers'].remove(ws_handler)
        if not self.readers[filename]['handlers']:
            self.remove_reader_for_filename(filename)

        return True

    def remove_reader_for_filename(self, filename):
        """Removes reader registration for a filename.

        Args:
            filename (str): Path to file which should exist in the registry.

        """
        logger.debug('No handlers left for {}, removing'.format(filename))
        loop = asyncio.get_event_loop()
        loop.remove_reader(self.readers[filename]['descriptor'])
        self.readers[filename]['descriptor'].close()
        del self.readers[filename]

    def reader(self, descriptor):
        """Reader callback for a file descriptor. Handles reading the last line
        of text and sending it to all registered handlers.

        Also detects rotation of a the file based on the stat info.

        Args:
            descriptor (file-like): The descriptor attached to the callback.

        """
        filename = descriptor.name
        logger.debug('Reader for {}'.format(filename))

        stat = os.stat(filename)
        reader = self.readers[filename]
        if stat.st_size == reader['previous_stat'].st_size:
            # Ignore calls if the size is the same
            # Should only happen when using the `select` event loop
            return
        elif stat.st_size < reader['previous_stat'].st_size:
            logger.info('Detected rotation on file {} - Sizes {} < {}'.format(
                filename, stat.st_size, reader['previous_stat'].st_size))

            self.remove_reader_callback_for_descriptor(descriptor)
            reader['descriptor'], msg = self.create_reader(filename, 1)
        else:
            msg = descriptor.read().decode()

        msg = msg.strip()
        self.send_message_to_handlers(msg, reader['handlers'])
        reader['previous_stat'] = stat

    def remove_reader_callback_for_descriptor(self, descriptor):
        """Removes the reader callback for a particular descriptor.

        Args:
            descriptor (file-like): The descriptor to remove the callback for.
        """
        loop = asyncio.get_event_loop()
        loop.remove_reader(descriptor)

    def send_message_to_handlers(self, message, handlers):
        """Sends a message string to the handlers

        Also handles empty messages and raises to avoid overloading the client.

        Args:
            message (str): The message to be sent.
            handlers (list): List of WebSocketHandlers to write the message.

        """
        logger.info("Sending: '{}' to handlers".format(message))

        if not message:
            logger.warning('Reader called with no message, wasted call?')
            self.empty_msg_count += 1
            if self.empty_msg_count > 10:
                raise ExcessiveEmptyMessagesError()

        for handler in handlers:
            handler.write_message(message)
