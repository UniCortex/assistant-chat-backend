from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId


def session_key(session_id: SessionId) -> str:
    return f"session:{session_id}"


def status_key(session_id: SessionId, message_id: MessageId) -> str:
    return f"message:{session_id}:{message_id}:status"


def result_key(session_id: SessionId, message_id: MessageId) -> str:
    return f"message:{session_id}:{message_id}:result"
