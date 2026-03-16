import logging

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.application.commands.submit_question import (
    SubmitQuestionCommand,
    SubmitQuestionHandler,
)
from app.presentation.http.controllers.queuing.schemas import (
    SubmitQuestionRequest,
    SubmitQuestionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(route_class=DishkaRoute)


@router.post(
    "/",
    response_model=SubmitQuestionResponse,
    status_code=202,
    summary="Submit a question",
)
async def submit_question(
    body: SubmitQuestionRequest,
    handler: FromDishka[SubmitQuestionHandler],
) -> SubmitQuestionResponse:
    result = await handler.handle(
        SubmitQuestionCommand(
            session_id=body.session_id,
            question=body.question,
        )
    )
    return SubmitQuestionResponse(
        session_id=result.session_id,
        message_id=result.message_id,
    )
