from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .formatters import SUPPORTED_FORMATS, format_transcript
from .models import TranscriptResult, TranscriptSegment


class TranscriptAgentError(RuntimeError):
    """Raised when the transcript agent cannot complete a requested run."""


@dataclass(frozen=True)
class AgentConfig:
    model_size: str = "small"
    device: str = "auto"
    compute_type: str = "auto"
    beam_size: int = 5
    vad_filter: bool = True


class MandarinYoutubeTranscriptAgent:
    """Translate spoken Mandarin from a YouTube video into an English transcript."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()

    def translate_youtube(
        self,
        url: str,
        output_path: str | Path,
        output_format: str = "srt",
        keep_audio: bool = False,
    ) -> TranscriptResult:
        if not url.strip():
            raise ValueError("A YouTube URL is required.")

        normalized_format = output_format.lower()
        if normalized_format not in SUPPORTED_FORMATS:
            supported = ", ".join(SUPPORTED_FORMATS)
            raise ValueError(f"Unsupported transcript format '{output_format}'. Use one of: {supported}.")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="mandarin-youtube-transcript-") as temp_dir:
            temp_path = Path(temp_dir)
            audio_path = self._download_audio(url, temp_path)
            result = self.translate_audio(audio_path)

            output.write_text(format_transcript(result.segments, normalized_format), encoding="utf-8")

            if keep_audio:
                audio_output = output.with_suffix(".wav")
                shutil.copyfile(audio_path, audio_output)

            return result

    def translate_audio(self, audio_path: str | Path) -> TranscriptResult:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise TranscriptAgentError(
                "Missing dependency 'faster-whisper'. Install the package with `pip install -e .`."
            ) from exc

        audio = Path(audio_path)
        if not audio.exists():
            raise FileNotFoundError(f"Audio file does not exist: {audio}")

        model = WhisperModel(
            self.config.model_size,
            device=self.config.device,
            compute_type=self.config.compute_type,
        )
        segments, info = model.transcribe(
            str(audio),
            language="zh",
            task="translate",
            beam_size=self.config.beam_size,
            vad_filter=self.config.vad_filter,
        )

        translated_segments = tuple(
            TranscriptSegment(start=segment.start, end=segment.end, text=segment.text.strip())
            for segment in segments
            if segment.text.strip()
        )
        return TranscriptResult(
            segments=translated_segments,
            source_language=getattr(info, "language", None),
            source_language_probability=getattr(info, "language_probability", None),
            duration=getattr(info, "duration", None),
        )

    def _download_audio(self, url: str, output_dir: Path) -> Path:
        try:
            from yt_dlp import YoutubeDL
        except ImportError as exc:
            raise TranscriptAgentError(
                "Missing dependency 'yt-dlp'. Install the package with `pip install -e .`."
            ) from exc

        output_template = output_dir / "source.%(ext)s"
        options = {
            "format": "bestaudio/best",
            "outtmpl": str(output_template),
            "noplaylist": True,
            "quiet": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
        }

        try:
            with YoutubeDL(options) as youtube:
                youtube.extract_info(url, download=True)
        except Exception as exc:  # yt-dlp raises several custom errors depending on the failure.
            raise TranscriptAgentError(f"Could not download YouTube audio: {exc}") from exc

        audio_path = output_dir / "source.wav"
        if not audio_path.exists():
            matches = sorted(output_dir.glob("source.*"))
            if matches:
                audio_path = matches[0]

        if not audio_path.exists():
            raise TranscriptAgentError(
                "YouTube audio download did not produce an audio file. Ensure ffmpeg is installed."
            )

        return audio_path
