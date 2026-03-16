from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId


class MessageResultRepository(ABC):
    """Port: retrieves the completed answer text for a message."""

    @abstractmethod
    async def get_answer(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> str | None: ...
