from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.application.queries.stream_answer import StreamAnswerHandler, StreamAnswerQuery

router = APIRouter(route_class=DishkaRoute)


@router.get(
    "/stream",
    summary="Stream answer tokens via SSE",
)
async def stream_answer(
    session_id: str = Query(..., description="Session identifier"),
    message_id: str = Query(...),
    handler: FromDishka[StreamAnswerHandler] = ...,
) -> StreamingResponse:
    generator = handler.handle(StreamAnswerQuery(session_id=session_id, message_id=message_id))
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
