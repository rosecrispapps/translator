# Mandarin YouTube Transcript Agent

Translate spoken Mandarin from a YouTube video into an English transcript file.

The package provides:

- A reusable `MandarinYoutubeTranscriptAgent` Python class.
- A `mandarin-youtube-transcript` CLI.
- A local web demo for a one-minute walkthrough.
- SRT, VTT, plain text, and JSON transcript output.

## 60-second demo

Demo mode walks the real pipeline and shows a bundled English transcript. It does not download audio or a Whisper model.

```bash
pip install -e . --no-deps
python -m mandarin_youtube_transcript_agent.web
```

`--no-deps` is enough for the demo. Open http://127.0.0.1:8765. The sample YouTube link is already filled in. Click **Translate** and read the English lines.

The same happy path in the terminal:

```bash
python -m mandarin_youtube_transcript_agent --demo "https://www.youtube.com/watch?v=ZhDemoTai01" \
  --format txt \
  --output transcript.txt \
  --demo-delay 0
```

The recording script, narration, and the live yt-dlp / Whisper command are in [DEMO.md](DEMO.md).

## Requirements

- Python 3.10 or newer
- `ffmpeg` available on your `PATH`
- Network access to YouTube and model downloads

Install the Python package:

```bash
pip install -e .
```

For development and tests:

```bash
pip install -e ".[dev]"
```

## Usage

Create an English SRT transcript from a Mandarin YouTube video:

```bash
mandarin-youtube-transcript "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output transcript.srt
```

Write another format:

```bash
mandarin-youtube-transcript "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format vtt \
  --output transcript.vtt
```

Use a larger Whisper model for better accuracy:

```bash
mandarin-youtube-transcript "https://www.youtube.com/watch?v=VIDEO_ID" \
  --model-size medium \
  --output transcript.srt
```

Keep the extracted audio next to the transcript:

```bash
mandarin-youtube-transcript "https://www.youtube.com/watch?v=VIDEO_ID" \
  --keep-audio \
  --output transcript.srt
```

You can also run it as a module:

```bash
python -m mandarin_youtube_transcript_agent "https://www.youtube.com/watch?v=VIDEO_ID"
```

## How it works

1. Downloads the video's best available audio stream with `yt-dlp`.
2. Converts the audio to WAV through `ffmpeg`.
3. Runs `faster-whisper` with `language="zh"` and `task="translate"`.
4. Writes the translated English segments to the requested transcript format.

Make sure your use follows YouTube's terms and any applicable content rights.
