"""
Pyinotify Reader Registry definition.

"""

import os
import asyncio
import logging
import pyinotify

from .loop_reader_registry import ReaderRegistry
from tailsocket.errors import CouldNotCreateDescriptorError

logger = logging.getLogger('tornado.application')


class EventHandler(pyinotify.ProcessEvent):
    """Pyinotify event handler, invokes registry methods on masked events.

    """

    def my_init(self, file, registry):
        self.filename = file
        self.registry = registry

    def process_IN_MODIFY(self, event):
        print("Modifying: ", event.pathname)
        with open(event.pathname, 'rb') as fd:
            fd.seek(
                self.registry.readers[event.pathname]['previous_stat'].st_size)
            self.registry.reader(fd)


class NotifyReaderRegistry(ReaderRegistry):
    """Subclass of ReaderRegistry using pyinotify handlers instead of raw
    asyncio polling for Linux compatibility.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._watch_manager = pyinotify.WatchManager()
        self._mask = pyinotify.IN_MODIFY  # TODO: does this include rolling?

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
        filename = os.path.abspath(filename)
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

        # add_watch returns a dict with the filename as a key and a watch
        # descriptor as a value
        watch_descriptor = self._watch_manager.add_watch(filename, self._mask)
        if watch_descriptor[filename] < 0:
            raise CouldNotCreateDescriptorError()

        handler = EventHandler(file=filename, registry=self)
        pyinotify.AsyncioNotifier(
            self._watch_manager,
            asyncio.get_event_loop(),
            default_proc_fun=handler)
        return watch_descriptor[filename], content

    def remove_reader_for_filename(self, filename):
        """Removes reader registration for a filename. Overridden for pyinotify.

        Args:
            filename (str): Path to file which should exist in the registry.

        """
        logger.debug('No handlers left for {}, removing'.format(filename))
        self._watch_manager.rm_watch(self.readers[filename]['descriptor'])
        del self.readers[filename]

    def remove_reader_callback_for_descriptor(self, descriptor):
        # Overridden as a no-op as it's not necessary using pyinotify.
        pass
