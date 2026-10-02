# 60-second POC demo

Screen recording of the happy path: paste a YouTube link, watch the pipeline, read an English transcript.

Demo mode is what you record. It uses a bundled sample so the take does not download a Whisper model or call YouTube. The live command is the same product with yt-dlp, ffmpeg, and faster-whisper. That path is documented below and is not part of the one-minute take.

## Before you hit record

From the repo root:

```bash
pip install -e . --no-deps
python -m mandarin_youtube_transcript_agent.web
```

`--no-deps` skips yt-dlp and faster-whisper. Demo mode does not import them. Leave that terminal running. It prints:

```text
Demo ready at http://127.0.0.1:8765
```

Open that URL in a desktop browser. Use a window about 1280×720 so the steps and the transcript sit side by side. The sample link is already in the field:

```text
https://www.youtube.com/watch?v=ZhDemoTai01
```

Do one rehearsal click so you know the steps take about six seconds. Reload the page before the real take so the transcript panel is empty again.

## What the viewer should see

1. The page title **English transcript**, the red **Demo mode** chip, and the filled-in YouTube URL.
2. A click on **Translate**.
3. The left column ticking through: check the link, yt-dlp, ffmpeg, Whisper, write the transcript.
4. Timed English lines on the right, starting with “Good morning. I am at a breakfast stall near Yongkang Street.”
5. Hold on that transcript until you stop the recording.

## Narration

Speak at a normal pace. The pipeline animation covers the middle of the take. You do not need to wait for each step before saying the next clause.

| Time | Do this | Say this |
| --- | --- | --- |
| 0:00–0:08 | Show the full page. Leave the sample URL in the field. | This turns a Mandarin YouTube video into an English transcript. |
| 0:08–0:14 | Click the URL field so the link is obvious. | I paste a YouTube link. Watch links, Shorts, and youtu.be all work. |
| 0:14–0:18 | Click **Translate**. | Translate. |
| 0:18–0:28 | Watch the five steps. The English lines show up when the last step finishes, about six seconds after the click. | It checks the link, downloads the audio with yt-dlp, converts it with ffmpeg, and Whisper translates the Mandarin into English. |
| 0:28–0:42 | Point at the lines and the demo note under the title. | This take is demo mode, so you are seeing a bundled sample. The live command runs yt-dlp and faster-whisper on the real audio. |
| 0:42–1:00 | Read the first line, then point at its timestamp. | The first line is: Good morning. I am at a breakfast stall near Yongkang Street. Every line has a timestamp, same as an SRT file. Link in, English out. |

About 130 spoken words. The step animation covers the middle, so the take lands near one minute.

## Terminal version

Use this if you would rather record a terminal than the browser. `--demo-delay` keeps each stage on screen. Drop it to `0` when you only want the transcript.

```bash
python -m mandarin_youtube_transcript_agent --demo "https://www.youtube.com/watch?v=ZhDemoTai01" \
  --format txt \
  --output transcript.txt
```

You should see the progress lines, then eight English lines, then `Wrote 8 translated segment(s) to transcript.txt`.

## How the real path works

Omit `--demo`. The CLI downloads the video’s audio and writes a real transcript. The web page does not have a live switch, so a recording cannot start a model download by accident.

```bash
pip install -e .
python -m mandarin_youtube_transcript_agent "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format txt \
  --output transcript.txt
```

What that command actually runs:

1. **yt-dlp** downloads the best audio stream for that single video (`noplaylist` is on).
2. **ffmpeg** converts it to a WAV file. `ffmpeg` has to be on your `PATH`.
3. **faster-whisper** loads the model (`--model-size`, default `small`) and transcribes with `language="zh"` and `task="translate"`, which is Whisper’s Mandarin-to-English translation task.
4. The CLI writes SRT, VTT, plain text, or JSON, and prints how many segments it wrote.

The first live run needs network access to YouTube and to download the Whisper model. Later runs reuse the cached model. That download is large and slow, so CI and this POC video stay on demo mode.

Formats and the other flags (`--model-size`, `--keep-audio`, `--device`) are in the README.

## Sample used in demo mode

The bundled transcript is original demo copy, not the output of a real video. Its id is `ZhDemoTai01`, title “Taipei breakfast stall”, source language `zh`, about 47 seconds, eight English lines.

Any other valid YouTube URL still completes the happy path. The page then says the lines are the bundled sample, not that video’s audio. Use the prefilled link in the recording so the id, title, and lines match.
