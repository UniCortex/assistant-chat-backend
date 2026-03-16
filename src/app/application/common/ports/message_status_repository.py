from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.enums.message_status import MessageStatus
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId


class MessageStatusRepository(ABC):
    """Port: stores and retrieves message processing status."""

    @abstractmethod
    async def set_processing(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> None: ...

    @abstractmethod
    async def get_status(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> MessageStatus | None: ...
