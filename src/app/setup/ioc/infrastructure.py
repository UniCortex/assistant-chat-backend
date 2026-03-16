from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from nats import connect as nats_connect
from nats.aio.client import Client as NatsClient
from redis.asyncio import Redis, from_url

from app.application.common.ports.answer_streamer import AnswerStreamer
from app.application.common.ports.message_result_repository import (
    MessageResultRepository,
)
from app.application.common.ports.message_status_repository import (
    MessageStatusRepository,
)
from app.application.common.ports.question_publisher import QuestionPublisher
from app.application.common.ports.session_repository import SessionRepository
from app.domain.ports.id_generator import IdGenerator
from app.infrastructure.adapters.id_generator_uuid import UuidIdGenerator
from app.infrastructure.adapters.message_result_repository_redis import (
    RedisMessageResultRepository,
)
from app.infrastructure.adapters.message_status_repository_redis import (
    RedisMessageStatusRepository,
)
from app.infrastructure.adapters.question_publisher_nats import NatsQuestionPublisher
from app.infrastructure.adapters.session_repository_redis import RedisSessionRepository
from app.infrastructure.streaming.answer_streamer_nats import NatsAnswerStreamer
from app.setup.config.settings import AppSettings


class InfrastructureProvider(Provider):
    scope = Scope.APP

    @provide
    async def redis(self, settings: AppSettings) -> AsyncGenerator[Redis]:
        client: Redis = await from_url(settings.redis_url, decode_responses=True)
        try:
            yield client
        finally:
            await client.aclose()

    @provide
    async def nats_client(self, settings: AppSettings) -> AsyncGenerator[NatsClient]:
        client = await nats_connect(settings.nats_url)
        try:
            yield client
        finally:
            await client.drain()

    @provide
    def session_repository(
        self,
        redis: Redis,
        settings: AppSettings,
    ) -> SessionRepository:
        return RedisSessionRepository(redis=redis, session_ttl=settings.session_ttl)

    @provide
    def message_status_repository(
        self,
        redis: Redis,
        settings: AppSettings,
    ) -> MessageStatusRepository:
        return RedisMessageStatusRepository(
            redis=redis,
            processing_ttl=settings.processing_ttl,
        )

    @provide
    def message_result_repository(self, redis: Redis) -> MessageResultRepository:
        return RedisMessageResultRepository(redis=redis)

    @provide
    def question_publisher(
        self,
        nats_client: NatsClient,
        settings: AppSettings,
    ) -> QuestionPublisher:
        return NatsQuestionPublisher(
            nats_client=nats_client,
            subject=settings.nats_subject_questions,
        )

    @provide
    def answer_streamer(
        self,
        nats_client: NatsClient,
        settings: AppSettings,
    ) -> AnswerStreamer:
        return NatsAnswerStreamer(
            nats_client=nats_client,
            answers_subject_prefix=settings.nats_subject_answers_prefix,
        )

    @provide
    def id_generator(self) -> IdGenerator:
        return UuidIdGenerator()
