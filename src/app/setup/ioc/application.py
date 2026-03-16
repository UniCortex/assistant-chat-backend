from dishka import Provider, Scope, provide

from app.application.commands.submit_question import SubmitQuestionHandler
from app.application.common.ports.answer_streamer import AnswerStreamer
from app.application.common.ports.message_result_repository import (
    MessageResultRepository,
)
from app.application.common.ports.message_status_repository import (
    MessageStatusRepository,
)
from app.application.common.ports.question_publisher import QuestionPublisher
from app.application.common.ports.session_repository import SessionRepository
from app.application.queries.poll_answer import PollAnswerHandler
from app.application.queries.stream_answer import StreamAnswerHandler
from app.domain.services.question import QuestionDomainService


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def submit_question_handler(
        self,
        session_repository: SessionRepository,
        message_status_repository: MessageStatusRepository,
        question_publisher: QuestionPublisher,
        question_domain_service: QuestionDomainService,
    ) -> SubmitQuestionHandler:
        return SubmitQuestionHandler(
            session_repository=session_repository,
            message_status_repository=message_status_repository,
            question_publisher=question_publisher,
            question_domain_service=question_domain_service,
        )

    @provide
    def poll_answer_handler(
        self,
        message_status_repository: MessageStatusRepository,
        message_result_repository: MessageResultRepository,
    ) -> PollAnswerHandler:
        return PollAnswerHandler(
            message_status_repository=message_status_repository,
            message_result_repository=message_result_repository,
        )

    @provide
    def stream_answer_handler(
        self,
        answer_streamer: AnswerStreamer,
    ) -> StreamAnswerHandler:
        return StreamAnswerHandler(answer_streamer=answer_streamer)
