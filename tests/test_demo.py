import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from mandarin_youtube_transcript_agent.agent import MandarinYoutubeTranscriptAgent
from mandarin_youtube_transcript_agent.cli import main
from mandarin_youtube_transcript_agent.demo_run import iter_demo_events, load_sample, sample_url
from mandarin_youtube_transcript_agent.web import create_server
from mandarin_youtube_transcript_agent.youtube_url import parse_youtube_url

SAMPLE_URL = "https://www.youtube.com/watch?v=ZhDemoTai01"


def test_parse_watch_shorts_and_short_link() -> None:
    assert parse_youtube_url(SAMPLE_URL).video_id == "ZhDemoTai01"
    assert parse_youtube_url("https://youtu.be/ZhDemoTai01?t=3").video_id == "ZhDemoTai01"
    assert parse_youtube_url("https://www.youtube.com/shorts/ZhDemoTai01").video_id == "ZhDemoTai01"
    assert parse_youtube_url("https://m.youtube.com/embed/ZhDemoTai01").video_id == "ZhDemoTai01"
    assert parse_youtube_url("youtu.be/ZhDemoTai01").video_id == "ZhDemoTai01"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "hello",
        "https://vimeo.com/12345678901",
        "https://notyoutube.com/watch?v=ZhDemoTai01",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/playlist?list=PL123456789012",
    ],
)
def test_parse_rejects_non_video_links(url: str) -> None:
    with pytest.raises(ValueError):
        parse_youtube_url(url)


def test_demo_events_finish_with_english_sample() -> None:
    events = list(iter_demo_events(SAMPLE_URL, delay_s=0))
    stages = [(event["stage"], event["status"]) for event in events]

    assert stages[0] == ("validate", "done")
    assert ("download", "running") in stages
    assert ("translate", "running") in stages
    assert stages[-1][0] == "write"

    result = events[-1]["result"]
    assert result["sample"] is True
    assert result["source_language"] == "zh"
    assert result["video_id"] == "ZhDemoTai01"
    assert "Yongkang Street" in result["segments"][0]["text"]
    assert "bundled sample" in result["notice"]


def test_other_youtube_url_is_accepted_and_labeled_as_sample() -> None:
    events = list(iter_demo_events("https://youtu.be/abcdefghijk", delay_s=0))
    result = events[-1]["result"]

    assert result["video_id"] == "abcdefghijk"
    assert "not this video" in result["notice"]
    assert result["segments"][-1]["text"].startswith("That is breakfast in Taipei")


def test_demo_delay_is_bounded() -> None:
    with pytest.raises(ValueError, match="delay_s"):
        list(iter_demo_events(SAMPLE_URL, delay_s=9))


def test_sample_file_matches_the_prefilled_url() -> None:
    sample = load_sample()
    assert sample_url() == SAMPLE_URL
    assert sample["title"] == "Taipei breakfast stall"
    assert len(sample["segments"]) == 8


def test_demo_cli_writes_transcript_without_calling_whisper(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fail_live(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("demo mode must not run the live agent")

    monkeypatch.setattr(MandarinYoutubeTranscriptAgent, "translate_youtube", fail_live)
    monkeypatch.setattr(MandarinYoutubeTranscriptAgent, "translate_audio", fail_live)

    output = tmp_path / "transcript.txt"
    code = main(
        [
            "--demo",
            SAMPLE_URL,
            "--format",
            "txt",
            "--output",
            str(output),
            "--demo-delay",
            "0",
        ]
    )

    assert code == 0
    text = output.read_text(encoding="utf-8")
    assert "Good morning. I am at a breakfast stall near Yongkang Street." in text
    assert text.count("\n") == 8


def test_demo_cli_rejects_a_bad_url(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output = tmp_path / "transcript.txt"
    code = main(["--demo", "https://example.com/watch?v=ZhDemoTai01", "-o", str(output), "--demo-delay", "0"])

    assert code == 1
    assert not output.exists()
    assert "YouTube" in capsys.readouterr().err


@pytest.fixture
def demo_server() -> str:
    server = create_server("127.0.0.1", 0, demo_delay_s=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()


def test_demo_page_and_translate_api(demo_server: str) -> None:
    with urlopen(f"{demo_server}/health", timeout=2) as response:
        assert json.load(response)["mode"] == "demo"

    with urlopen(f"{demo_server}/", timeout=2) as response:
        page = response.read().decode("utf-8")
    assert SAMPLE_URL in page
    assert "Translate with Whisper" in page
    assert "__SAMPLE_URL__" not in page

    payload = json.dumps({"url": "https://www.youtube.com/shorts/ZhDemoTai01", "delay_s": 0}).encode()
    request = Request(
        f"{demo_server}/api/translate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=2) as response:
        events = [json.loads(line) for line in response.read().decode("utf-8").splitlines() if line.strip()]

    assert events[0]["message"] == "Accepted video ZhDemoTai01"
    assert any(event["stage"] == "translate" and event["status"] == "running" for event in events)
    assert "soy milk" in events[-1]["result"]["segments"][5]["text"]


def test_translate_api_rejects_a_bad_url(demo_server: str) -> None:
    payload = json.dumps({"url": "https://example.com/video"}).encode()
    request = Request(f"{demo_server}/api/translate", data=payload, method="POST")
    with pytest.raises(HTTPError) as caught:
        urlopen(request, timeout=2)
    assert caught.value.code == 400
    body = json.loads(caught.value.read().decode("utf-8"))
    assert "YouTube" in body["error"]
