import logging

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query

from app.application.common.exceptions.application import (
    MessageFailedError,
    MessageNotReadyError,
)
from app.application.queries.poll_answer import PollAnswerHandler, PollAnswerQuery
from app.presentation.http.controllers.queuing.schemas import PollAnswerResponse

logger = logging.getLogger(__name__)

router = APIRouter(route_class=DishkaRoute)


@router.get(
    "/",
    response_model=PollAnswerResponse,
    summary="Poll for answer",
)
async def poll_answer(
    session_id: str = Query(..., description="Session identifier"),
    message_id: str = Query(...),
    handler: FromDishka[PollAnswerHandler] = ...,
) -> PollAnswerResponse:
    try:
        result = await handler.handle(PollAnswerQuery(session_id=session_id, message_id=message_id))
    except MessageNotReadyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "application_error", "detail": "not ready yet"},
        ) from exc
    except MessageFailedError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "session_id": session_id,
                "message_id": message_id,
                "status": "failed",
                "error_code": "application_error",
                "detail": exc.detail,
            },
        ) from exc

    return PollAnswerResponse(
        session_id=result.session_id,
        message_id=result.message_id,
        status=result.status,
        answer=result.answer,
    )
