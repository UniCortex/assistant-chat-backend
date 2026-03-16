import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.commands.submit_question import (
    SubmitQuestionCommand,
    SubmitQuestionHandler,
)
from app.application.common.ports.message_status_repository import (
    MessageStatusRepository,
)
from app.application.common.ports.question_publisher import QuestionPublisher
from app.application.common.ports.session_repository import SessionRepository
from app.domain.ports.id_generator import IdGenerator
from app.domain.services.question import QuestionDomainService


def _make_handler() -> tuple[SubmitQuestionHandler, dict[str, AsyncMock | QuestionPublisher | MessageStatusRepository | SessionRepository]]:
    mocks: dict[str, AsyncMock | QuestionPublisher | MessageStatusRepository | SessionRepository] = {
        "session_repo": AsyncMock(spec=SessionRepository),
        "status_repo": AsyncMock(spec=MessageStatusRepository),
        "publisher": AsyncMock(spec=QuestionPublisher),
    }
    id_gen = MagicMock(spec=IdGenerator)
    id_gen.generate.return_value = uuid.uuid4()

    domain_service = QuestionDomainService(id_generator=id_gen)

    handler = SubmitQuestionHandler(
        session_repository=mocks["session_repo"],
        message_status_repository=mocks["status_repo"],
        question_publisher=mocks["publisher"],
        question_domain_service=domain_service,
    )
    return handler, mocks


@pytest.mark.asyncio
class TestSubmitQuestionHandler:
    async def test_returns_session_and_message_ids(self) -> None:
        handler, _ = _make_handler()
        session_id = uuid.uuid4()
        result = await handler.handle(SubmitQuestionCommand(session_id=session_id, question="Test?"))
        assert result.session_id == session_id
        assert isinstance(result.message_id, uuid.UUID)

    async def test_creates_or_renews_session(self) -> None:
        handler, mocks = _make_handler()
        session_id = uuid.uuid4()
        await handler.handle(SubmitQuestionCommand(session_id=session_id, question="Test?"))
        mocks["session_repo"].create_or_renew.assert_awaited_once()

    async def test_sets_status_processing(self) -> None:
        handler, mocks = _make_handler()
        await handler.handle(SubmitQuestionCommand(session_id=uuid.uuid4(), question="Test?"))
        mocks["status_repo"].set_processing.assert_awaited_once()

    async def test_publishes_question(self) -> None:
        handler, mocks = _make_handler()
        await handler.handle(SubmitQuestionCommand(session_id=uuid.uuid4(), question="Test?"))
        mocks["publisher"].publish.assert_awaited_once()
