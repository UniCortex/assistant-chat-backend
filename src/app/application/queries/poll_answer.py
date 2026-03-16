from dataclasses import dataclass

from app.application.common.exceptions.application import (
    MessageFailedError,
    MessageNotReadyError,
)
from app.application.common.ports.message_result_repository import (
    MessageResultRepository,
)
from app.application.common.ports.message_status_repository import (
    MessageStatusRepository,
)
from app.domain.enums.message_status import MessageStatus
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId


@dataclass(frozen=True)
class PollAnswerQuery:
    session_id: str
    message_id: str


@dataclass(frozen=True)
class PollAnswerResult:
    session_id: str
    message_id: str
    status: str
    answer: str


class PollAnswerHandler:
    """
    Application service that resolves the current state of a message:
      - PROCESSING  → raises MessageNotReadyError
      - COMPLETED   → returns answer text
      - FAILED      → raises MessageFailedError
    """

    def __init__(
        self,
        message_status_repository: MessageStatusRepository,
        message_result_repository: MessageResultRepository,
    ) -> None:
        self._status_repo = message_status_repository
        self._result_repo = message_result_repository

    async def handle(self, query: PollAnswerQuery) -> PollAnswerResult:
        session_id = SessionId.from_str(query.session_id)
        message_id = MessageId.from_str(query.message_id)

        status = await self._status_repo.get_status(session_id, message_id)

        if status is None or status == MessageStatus.PROCESSING:
            raise MessageNotReadyError

        if status == MessageStatus.COMPLETED:
            answer = await self._result_repo.get_answer(session_id, message_id) or ""
            return PollAnswerResult(
                session_id=query.session_id,
                message_id=query.message_id,
                status=MessageStatus.COMPLETED,
                answer=answer,
            )

        if status == MessageStatus.FAILED:
            raw = await self._result_repo.get_answer(session_id, message_id)
            import json

            detail = "internal worker error"
            if raw:
                try:
                    detail = json.loads(raw).get("detail", detail)
                except (json.JSONDecodeError, AttributeError):
                    detail = raw
            raise MessageFailedError(detail=detail)

        raise MessageNotReadyError
