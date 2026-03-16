from redis.asyncio import Redis

from app.application.common.ports.message_status_repository import (
    MessageStatusRepository,
)
from app.domain.enums.message_status import MessageStatus
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId
from app.infrastructure.adapters.redis_keys import status_key


class RedisMessageStatusRepository(MessageStatusRepository):
    def __init__(self, redis: Redis, processing_ttl: int) -> None:
        self._redis = redis
        self._processing_ttl = processing_ttl

    async def set_processing(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> None:
        key = status_key(session_id, message_id)
        await self._redis.set(key, MessageStatus.PROCESSING, ex=self._processing_ttl)

    async def get_status(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> MessageStatus | None:
        key = status_key(session_id, message_id)
        raw: str | None = await self._redis.get(key)
        if raw is None:
            return None
        try:
            return MessageStatus(raw)
        except ValueError:
            return None
