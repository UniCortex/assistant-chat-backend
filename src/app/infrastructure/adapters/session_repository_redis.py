import logging

from redis.asyncio import Redis

from app.application.common.ports.session_repository import SessionRepository
from app.domain.value_objects.session_id import SessionId
from app.infrastructure.adapters.redis_keys import session_key

logger = logging.getLogger(__name__)


class RedisSessionRepository(SessionRepository):
    def __init__(self, redis: Redis, session_ttl: int) -> None:
        self._redis = redis
        self._session_ttl = session_ttl

    async def create_or_renew(self, session_id: SessionId) -> None:
        key = session_key(session_id)
        exists = await self._redis.exists(key)
        await self._redis.set(key, "active", ex=self._session_ttl)
        if exists:
            logger.info("Renewed session %s", session_id)
        else:
            logger.info("Created session %s", session_id)
