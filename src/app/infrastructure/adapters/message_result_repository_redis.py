from typing import cast

from redis.asyncio import Redis

from app.application.common.ports.message_result_repository import (
    MessageResultRepository,
)
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId
from app.infrastructure.adapters.redis_keys import result_key


class RedisMessageResultRepository(MessageResultRepository):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get_answer(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> str | None:
        raw = await self._redis.get(result_key(session_id, message_id))
        return cast("str | None", raw)
