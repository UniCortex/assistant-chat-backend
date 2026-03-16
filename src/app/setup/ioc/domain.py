from dishka import Provider, Scope, provide

from app.domain.ports.id_generator import IdGenerator
from app.domain.services.question import QuestionDomainService


class DomainProvider(Provider):
    scope = Scope.APP

    @provide
    def question_domain_service(
        self,
        id_generator: IdGenerator,
    ) -> QuestionDomainService:
        return QuestionDomainService(id_generator=id_generator)
