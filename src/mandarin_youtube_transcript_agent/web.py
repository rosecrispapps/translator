"""Local demo server: paste a YouTube URL, watch the pipeline, read English lines."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .demo_run import DATA_DIR, DEFAULT_DEMO_DELAY_S, iter_demo_events, sample_url

INDEX_PATH = DATA_DIR / "index.html"
MAX_BODY_BYTES = 8_192


class DemoServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    demo_delay_s = DEFAULT_DEMO_DELAY_S


class DemoHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server: DemoServer

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/":
            page = INDEX_PATH.read_text(encoding="utf-8").replace("__SAMPLE_URL__", sample_url())
            self._send(200, "text/html; charset=utf-8", page.encode("utf-8"))
            return
        if path == "/health":
            self._send_json(200, {"ok": True, "mode": "demo"})
            return
        if path == "/api/config":
            self._send_json(200, {"mode": "demo", "sample_url": sample_url()})
            return
        self._send_json(404, {"error": "Not found."})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path != "/api/translate":
            self._send_json(404, {"error": "Not found."})
            return

        try:
            body = self._read_json()
            url = str(body.get("url", ""))
            delay_s = body.get("delay_s", self.server.demo_delay_s)
            events = iter_demo_events(url, delay_s=float(delay_s))
            # Validate before streaming so a bad link returns a normal error response.
            first = next(events)
        except (TypeError, ValueError) as exc:
            message = str(exc) if isinstance(exc, ValueError) else "Send a JSON body with a url field."
            self._send_json(400, {"error": message})
            return
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Send a JSON body with a url field."})
            return

        self.close_connection = True
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self._write_event(first)
        for event in events:
            self._write_event(event)
        self._write_chunk(b"")

    def log_message(self, format: str, *args: object) -> None:
        return

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("Request body is too large.")
        raw = self.rfile.read(length) if length else b"{}"
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Send a JSON object with a url field.")
        return payload

    def _write_event(self, event: dict) -> None:
        payload = json.dumps(event, ensure_ascii=False).encode("utf-8") + b"\n"
        self._write_chunk(payload)

    def _write_chunk(self, payload: bytes) -> None:
        try:
            self.wfile.write(f"{len(payload):X}\r\n".encode("ascii"))
            self.wfile.write(payload)
            self.wfile.write(b"\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict) -> None:
        self._send(status, "application/json; charset=utf-8", json.dumps(payload).encode("utf-8"))


def create_server(host: str = "127.0.0.1", port: int = 8765, demo_delay_s: float = DEFAULT_DEMO_DELAY_S) -> DemoServer:
    server = DemoServer((host, port), DemoHandler)
    server.demo_delay_s = demo_delay_s
    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mandarin-youtube-demo",
        description="Serve the local Mandarin YouTube → English transcript demo.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DEMO_DELAY_S,
        help="Seconds to show each pipeline stage. Use 0 for tests.",
    )
    args = parser.parse_args(argv)

    try:
        server = create_server(args.host, args.port, demo_delay_s=args.delay)
    except OSError as exc:
        print(f"error: could not bind {args.host}:{args.port}: {exc}")
        return 1

    host, port = server.server_address[:2]
    print(f"Demo ready at http://{host}:{port}")
    print("Demo mode uses a bundled English sample. Ctrl+C stops the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
