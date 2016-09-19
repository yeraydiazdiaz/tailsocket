"""
Custom exceptions for TailSocket.

"""


class ExcessiveEmptyMessagesError(Exception):
    """Raised to avoid blocking the websocket with empty messages.

    """
    pass
