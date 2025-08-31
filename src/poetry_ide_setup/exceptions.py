"""Custom exceptions for poetry-ide-setup."""


class PoetryIdeSetupError(Exception):
    """Base exception for poetry-ide-setup errors."""

    pass


class PoetryNotFoundError(PoetryIdeSetupError):
    """Raised when Poetry is not found or not properly configured."""

    pass


class IdeaDirectoryNotFoundError(PoetryIdeSetupError):
    """Raised when .idea directory is not found."""

    pass


class InterpreterNotFoundError(PoetryIdeSetupError):
    """Raised when Python interpreter cannot be detected."""

    pass


class ConfigurationError(PoetryIdeSetupError):
    """Raised when IDE configuration cannot be updated."""

    pass


class XMLParsingError(PoetryIdeSetupError):
    """Raised when XML configuration files cannot be parsed or written."""

    pass
