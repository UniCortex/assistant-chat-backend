from dataclasses import dataclass

from .base import ValueObject


@dataclass(frozen=True)
class QuestionText(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            from app.domain.exceptions.message import EmptyQuestionError

            raise EmptyQuestionError("Question text cannot be empty.")

    def __str__(self) -> str:
        return self.value
