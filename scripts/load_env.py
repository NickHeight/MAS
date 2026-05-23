"""Load MAS workspace .env into os.environ (does not override existing vars)."""

from __future__ import annotations

import os
from pathlib import Path

MAS_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = MAS_ROOT / ".env"


def load_mas_env() -> None:
    if not ENV_FILE.is_file():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_mas_env()
