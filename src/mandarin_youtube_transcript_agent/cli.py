from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import AgentConfig, MandarinYoutubeTranscriptAgent, TranscriptAgentError
from .demo_run import DEFAULT_DEMO_DELAY_S, demo_segments, iter_demo_events
from .formatters import SUPPORTED_FORMATS, format_transcript


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
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Show the happy path with a bundled English sample. Does not download audio or run Whisper.",
    )
    parser.add_argument(
        "--demo-delay",
        type=float,
        default=DEFAULT_DEMO_DELAY_S,
        help="Seconds between demo progress lines. Use 0 in tests. Ignored without --demo.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output = args.output or Path(f"transcript.{args.format}")
    if args.demo:
        return _run_demo(args.url, output, args.format, args.demo_delay)

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


def _run_demo(url: str, output: Path, output_format: str, delay_s: float) -> int:
    result_payload = None
    try:
        events = iter_demo_events(url, delay_s=delay_s)
        first = next(events)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("Demo mode — bundled sample transcript (no download, no Whisper)", flush=True)
    print(first["message"], flush=True)
    try:
        for event in events:
            if event["status"] == "running":
                print(event["message"], flush=True)
            if event["stage"] == "write" and event["status"] == "done":
                print(event["message"], flush=True)
                result_payload = event["result"]
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if result_payload is None:
        print("error: demo run did not produce a transcript", file=sys.stderr)
        return 1

    segments = demo_segments(result_payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = format_transcript(segments, output_format)
    output.write_text(rendered, encoding="utf-8")

    print(file=sys.stdout)
    print(
        f"English transcript · source {result_payload['source_language']} · "
        f"{len(segments)} lines · video {result_payload['video_id']}",
        flush=True,
    )
    print(result_payload["notice"], flush=True)
    print(rendered, end="" if rendered.endswith("\n") else "\n", flush=True)
    print(f"Wrote {len(segments)} translated segment(s) to {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
