from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

_VIDEO_ID = r"[A-Za-z0-9_-]{11}"


@dataclass(frozen=True)
class YoutubeVideo:
    """A YouTube video identified by its 11-character id."""

    video_id: str
    url: str


def parse_youtube_url(url: str) -> YoutubeVideo:
    """Accept watch, shorts, embed, live, and youtu.be links."""

    raw = url.strip()
    if not raw:
        raise ValueError("Paste a YouTube URL.")

    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Use a YouTube watch, shorts, embed, or youtu.be link.")

    host = parsed.netloc.lower().split("@")[-1].split(":")[0].rstrip(".")
    if not _is_youtube_host(host):
        raise ValueError("Use a YouTube watch, shorts, embed, or youtu.be link.")

    video_id = _video_id_from_parts(host, parsed.path, parsed.query)
    if video_id is None:
        raise ValueError("Use a YouTube watch, shorts, embed, or youtu.be link.")

    return YoutubeVideo(video_id=video_id, url=raw)


def _is_youtube_host(host: str) -> bool:
    if host in {"youtu.be", "youtube.com", "youtube-nocookie.com"}:
        return True
    return (
        host.endswith(".youtu.be")
        or host.endswith(".youtube.com")
        or host.endswith(".youtube-nocookie.com")
    )


def _video_id_from_parts(host: str, path: str, query: str) -> str | None:
    if host == "youtu.be" or host.endswith(".youtu.be"):
        candidate = path.strip("/").split("/", 1)[0]
        return candidate if re.fullmatch(_VIDEO_ID, candidate) else None

    parts = [part for part in path.split("/") if part]
    if parts[:1] == ["watch"]:
        candidate = parse_qs(query).get("v", [None])[0]
    elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live", "v"}:
        candidate = parts[1]
    else:
        candidate = None

    if candidate and re.fullmatch(_VIDEO_ID, candidate):
        return candidate
    return None
