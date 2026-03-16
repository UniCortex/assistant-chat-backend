from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId


class AnswerStreamer(ABC):
    """Port: yields SSE token chunks for a message from the broker."""

    @abstractmethod
    def stream(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> AsyncGenerator[str]: ...
