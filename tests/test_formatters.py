import json

import pytest

from mandarin_youtube_transcript_agent.formatters import (
    format_srt_timestamp,
    format_transcript,
    format_vtt_timestamp,
)
from mandarin_youtube_transcript_agent.models import TranscriptSegment


def test_srt_timestamp_rounds_across_second_boundary() -> None:
    assert format_srt_timestamp(59.9996) == "00:01:00,000"


def test_vtt_timestamp_clamps_negative_values() -> None:
    assert format_vtt_timestamp(-1.5) == "00:00:00.000"


def test_formats_srt_segments() -> None:
    segments = (
        TranscriptSegment(start=0, end=1.2, text="Hello."),
        TranscriptSegment(start=1.2, end=2.4, text="Welcome back."),
    )

    assert format_transcript(segments, "srt") == (
        "1\n"
        "00:00:00,000 --> 00:00:01,200\n"
        "Hello.\n\n"
        "2\n"
        "00:00:01,200 --> 00:00:02,400\n"
        "Welcome back.\n"
    )


def test_formats_vtt_segments() -> None:
    segments = (TranscriptSegment(start=0, end=1.2, text="Hello."),)

    assert format_transcript(segments, "vtt") == (
        "WEBVTT\n\n"
        "00:00:00.000 --> 00:00:01.200\n"
        "Hello.\n"
    )


def test_formats_json_segments() -> None:
    segments = (TranscriptSegment(start=0, end=1.2, text="Hello."),)

    assert json.loads(format_transcript(segments, "json")) == {
        "segments": [{"start": 0, "end": 1.2, "text": "Hello."}]
    }


def test_rejects_unsupported_format() -> None:
    with pytest.raises(ValueError, match="Unsupported transcript format"):
        format_transcript([], "docx")
