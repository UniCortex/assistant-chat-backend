from .base import ApplicationError


class MessageNotReadyError(ApplicationError):
    """Raised when the answer is not yet available (still processing)."""


class MessageFailedError(ApplicationError):
    """Raised when message processing ended in failure."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)
