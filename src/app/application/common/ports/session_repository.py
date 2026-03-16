from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.value_objects.session_id import SessionId


class SessionRepository(ABC):
    """Port: manages client session lifecycle in persistent storage."""

    @abstractmethod
    async def create_or_renew(self, session_id: SessionId) -> None:
        """Creates the session if absent; refreshes TTL if already present."""
        ...
