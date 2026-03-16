from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import cast

from app.application.common.ports.answer_streamer import AnswerStreamer
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId


@dataclass(frozen=True)
class StreamAnswerQuery:
    session_id: str
    message_id: str


class StreamAnswerHandler:
    """Application service that delegates token streaming to the port."""

    def __init__(self, answer_streamer: AnswerStreamer) -> None:
        self._streamer = answer_streamer

    def handle(self, query: StreamAnswerQuery) -> AsyncGenerator[str]:
        session_id = SessionId.from_str(query.session_id)
        message_id = MessageId.from_str(query.message_id)
        return cast(
            AsyncGenerator[str],
            self._streamer.stream(session_id, message_id),
        )
