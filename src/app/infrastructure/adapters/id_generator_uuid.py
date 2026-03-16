import uuid

from app.domain.ports.id_generator import IdGenerator


class UuidIdGenerator(IdGenerator):
    def generate(self) -> uuid.UUID:
        return uuid.uuid4()
