from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import AgentConfig, MandarinYoutubeTranscriptAgent, TranscriptAgentError
from .formatters import SUPPORTED_FORMATS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mandarin-youtube-transcript",
        description="Translate spoken Mandarin in a YouTube video into an English transcript.",
    )
    parser.add_argument("url", help="YouTube video URL.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output transcript path. Defaults to transcript.<format>.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=SUPPORTED_FORMATS,
        default="srt",
        help="Transcript output format.",
    )
    parser.add_argument(
        "--model-size",
        default="small",
        help="faster-whisper model size or local model path.",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="Inference device passed to faster-whisper, such as auto, cpu, or cuda.",
    )
    parser.add_argument(
        "--compute-type",
        default="auto",
        help="Compute type passed to faster-whisper, such as auto, int8, or float16.",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Beam size for Whisper decoding.",
    )
    parser.add_argument(
        "--no-vad",
        action="store_true",
        help="Disable voice activity detection filtering.",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Save the downloaded WAV audio next to the transcript.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output = args.output or Path(f"transcript.{args.format}")
    config = AgentConfig(
        model_size=args.model_size,
        device=args.device,
        compute_type=args.compute_type,
        beam_size=args.beam_size,
        vad_filter=not args.no_vad,
    )
    agent = MandarinYoutubeTranscriptAgent(config)

    try:
        result = agent.translate_youtube(
            url=args.url,
            output_path=output,
            output_format=args.format,
            keep_audio=args.keep_audio,
        )
    except (OSError, TranscriptAgentError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    segment_count = len(result.segments)
    print(f"Wrote {segment_count} translated segment(s) to {output}")
    if result.source_language:
        print(f"Detected source language: {result.source_language}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
