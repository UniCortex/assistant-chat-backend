from app.infrastructure.streaming.answer_streamer_nats import (
    _MAX_COALESCE_BUFFER,
    _flush_oversized_tail,
    _take_whitespace_delimited_prefixes,
)


def _feed_tokens(parts: list[str]) -> tuple[str, list[str]]:
    """Mimic NatsAnswerStreamer token accumulation + coalescing."""
    buf = ""
    out: list[str] = []
    for p in parts:
        buf += p
        buf, emitted = _take_whitespace_delimited_prefixes(buf)
        out.extend(emitted)
        buf, forced = _flush_oversized_tail(buf, _MAX_COALESCE_BUFFER)
        out.extend(forced)
    return buf, out


def test_take_prefixes_single_word_with_trailing_space() -> None:
    rest, emitted = _take_whitespace_delimited_prefixes("Куликов ")
    assert rest == ""
    assert emitted == ["Куликов "]


def test_take_prefixes_incremental_kulikov() -> None:
    tail, emitted = _feed_tokens(["К", "ули", "ков", " "])
    assert tail == ""
    assert emitted == ["Куликов "]


def test_take_prefixes_multiple_words_one_buffer() -> None:
    rest, emitted = _take_whitespace_delimited_prefixes("a b c ")
    assert rest == ""
    assert emitted == ["a ", "b ", "c "]


def test_take_prefixes_tail_without_whitespace_stays() -> None:
    rest, emitted = _take_whitespace_delimited_prefixes("Куликов")
    assert rest == "Куликов"
    assert emitted == []


def test_take_prefixes_leading_spaces_then_word() -> None:
    rest, emitted = _take_whitespace_delimited_prefixes("  Дмитрий ")
    assert rest == ""
    assert emitted == ["  ", "Дмитрий "]


def test_incremental_flushes_tail_on_done_semantics() -> None:
    tail, emitted = _feed_tokens(["часть"])
    assert tail == "часть"
    assert emitted == []


def test_flush_oversized_tail_no_whitespace() -> None:
    long = "x" * (_MAX_COALESCE_BUFFER + 1)
    rest, forced = _flush_oversized_tail(long, _MAX_COALESCE_BUFFER)
    assert rest == ""
    assert forced == [long]


def test_flush_oversized_tail_under_limit_unchanged() -> None:
    rest, forced = _flush_oversized_tail("word", _MAX_COALESCE_BUFFER)
    assert rest == "word"
    assert forced == []


def test_incremental_chunks_crossing_max_without_space() -> None:
    piece = "n" * 2000
    tail, emitted = _feed_tokens([piece, piece, piece])
    assert tail == ""
    assert len(emitted) == 1
    assert len(emitted[0]) == 6000
