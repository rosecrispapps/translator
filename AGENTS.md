# translator

## Cursor Cloud specific instructions

This repository is the **Mandarin YouTube Transcript Agent**: a Python 3.10+ CLI/library
that downloads a YouTube video's audio (`yt-dlp` + `ffmpeg`), transcribes the Mandarin
speech and translates it to English with `faster-whisper`, and writes the transcript as
SRT / VTT / TXT / JSON.

> The implementation currently lives on PR #1 (branch
> `cursor/mandarin-youtube-transcript-agent-6a45`); `main` only contains this file and a
> README stub. The commands below assume that code is present (work on the PR branch, or
> they apply to `main` once the PR merges).

### Environment
- Python 3.12 and `ffmpeg` are preinstalled in the image; no system packages are needed.
- The startup update script installs the project into a virtualenv at `/workspace/.venv`
  (only when a `pyproject.toml` exists). Activate it before running anything:
  `source /workspace/.venv/bin/activate` (or call `/workspace/.venv/bin/python`).
  After changing dependencies, reinstall with `pip install -e ".[dev]"`.

### Lint / test / run
- Tests: `pytest` (unit tests cover transcript formatting only; no network required).
- Run the CLI: `mandarin-youtube-transcript "<youtube-url>" -o transcript.srt`
  (equivalently `python -m mandarin_youtube_transcript_agent ...`). See the README on the
  implementation branch for all flags.
- No linter is configured (no ruff/flake8/mypy/black config in the repo).

### Non-obvious gotchas
- **YouTube downloads are blocked from this VM's datacenter IP.** `yt-dlp` returns
  "Sign in to confirm you're not a bot". A real end-to-end run needs an authenticated
  YouTube session: log into YouTube in the Desktop Chrome, then download with
  `yt-dlp --cookies-from-browser chrome ...`. The application's hardcoded `yt_dlp`
  options do not pass cookies, so the unmodified CLI cannot fetch bot-gated videos. To
  exercise the core translation without YouTube, call
  `MandarinYoutubeTranscriptAgent.translate_audio(<audio_path>)` directly on a local
  audio file.
- `deno` (a JS runtime that `yt-dlp` uses to solve YouTube challenges) is installed at
  `~/.deno/bin`. Add it to PATH (`export PATH="$HOME/.deno/bin:$PATH"`) and pass
  `--js-runtimes deno` to `yt-dlp`.
- **Short clips can return 0 segments with the default VAD filter.** If a transcript
  comes back empty, disable it: CLI `--no-vad`, or `AgentConfig(vad_filter=False)`
  (the library default is `vad_filter=True`).
- `faster-whisper` downloads the Whisper model on first use (needs network to Hugging
  Face). CPU-only works fine with `--device cpu --compute-type int8`.
