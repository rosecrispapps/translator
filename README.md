# Mandarin YouTube Transcript Agent

Translate spoken Mandarin from a YouTube video into an English transcript file.

The package provides:

- A reusable `MandarinYoutubeTranscriptAgent` Python class.
- A `mandarin-youtube-transcript` CLI.
- SRT, VTT, plain text, and JSON transcript output.

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
