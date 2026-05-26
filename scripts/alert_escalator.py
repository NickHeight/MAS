#!/usr/bin/env python3
"""MAS local wake-up escalation CLI.

Sends project-aware alerts through Slack, Twilio SMS, and Twilio Voice without
storing secrets in the repository. Designed to be called by MAS loops, hooks,
or future Katya workflows when a true human gate appears.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

MAS_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROFILES_PATH = MAS_ROOT / "config" / "alert_profiles.example.json"
DEFAULT_ACK_STATE = MAS_ROOT / ".mas" / "alerts" / "acks.json"


class AlertError(RuntimeError):
    """Raised when an alert channel fails."""


@dataclass(frozen=True)
class CallPolicy:
    enabled: bool
    max_attempts: int
    interval_seconds: int
    timeout_seconds: int


@dataclass(frozen=True)
class AlertProfile:
    name: str
    description: str
    channels: list[str]
    call_policy: CallPolicy
    ack_keywords: list[str]
    state_file: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_profiles(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AlertError(f"profile file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_profile(name: str, profile_path: Path) -> AlertProfile:
    data = load_profiles(profile_path)
    raw = data.get("profiles", {}).get(name)
    if not raw:
        choices = ", ".join(sorted(data.get("profiles", {}).keys()))
        raise AlertError(f"unknown profile {name!r}; available: {choices}")

    call = raw.get("call", {})
    ack = raw.get("ack", {})
    raw_state_file = Path(ack.get("state_file") or DEFAULT_ACK_STATE)
    state_file = raw_state_file if raw_state_file.is_absolute() else MAS_ROOT / raw_state_file

    return AlertProfile(
        name=name,
        description=raw.get("description", ""),
        channels=list(raw.get("channels", [])),
        call_policy=CallPolicy(
            enabled=bool(call.get("enabled", False)),
            max_attempts=max(0, int(call.get("max_attempts", 0))),
            interval_seconds=max(0, int(call.get("interval_seconds", 0))),
            timeout_seconds=max(1, int(call.get("timeout_seconds", 25))),
        ),
        ack_keywords=[kw.upper() for kw in ack.get("keywords", ["ACK", "DONE", "STOP"])],
        state_file=state_file,
    )


def read_ack_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_ack_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_acknowledged(path: Path, incident_id: str) -> bool:
    state = read_ack_state(path)
    incident = state.get("incidents", {}).get(incident_id)
    return bool(incident and incident.get("acked_at"))


def mark_ack(path: Path, incident_id: str, source: str, note: str = "") -> None:
    state = read_ack_state(path)
    incidents = state.setdefault("incidents", {})
    incidents[incident_id] = {
        "acked_at": utc_now(),
        "source": source,
        "note": note,
    }
    write_ack_state(path, state)


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise AlertError(f"required env var missing: {name}")
    return value


def http_post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        text = response.read().decode("utf-8")
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {"raw": text}


def http_post_form(
    url: str,
    form: dict[str, str],
    *,
    username: str,
    password: str,
    timeout: int = 20,
) -> dict[str, Any]:
    body = urllib.parse.urlencode(form).encode("utf-8")
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        text = response.read().decode("utf-8")
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {"raw": text}


def build_message(args: argparse.Namespace, profile: AlertProfile) -> str:
    parts = [
        f"[{args.severity.upper()}] {args.title}",
        f"Project: {args.project}",
        f"Profile: {profile.name}",
    ]
    if args.agent:
        parts.append(f"Agent: {args.agent}")
    if args.incident_id:
        parts.append(f"Incident: {args.incident_id}")
    parts.append("")
    parts.append(args.body)
    parts.append("")
    parts.append(f"Reply/mark ACK with: python scripts/alert_escalator.py ack {args.incident_id}")
    return "\n".join(parts)


def send_slack(message: str, dry_run: bool) -> None:
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL")

    if dry_run:
        print("[dry-run] Slack alert would be sent")
        return
    if webhook:
        http_post_json(webhook, {"text": message})
        print("sent Slack webhook alert")
        return
    if bot_token and channel:
        result = http_post_json(
            "https://slack.com/api/chat.postMessage",
            {"channel": channel, "text": message},
            headers={"Authorization": f"Bearer {bot_token}"},
        )
        if not result.get("ok"):
            raise AlertError(f"Slack API rejected message: {result}")
        print("sent Slack bot alert")
        return
    raise AlertError("Slack requested but SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN+SLACK_CHANNEL is missing")


def twilio_auth() -> tuple[str, str]:
    return env_required("TWILIO_ACCOUNT_SID"), env_required("TWILIO_AUTH_TOKEN")


def send_sms(message: str, dry_run: bool) -> None:
    if dry_run:
        print("[dry-run] SMS would be sent to ALERT_NICK_PHONE from TWILIO_FROM_NUMBER")
        return

    to_number = env_required("ALERT_NICK_PHONE")
    from_number = env_required("TWILIO_FROM_NUMBER")
    sid, token = twilio_auth()

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    result = http_post_form(
        url,
        {"From": from_number, "To": to_number, "Body": message[:1500]},
        username=sid,
        password=token,
    )
    print(f"sent SMS alert sid={result.get('sid', 'unknown')}")


def call_twiml(title: str, body: str, incident_id: str) -> str:
    spoken = (
        f"MAS alert. {title}. Incident {incident_id}. "
        f"{body[:350]} "
        "Wake up and acknowledge the alert."
    )
    return f"<Response><Say voice=\"alice\">{escape(spoken)}</Say><Pause length=\"2\"/><Say voice=\"alice\">Repeating. {escape(spoken)}</Say></Response>"


def place_call(args: argparse.Namespace, dry_run: bool) -> None:
    if dry_run:
        print("[dry-run] Voice call would be placed to ALERT_NICK_PHONE from TWILIO_FROM_NUMBER")
        return

    to_number = env_required("ALERT_NICK_PHONE")
    from_number = env_required("TWILIO_FROM_NUMBER")
    sid, token = twilio_auth()

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json"
    result = http_post_form(
        url,
        {
            "From": from_number,
            "To": to_number,
            "Twiml": call_twiml(args.title, args.body, args.incident_id),
            "Timeout": str(args.call_timeout_seconds),
        },
        username=sid,
        password=token,
    )
    print(f"placed voice call sid={result.get('sid', 'unknown')}")


def trigger(args: argparse.Namespace) -> int:
    profile = resolve_profile(args.profile, Path(args.profiles))
    if args.incident_id is None:
        args.incident_id = f"{args.project}-{int(time.time())}"
    args.call_timeout_seconds = profile.call_policy.timeout_seconds

    message = build_message(args, profile)
    print(f"triggering alert incident={args.incident_id} profile={profile.name} dry_run={args.dry_run}")

    channel_errors: list[str] = []
    for channel in profile.channels:
        try:
            if channel == "slack":
                send_slack(message, args.dry_run)
            elif channel == "sms":
                send_sms(message, args.dry_run)
            elif channel == "voice":
                # Voice is handled below because it can repeat until ACK.
                continue
            elif channel == "email":
                print("email channel configured but not implemented in local v1; skipping")
            else:
                raise AlertError(f"unknown channel {channel!r}")
        except (AlertError, urllib.error.URLError, TimeoutError) as exc:
            channel_errors.append(f"{channel}: {exc}")
            print(f"ERROR {channel}: {exc}", file=sys.stderr)

    if "voice" in profile.channels and profile.call_policy.enabled:
        for attempt in range(1, profile.call_policy.max_attempts + 1):
            if is_acknowledged(profile.state_file, args.incident_id):
                print(f"incident acknowledged before call attempt {attempt}; stopping voice loop")
                break
            print(f"voice attempt {attempt}/{profile.call_policy.max_attempts}")
            try:
                place_call(args, args.dry_run)
            except (AlertError, urllib.error.URLError, TimeoutError) as exc:
                channel_errors.append(f"voice attempt {attempt}: {exc}")
                print(f"ERROR voice attempt {attempt}: {exc}", file=sys.stderr)
            if attempt < profile.call_policy.max_attempts and not args.dry_run:
                time.sleep(profile.call_policy.interval_seconds)

    if channel_errors:
        print("completed with channel errors:")
        for error in channel_errors:
            print(f"- {error}")
        return 2
    return 0


def ack(args: argparse.Namespace) -> int:
    profile = resolve_profile(args.profile, Path(args.profiles))
    mark_ack(profile.state_file, args.incident_id, args.source, args.note)
    print(f"acknowledged incident={args.incident_id} state_file={profile.state_file}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MAS wake-up alert escalation")
    parser.add_argument("--profiles", default=str(DEFAULT_PROFILES_PATH), help="Path to alert profiles JSON")
    parser.add_argument("--profile", default="mas-default", help="Profile name from alert profiles JSON")

    sub = parser.add_subparsers(dest="command", required=True)

    trigger_parser = sub.add_parser("trigger", help="Send an alert through the selected profile")
    trigger_parser.add_argument("--project", required=True, help="Project or client slug")
    trigger_parser.add_argument("--severity", default="p0", help="Severity label, e.g. p0/p1/info")
    trigger_parser.add_argument("--title", required=True, help="Short alert title")
    trigger_parser.add_argument("--body", required=True, help="Alert detail")
    trigger_parser.add_argument("--agent", default="", help="Agent/session name")
    trigger_parser.add_argument("--incident-id", default=None, help="Stable incident id for ACK tracking")
    trigger_parser.add_argument("--dry-run", action="store_true", help="Print intended actions without sending")
    trigger_parser.set_defaults(func=trigger)

    ack_parser = sub.add_parser("ack", help="Mark an incident acknowledged")
    ack_parser.add_argument("incident_id", help="Incident id to acknowledge")
    ack_parser.add_argument("--source", default="manual-cli", help="Where the ACK came from")
    ack_parser.add_argument("--note", default="", help="Optional ACK note")
    ack_parser.set_defaults(func=ack)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except AlertError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
