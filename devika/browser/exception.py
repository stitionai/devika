class BrowserException(Exception):
    """Base exception class."""

    def __init__(self, message: str):
        super().__init__(message)


class SearchException(BrowserException):
    """Search exception class."""
