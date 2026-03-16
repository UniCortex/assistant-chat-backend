import json
import logging

from nats.aio.client import Client

from app.application.common.ports.question_publisher import QuestionPublisher
from app.domain.entities.message import Message

logger = logging.getLogger(__name__)


class NatsQuestionPublisher(QuestionPublisher):
    def __init__(self, nats_client: Client, subject: str) -> None:
        self._nats = nats_client
        self._subject = subject

    async def publish(self, message: Message) -> None:
        payload = json.dumps(
            {
                "session_id": str(message.session_id),
                "message_id": str(message.message_id),
                "question": str(message.question),
            }
        ).encode()
        await self._nats.publish(self._subject, payload)
        logger.info(
            "Published question message_id=%s session_id=%s",
            message.message_id,
            message.session_id,
        )
