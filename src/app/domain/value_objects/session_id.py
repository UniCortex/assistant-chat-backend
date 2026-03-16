import uuid
from dataclasses import dataclass

from .base import ValueObject


@dataclass(frozen=True)
class SessionId(ValueObject):
    value: uuid.UUID

    @classmethod
    def from_str(cls, raw: str) -> "SessionId":
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)
