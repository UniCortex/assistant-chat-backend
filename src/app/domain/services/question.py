from app.domain.entities.message import Message
from app.domain.enums.message_status import MessageStatus
from app.domain.ports.id_generator import IdGenerator
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.question_text import QuestionText
from app.domain.value_objects.session_id import SessionId


class QuestionDomainService:
    """Stateless domain service: assembles a new Message aggregate."""

    def __init__(self, id_generator: IdGenerator) -> None:
        self._id_generator = id_generator

    def create_message(self, session_id: SessionId, question_text: str) -> Message:
        return Message(
            message_id=MessageId(value=self._id_generator.generate()),
            session_id=session_id,
            question=QuestionText(value=question_text),
            status=MessageStatus.PROCESSING,
        )
