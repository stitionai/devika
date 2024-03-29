"""LLM related exceptions."""


class LLMException(Exception):
    """Base class for LLM exceptions."""

    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return f"{self.__class__.__name__}: {super().__str__()}"

    def log(self):
        """Log the exception."""


class TokenUsageExceeded(LLMException):
    """Exception for token usage exceeded."""

    def log(self):
        """Log the exception."""

    def __str__(self):
        return f"{self.__class__.__name__}: {super().__str__()}"


class ModelNotSupported(LLMException):
    """Exception for model not supported."""

    def log(self):
        """Log the exception."""

    def __str__(self):
        return f"{self.__class__.__name__}: {super().__str__()}"


class ModelResponseTimeout(LLMException):
    """Exception for model response timeout."""

    def log(self):
        """Log the exception."""

    def __str__(self):
        return f"{self.__class__.__name__}: {super().__str__()}"


class LLMConfigException(LLMException):
    """Exception for LLM config exception."""

    def log(self):
        """Log the exception."""

    def __str__(self):
        return f"{self.__class__.__name__}: {super().__str__()}"
