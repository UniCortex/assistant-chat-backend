from __future__ import annotations

import uuid
from abc import ABC, abstractmethod


class IdGenerator(ABC):
    """Port: generates unique identifiers."""

    @abstractmethod
    def generate(self) -> uuid.UUID: ...
