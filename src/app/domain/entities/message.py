from dataclasses import dataclass, field

from app.domain.enums.message_status import MessageStatus
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.question_text import QuestionText
from app.domain.value_objects.session_id import SessionId

from .base import Entity


@dataclass
class Message(Entity):
    """Aggregate root representing a single question-answer interaction."""

    message_id: MessageId
    session_id: SessionId
    question: QuestionText
    status: MessageStatus = field(default=MessageStatus.PROCESSING)
