import uuid
from unittest.mock import AsyncMock

import pytest

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
from app.application.queries.poll_answer import PollAnswerHandler, PollAnswerQuery
from app.domain.enums.message_status import MessageStatus


def _make_query() -> PollAnswerQuery:
    return PollAnswerQuery(
        session_id=str(uuid.uuid4()),
        message_id=str(uuid.uuid4()),
    )


def _make_handler(
    status: MessageStatus | None,
    answer: str | None = None,
) -> PollAnswerHandler:
    status_repo = AsyncMock(spec=MessageStatusRepository)
    result_repo = AsyncMock(spec=MessageResultRepository)
    status_repo.get_status.return_value = status
    result_repo.get_answer.return_value = answer
    return PollAnswerHandler(
        message_status_repository=status_repo,
        message_result_repository=result_repo,
    )


@pytest.mark.asyncio
class TestPollAnswerHandler:
    async def test_raises_not_ready_when_processing(self) -> None:
        handler = _make_handler(status=MessageStatus.PROCESSING)
        with pytest.raises(MessageNotReadyError):
            await handler.handle(_make_query())

    async def test_raises_not_ready_when_status_none(self) -> None:
        handler = _make_handler(status=None)
        with pytest.raises(MessageNotReadyError):
            await handler.handle(_make_query())

    async def test_returns_result_when_completed(self) -> None:
        handler = _make_handler(
            status=MessageStatus.COMPLETED,
            answer="The library is open 9–21.",
        )
        result = await handler.handle(_make_query())
        assert result.status == MessageStatus.COMPLETED
        assert result.answer == "The library is open 9–21."

    async def test_empty_answer_defaults_to_empty_string(self) -> None:
        handler = _make_handler(status=MessageStatus.COMPLETED, answer=None)
        result = await handler.handle(_make_query())
        assert result.answer == ""

    async def test_raises_failed_with_detail_when_failed(self) -> None:
        import json

        raw = json.dumps({"detail": "Worker OOM"})
        handler = _make_handler(status=MessageStatus.FAILED, answer=raw)
        with pytest.raises(MessageFailedError) as exc_info:
            await handler.handle(_make_query())
        assert exc_info.value.detail == "Worker OOM"

    async def test_raises_failed_with_raw_when_not_json(self) -> None:
        handler = _make_handler(status=MessageStatus.FAILED, answer="plain error")
        with pytest.raises(MessageFailedError) as exc_info:
            await handler.handle(_make_query())
        assert exc_info.value.detail == "plain error"
