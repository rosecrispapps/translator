from __future__ import annotations

import json
from dataclasses import asdict
from typing import Iterable

from .models import TranscriptSegment


SUPPORTED_FORMATS = ("srt", "vtt", "txt", "json")


def format_transcript(segments: Iterable[TranscriptSegment], output_format: str) -> str:
    normalized_format = output_format.lower()
    segment_tuple = tuple(segments)

    if normalized_format == "srt":
        return _format_srt(segment_tuple)
    if normalized_format == "vtt":
        return _format_vtt(segment_tuple)
    if normalized_format == "txt":
        return _format_txt(segment_tuple)
    if normalized_format == "json":
        return _format_json(segment_tuple)

    supported = ", ".join(SUPPORTED_FORMATS)
    raise ValueError(f"Unsupported transcript format '{output_format}'. Use one of: {supported}.")


def format_srt_timestamp(seconds: float) -> str:
    hours, minutes, whole_seconds, milliseconds = _timestamp_parts(seconds)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def format_vtt_timestamp(seconds: float) -> str:
    hours, minutes, whole_seconds, milliseconds = _timestamp_parts(seconds)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def _format_srt(segments: tuple[TranscriptSegment, ...]) -> str:
    blocks = []
    for index, segment in enumerate(segments, start=1):
        blocks.append(
            "\n".join(
                (
                    str(index),
                    f"{format_srt_timestamp(segment.start)} --> {format_srt_timestamp(segment.end)}",
                    segment.text.strip(),
                )
            )
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def _format_vtt(segments: tuple[TranscriptSegment, ...]) -> str:
    blocks = ["WEBVTT"]
    for segment in segments:
        blocks.append(
            "\n".join(
                (
                    f"{format_vtt_timestamp(segment.start)} --> {format_vtt_timestamp(segment.end)}",
                    segment.text.strip(),
                )
            )
        )
    return "\n\n".join(blocks) + "\n"


def _format_txt(segments: tuple[TranscriptSegment, ...]) -> str:
    lines = [
        f"[{format_vtt_timestamp(segment.start).split('.')[0]}] {segment.text.strip()}"
        for segment in segments
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def _format_json(segments: tuple[TranscriptSegment, ...]) -> str:
    payload = {"segments": [asdict(segment) for segment in segments]}
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _timestamp_parts(seconds: float) -> tuple[int, int, int, int]:
    total_milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return hours, minutes, whole_seconds, milliseconds
