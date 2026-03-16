import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.base import DomainError
from app.domain.exceptions.message import EmptyQuestionError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(EmptyQuestionError)
    async def _empty_question(request: Request, exc: EmptyQuestionError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error_code": "validation_error", "detail": str(exc)},
        )

    @app.exception_handler(DomainError)
    async def _domain_error(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning("Unhandled domain error: %s", exc)
        return JSONResponse(
            status_code=400,
            content={"error_code": "domain_error", "detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unexpected error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error_code": "internal_error", "detail": "Internal server error"},
        )
