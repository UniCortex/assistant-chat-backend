import uuid
from dataclasses import FrozenInstanceError

import pytest

from app.domain.exceptions.message import EmptyQuestionError
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.question_text import QuestionText
from app.domain.value_objects.session_id import SessionId


class TestSessionId:
    def test_from_str_roundtrip(self) -> None:
        raw = str(uuid.uuid4())
        sid = SessionId.from_str(raw)
        assert str(sid) == raw

    def test_equality(self) -> None:
        raw = str(uuid.uuid4())
        assert SessionId.from_str(raw) == SessionId.from_str(raw)

    def test_inequality(self) -> None:
        assert SessionId.from_str(str(uuid.uuid4())) != SessionId.from_str(str(uuid.uuid4()))

    def test_invalid_uuid_raises(self) -> None:
        with pytest.raises(ValueError):
            SessionId.from_str("not-a-uuid")


class TestMessageId:
    def test_from_str_roundtrip(self) -> None:
        raw = str(uuid.uuid4())
        mid = MessageId.from_str(raw)
        assert str(mid) == raw


class TestQuestionText:
    def test_valid_text(self) -> None:
        qt = QuestionText(value="What is the exam schedule?")
        assert str(qt) == "What is the exam schedule?"

    def test_empty_string_raises(self) -> None:
        with pytest.raises(EmptyQuestionError):
            QuestionText(value="")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(EmptyQuestionError):
            QuestionText(value="   ")

    def test_frozen_immutable(self) -> None:
        qt = QuestionText(value="Hello")
        with pytest.raises((TypeError, FrozenInstanceError)):
            qt.value = "Changed"
