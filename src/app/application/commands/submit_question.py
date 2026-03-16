import uuid
from dataclasses import dataclass

from app.application.common.ports.message_status_repository import (
    MessageStatusRepository,
)
from app.application.common.ports.question_publisher import QuestionPublisher
from app.application.common.ports.session_repository import SessionRepository
from app.domain.services.question import QuestionDomainService
from app.domain.value_objects.session_id import SessionId


@dataclass(frozen=True)
class SubmitQuestionCommand:
    session_id: uuid.UUID
    question: str


@dataclass(frozen=True)
class SubmitQuestionResult:
    session_id: uuid.UUID
    message_id: uuid.UUID


class SubmitQuestionHandler:
    """
    Application service that orchestrates:
      1. Session upsert
      2. Message aggregate creation (domain service)
      3. Status initialisation in Redis
      4. Question publication to NATS
    """

    def __init__(
        self,
        session_repository: SessionRepository,
        message_status_repository: MessageStatusRepository,
        question_publisher: QuestionPublisher,
        question_domain_service: QuestionDomainService,
    ) -> None:
        self._session_repo = session_repository
        self._status_repo = message_status_repository
        self._publisher = question_publisher
        self._domain_service = question_domain_service

    async def handle(self, command: SubmitQuestionCommand) -> SubmitQuestionResult:
        session_id = SessionId.from_str(str(command.session_id))

        await self._session_repo.create_or_renew(session_id)

        message = self._domain_service.create_message(
            session_id=session_id,
            question_text=command.question,
        )

        await self._status_repo.set_processing(
            session_id=session_id,
            message_id=message.message_id,
        )

        await self._publisher.publish(message)

        return SubmitQuestionResult(
            session_id=command.session_id,
            message_id=message.message_id.value,
        )
