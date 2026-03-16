from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.message import Message


class QuestionPublisher(ABC):
    """Port: publishes a question message to the broker for worker consumption."""

    @abstractmethod
    async def publish(self, message: Message) -> None: ...
