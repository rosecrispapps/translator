from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptSegment:
    """A translated transcript segment with start and end times in seconds."""

    start: float
    end: float
    text: str


@dataclass(frozen=True)
class TranscriptResult:
    """The translated transcript and useful metadata from the transcription run."""

    segments: tuple[TranscriptSegment, ...]
    source_language: str | None
    source_language_probability: float | None
    duration: float | None
