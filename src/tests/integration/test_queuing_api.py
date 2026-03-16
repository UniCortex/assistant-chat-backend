"""
Integration tests for the queuing HTTP endpoints.

Dishka's `override` mechanism swaps real infrastructure adapters
for in-memory fakes — no Redis or NATS required.
"""

import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient

from app.application.commands.submit_question import SubmitQuestionHandler
from app.application.common.ports.answer_streamer import AnswerStreamer
from app.application.common.ports.message_result_repository import (
    MessageResultRepository,
)
from app.application.common.ports.message_status_repository import (
    MessageStatusRepository,
)
from app.application.common.ports.question_publisher import QuestionPublisher
from app.application.common.ports.session_repository import SessionRepository
from app.application.queries.poll_answer import PollAnswerHandler
from app.application.queries.stream_answer import StreamAnswerHandler
from app.domain.enums.message_status import MessageStatus
from app.domain.ports.id_generator import IdGenerator
from app.domain.services.question import QuestionDomainService
from app.presentation.http.controllers.root_router import api_v1_router
from app.presentation.http.errors.handlers import register_error_handlers


class _FakeInfraProvider(Provider):
    scope = Scope.APP

    def __init__(
        self,
        *,
        status: MessageStatus | None = None,
        answer: str | None = None,
        fixed_message_id: uuid.UUID | None = None,
    ) -> None:
        super().__init__()
        self._status = status
        self._answer = answer
        self._fixed_id = fixed_message_id or uuid.uuid4()

    @provide
    def session_repository(self) -> SessionRepository:
        return AsyncMock(spec=SessionRepository)

    @provide
    def message_status_repository(self) -> MessageStatusRepository:
        repo = AsyncMock(spec=MessageStatusRepository)
        repo.get_status.return_value = self._status
        return repo

    @provide
    def message_result_repository(self) -> MessageResultRepository:
        repo = AsyncMock(spec=MessageResultRepository)
        repo.get_answer.return_value = self._answer
        return repo

    @provide
    def question_publisher(self) -> QuestionPublisher:
        return AsyncMock(spec=QuestionPublisher)

    @provide
    def answer_streamer(self) -> AnswerStreamer:
        streamer = MagicMock(spec=AnswerStreamer)

        async def _gen(*_a: object, **_kw: object) -> AsyncGenerator[str]:
            yield "event: token\ndata: hello\n\n"
            yield "event: done\ndata: end\n\n"

        streamer.stream.side_effect = _gen
        return streamer

    @provide
    def id_generator(self) -> IdGenerator:
        gen = MagicMock(spec=IdGenerator)
        gen.generate.return_value = self._fixed_id
        return gen


class _AppProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def submit_question_handler(
        self,
        session_repository: SessionRepository,
        message_status_repository: MessageStatusRepository,
        question_publisher: QuestionPublisher,
        question_domain_service: QuestionDomainService,
    ) -> SubmitQuestionHandler:
        return SubmitQuestionHandler(
            session_repository=session_repository,
            message_status_repository=message_status_repository,
            question_publisher=question_publisher,
            question_domain_service=question_domain_service,
        )

    @provide
    def poll_answer_handler(
        self,
        message_status_repository: MessageStatusRepository,
        message_result_repository: MessageResultRepository,
    ) -> PollAnswerHandler:
        return PollAnswerHandler(
            message_status_repository=message_status_repository,
            message_result_repository=message_result_repository,
        )

    @provide
    def stream_answer_handler(self, answer_streamer: AnswerStreamer) -> StreamAnswerHandler:
        return StreamAnswerHandler(answer_streamer=answer_streamer)


class _DomainProvider(Provider):
    scope = Scope.APP

    @provide
    def question_domain_service(self, id_generator: IdGenerator) -> QuestionDomainService:
        return QuestionDomainService(id_generator=id_generator)


def _build_app(fake_infra: _FakeInfraProvider) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_v1_router)
    register_error_handlers(app)

    container = make_async_container(fake_infra, _DomainProvider(), _AppProvider())
    setup_dishka(container, app)
    return app


def _client(fake_infra: _FakeInfraProvider) -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=_build_app(fake_infra)),
        base_url="http://test",
    )


@pytest.mark.asyncio
class TestSubmitEndpoint:
    async def test_returns_202_with_ids(self) -> None:
        session_id = uuid.uuid4()
        fixed_msg_id = uuid.uuid4()
        fake = _FakeInfraProvider(fixed_message_id=fixed_msg_id)
        async with _client(fake) as c:
            resp = await c.post(
                "/api/v1/queuing/",
                json={"session_id": str(session_id), "question": "Hello?"},
            )
        assert resp.status_code == 202
        body = resp.json()
        assert body["session_id"] == str(session_id)
        assert body["message_id"] == str(fixed_msg_id)

    async def test_rejects_empty_question(self) -> None:
        fake = _FakeInfraProvider()
        async with _client(fake) as c:
            resp = await c.post(
                "/api/v1/queuing/",
                json={"session_id": str(uuid.uuid4()), "question": ""},
            )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestPollEndpoint:
    async def test_returns_404_when_processing(self) -> None:
        fake = _FakeInfraProvider(status=MessageStatus.PROCESSING)
        async with _client(fake) as c:
            resp = await c.get(
                "/api/v1/queuing/",
                params={
                    "session_id": str(uuid.uuid4()),
                    "message_id": str(uuid.uuid4()),
                },
            )
        assert resp.status_code == 404

    async def test_returns_200_with_answer_when_completed(self) -> None:
        fake = _FakeInfraProvider(
            status=MessageStatus.COMPLETED,
            answer="The exam is on Monday.",
        )
        async with _client(fake) as c:
            resp = await c.get(
                "/api/v1/queuing/",
                params={
                    "session_id": str(uuid.uuid4()),
                    "message_id": str(uuid.uuid4()),
                },
            )
        assert resp.status_code == 200
        assert resp.json()["answer"] == "The exam is on Monday."
        assert resp.json()["status"] == "completed"

    async def test_returns_500_when_failed(self) -> None:
        import json as _json

        raw = _json.dumps({"detail": "GPU error"})
        fake = _FakeInfraProvider(status=MessageStatus.FAILED, answer=raw)
        async with _client(fake) as c:
            resp = await c.get(
                "/api/v1/queuing/",
                params={
                    "session_id": str(uuid.uuid4()),
                    "message_id": str(uuid.uuid4()),
                },
            )
        assert resp.status_code == 500
        assert resp.json()["detail"]["detail"] == "GPU error"


@pytest.mark.asyncio
class TestStreamEndpoint:
    async def test_returns_sse_events(self) -> None:
        fake = _FakeInfraProvider()
        async with _client(fake) as c:
            resp = await c.get(
                "/api/v1/queuing/stream",
                params={
                    "session_id": str(uuid.uuid4()),
                    "message_id": str(uuid.uuid4()),
                },
            )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        text = resp.text
        assert "event: token" in text
        assert "event: done" in text
