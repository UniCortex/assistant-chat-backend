import asyncio
import json
import logging
import re
from collections.abc import AsyncGenerator

from nats.aio.client import Client
from nats.aio.msg import Msg

from app.application.common.ports.answer_streamer import AnswerStreamer
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.session_id import SessionId

logger = logging.getLogger(__name__)

_SSE_TIMEOUT = 60.0
_MAX_COALESCE_BUFFER = 4096


def _sse_event(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


def _take_whitespace_delimited_prefixes(buffer: str) -> tuple[str, list[str]]:
    """Split leading segments that end at the first whitespace run (inclusive)."""
    emitted: list[str] = []
    rest = buffer
    while True:
        m = re.search(r"\s+", rest)
        if not m:
            break
        emitted.append(rest[: m.end()])
        rest = rest[m.end() :]
    return rest, emitted


def _flush_oversized_tail(buffer: str, max_len: int) -> tuple[str, list[str]]:
    if len(buffer) <= max_len:
        return buffer, []
    return "", [buffer]


class NatsAnswerStreamer(AnswerStreamer):
    def __init__(
        self,
        nats_client: Client,
        answers_subject_prefix: str,
    ) -> None:
        self._nats = nats_client
        self._prefix = answers_subject_prefix

    async def stream(
        self,
        session_id: SessionId,
        message_id: MessageId,
    ) -> AsyncGenerator[str]:
        subject = f"{self._prefix}{message_id}"
        queue: asyncio.Queue[str | None] = asyncio.Queue()

        async def _on_message(msg: Msg) -> None:
            try:
                payload = json.loads(msg.data.decode())
                event_type: str = payload.get("event", "token")
                data: str = payload.get("data", "")
                await queue.put(json.dumps({"event": event_type, "data": data}))
                if event_type == "done":
                    await queue.put(None)
            except Exception as exc:  # noqa: BLE001
                logger.error("SSE handler error: %s", exc)
                await queue.put(None)

        sub = await self._nats.subscribe(subject, cb=_on_message)
        logger.info("SSE subscribed to %s", subject)

        token_buffer = ""
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=_SSE_TIMEOUT)
                except TimeoutError:
                    logger.warning("SSE timeout for message_id=%s", message_id)
                    if token_buffer:
                        yield _sse_event("token", token_buffer)
                    yield _sse_event("done", "end")
                    break

                if item is None:
                    if token_buffer:
                        yield _sse_event("token", token_buffer)
                    yield _sse_event("done", "end")
                    break

                parsed = json.loads(item)
                if parsed["event"] == "done":
                    if token_buffer:
                        yield _sse_event("token", token_buffer)
                    yield _sse_event("done", "end")
                    break

                chunk = parsed["data"]
                if not isinstance(chunk, str):
                    chunk = str(chunk)
                token_buffer += chunk
                token_buffer, emitted = _take_whitespace_delimited_prefixes(token_buffer)
                for part in emitted:
                    yield _sse_event("token", part)
                token_buffer, forced = _flush_oversized_tail(
                    token_buffer,
                    _MAX_COALESCE_BUFFER,
                )
                for part in forced:
                    yield _sse_event("token", part)
        finally:
            await sub.unsubscribe()
            logger.info("SSE unsubscribed from %s", subject)
