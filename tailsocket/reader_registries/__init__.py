"""
ReaderRegistry module.

Contains factory function and ReaderRegistry and NotifyReaderRegistry classes.

"""

import sys


def get_registry(*args, **kwargs):
    """ReaderRegistry factory, returns an instance of the appropriate
    ReaderRegistry class depending on the system platform.

    """
    if sys.platform == 'linux':
        import tailsocket.reader_registries.notify_reader_registry as nrr
        return nrr.NotifyReaderRegistry(*args, **kwargs)

    import tailsocket.reader_registries.loop_reader_registry as lrr
    return lrr.ReaderRegistry(*args, **kwargs)
