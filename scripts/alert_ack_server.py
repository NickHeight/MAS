#!/usr/bin/env python3
"""Tiny local ACK webhook for MAS wake-up alerts.

Use behind a temporary tunnel or Twilio Messaging webhook when you want SMS
replies like "ACK <incident_id>" to stop repeated calls.
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

MAS_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ACK_STATE = MAS_ROOT / ".mas" / "alerts" / "acks.json"
ACK_WORDS = {"ACK", "DONE", "STOP"}


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mark_ack(path: Path, incident_id: str, source: str, note: str = "") -> None:
    from datetime import datetime, timezone

    state = read_state(path)
    incidents = state.setdefault("incidents", {})
    incidents[incident_id] = {
        "acked_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "note": note,
    }
    write_state(path, state)


def parse_ack(body: str, fallback_incident_id: str | None = None) -> tuple[str | None, str]:
    cleaned = " ".join(body.strip().split())
    if not cleaned:
        return None, "empty body"
    parts = cleaned.split(" ", 1)
    verb = parts[0].upper()
    if verb not in ACK_WORDS:
        return None, f"ignored non-ACK body: {cleaned}"
    if len(parts) > 1 and parts[1].strip():
        return parts[1].strip(), cleaned
    if fallback_incident_id:
        return fallback_incident_id, cleaned
    return None, "ACK missing incident id"


class AckHandler(BaseHTTPRequestHandler):
    state_file: Path = DEFAULT_ACK_STATE
    default_incident_id: str | None = None

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/ack":
            self._send(404, {"ok": False, "error": "not found"})
            return
        query = urllib.parse.parse_qs(parsed.query)
        incident_id = (query.get("incident_id") or query.get("id") or [None])[0]
        if not incident_id:
            self._send(400, {"ok": False, "error": "incident_id required"})
            return
        mark_ack(self.state_file, incident_id, "http-get", "GET /ack")
        self._send(200, {"ok": True, "incident_id": incident_id})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        content_type = self.headers.get("Content-Type", "")

        if "application/json" in content_type:
            try:
                data = json.loads(raw or "{}")
            except json.JSONDecodeError:
                self._send(400, {"ok": False, "error": "invalid json"})
                return
            body = str(data.get("Body") or data.get("body") or data.get("text") or "")
            source = str(data.get("From") or data.get("source") or "http-json")
        else:
            data = urllib.parse.parse_qs(raw)
            body = (data.get("Body") or data.get("body") or data.get("text") or [""])[0]
            source = (data.get("From") or data.get("source") or ["http-form"])[0]

        incident_id, note = parse_ack(body, self.default_incident_id)
        if not incident_id:
            self._send(202, {"ok": False, "ignored": note})
            return
        mark_ack(self.state_file, incident_id, source, note)
        self._send(200, {"ok": True, "incident_id": incident_id})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        print(f"{self.address_string()} - {format % args}")


def main() -> int:
    parser = argparse.ArgumentParser(description="MAS alert ACK webhook")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--state-file", default=str(DEFAULT_ACK_STATE))
    parser.add_argument("--default-incident-id", default=None)
    args = parser.parse_args()

    AckHandler.state_file = Path(args.state_file)
    AckHandler.default_incident_id = args.default_incident_id
    server = ThreadingHTTPServer((args.host, args.port), AckHandler)
    print(f"ACK server listening on http://{args.host}:{args.port}/ack")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
