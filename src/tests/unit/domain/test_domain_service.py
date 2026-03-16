import uuid
from unittest.mock import MagicMock

from app.domain.enums.message_status import MessageStatus
from app.domain.ports.id_generator import IdGenerator
from app.domain.services.question import QuestionDomainService
from app.domain.value_objects.session_id import SessionId


def _make_service(fixed_id: uuid.UUID | None = None) -> QuestionDomainService:
    generator = MagicMock(spec=IdGenerator)
    generator.generate.return_value = fixed_id or uuid.uuid4()
    return QuestionDomainService(id_generator=generator)


class TestQuestionDomainService:
    def test_creates_message_with_correct_fields(self) -> None:
        fixed_id = uuid.uuid4()
        service = _make_service(fixed_id=fixed_id)
        session_id = SessionId.from_str(str(uuid.uuid4()))

        message = service.create_message(
            session_id=session_id,
            question_text="When are the library hours?",
        )

        assert message.message_id.value == fixed_id
        assert message.session_id == session_id
        assert str(message.question) == "When are the library hours?"
        assert message.status == MessageStatus.PROCESSING

    def test_initial_status_is_always_processing(self) -> None:
        service = _make_service()
        session_id = SessionId.from_str(str(uuid.uuid4()))
        message = service.create_message(session_id=session_id, question_text="Test?")
        assert message.status == MessageStatus.PROCESSING
