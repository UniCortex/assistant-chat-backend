import uuid

from pydantic import BaseModel, Field


class SubmitQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Student/staff question")
    session_id: uuid.UUID = Field(..., description="Client session identifier")


class SubmitQuestionResponse(BaseModel):
    session_id: uuid.UUID
    message_id: uuid.UUID


class PollAnswerResponse(BaseModel):
    session_id: str
    message_id: str
    status: str
    answer: str | None = None


class ErrorResponse(BaseModel):
    session_id: str | None = None
    message_id: str | None = None
    status: str | None = None
    error_code: str
    detail: str
