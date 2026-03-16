from dataclasses import dataclass

from app.domain.value_objects.session_id import SessionId

from .base import Entity


@dataclass
class Session(Entity):
    session_id: SessionId
