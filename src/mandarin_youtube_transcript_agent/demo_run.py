"""Demo happy path: same stages as the live CLI, with a bundled English transcript.

Live transcription stays in ``MandarinYoutubeTranscriptAgent`` (yt-dlp, ffmpeg,
faster-whisper). Demo mode never imports those libraries and never downloads a model.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from pathlib import Path

from .models import TranscriptSegment
from .youtube_url import YoutubeVideo, parse_youtube_url

DATA_DIR = Path(__file__).resolve().parent / "data"
SAMPLE_PATH = DATA_DIR / "demo_transcript.json"

DEMO_NOTICE = (
    "Demo mode: bundled sample. The live command runs yt-dlp, ffmpeg, and faster-whisper on the real audio."
)
MISMATCH_NOTICE = (
    "Link accepted. These lines are the bundled sample, not this video. Drop --demo to transcribe the real audio."
)

# Pauses long enough that a screen recording can show each stage, short enough for a 60s take.
DEFAULT_DEMO_DELAY_S = 1.6


def sample_url() -> str:
    sample = load_sample()
    return f"https://www.youtube.com/watch?v={sample['video_id']}"


def load_sample() -> dict:
    payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    video_id = payload["video_id"]
    if len(video_id) != 11:
        raise ValueError("Sample video id must be 11 characters.")
    segments = payload["segments"]
    if not segments:
        raise ValueError("Sample transcript has no segments.")
    for segment in segments:
        text = str(segment["text"]).strip()
        start = float(segment["start"])
        end = float(segment["end"])
        if not text or end <= start:
            raise ValueError("Sample segment is missing text or a valid time range.")
    return payload


def iter_demo_events(url: str, delay_s: float = 0.0) -> Iterator[dict]:
    """Yield progress events, then the English transcript, for a YouTube URL."""

    delay_s = _checked_delay(delay_s)
    video = parse_youtube_url(url)
    sample = load_sample()

    yield _event(
        "validate",
        "done",
        f"Accepted video {video.video_id}",
        video_id=video.video_id,
    )

    timed_stages = (
        ("download", "Downloading audio with yt-dlp", "Audio ready", delay_s),
        ("convert", "Converting audio to WAV with ffmpeg", "WAV ready", delay_s),
        (
            "translate",
            "Translating Mandarin speech to English with Whisper",
            "English text ready",
            delay_s * 1.4,
        ),
    )
    for stage, running_message, done_message, pause in timed_stages:
        yield _event(stage, "running", running_message, video_id=video.video_id)
        _pause(pause)
        yield _event(stage, "done", done_message, video_id=video.video_id)

    yield _event(
        "write",
        "done",
        "English transcript ready",
        video_id=video.video_id,
        result=_demo_result(video, sample),
    )


def demo_segments(result: dict) -> tuple[TranscriptSegment, ...]:
    return tuple(
        TranscriptSegment(start=segment["start"], end=segment["end"], text=segment["text"])
        for segment in result["segments"]
    )


def _demo_result(video: YoutubeVideo, sample: dict) -> dict:
    matched = video.video_id == sample["video_id"]
    return {
        "mode": "demo",
        "sample": True,
        "video_id": video.video_id,
        "title": sample["title"] if matched else "Bundled sample transcript",
        "source_language": sample["source_language"],
        "source_language_probability": sample["source_language_probability"],
        "duration": sample["duration"],
        "notice": DEMO_NOTICE if matched else MISMATCH_NOTICE,
        "segments": [
            {
                "start": float(segment["start"]),
                "end": float(segment["end"]),
                "text": str(segment["text"]).strip(),
            }
            for segment in sample["segments"]
        ],
    }


def _event(stage: str, status: str, message: str, **extra: object) -> dict:
    return {"stage": stage, "status": status, "message": message, **extra}


def _checked_delay(delay_s: float) -> float:
    delay = float(delay_s)
    if delay < 0 or delay > 5:
        raise ValueError("delay_s must be between 0 and 5 seconds.")
    return delay


def _pause(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)
