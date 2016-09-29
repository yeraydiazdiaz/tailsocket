"""
Custom exceptions for TailSocket.

"""


class ExcessiveEmptyMessagesError(Exception):
    """Raised to avoid blocking the websocket with empty messages.

    """
    pass


class CouldNotCreateDescriptorError(Exception):
    """Raised when a descriptor could not be created for a file path.

    """
    pass
