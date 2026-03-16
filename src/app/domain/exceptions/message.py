from .base import DomainError


class EmptyQuestionError(DomainError):
    """Raised when a question text is blank or empty."""


class InvalidSessionIdError(DomainError):
    """Raised when a session identifier has an invalid format."""


class InvalidMessageIdError(DomainError):
    """Raised when a message identifier has an invalid format."""
