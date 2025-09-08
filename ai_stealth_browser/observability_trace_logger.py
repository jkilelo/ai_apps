"""Run trace logger utility.

Provides append-only JSONL logging for actions, to be invoked by agents or hooks.
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

TRACE_DIR = Path(".trace")
TRACE_DIR.mkdir(exist_ok=True)
TRACE_FILE = TRACE_DIR / "runs.jsonl"


def log_event(event_type: str, payload: Dict[str, Any]) -> None:
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        **payload,
    }
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    # Example manual test
    log_event("example", {"message": "trace logger ready"})
    print("Wrote example trace line ->", TRACE_FILE)
