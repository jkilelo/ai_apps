"""Structured event logging helpers (JSONL sink)."""

from __future__ import annotations
import json
from pathlib import Path
import os
from datetime import datetime, timezone
from typing import Dict, Any

LOG_PATH = Path("event_traces.jsonl")


def append_event(event_type: str, payload: Dict[str, Any]) -> None:
    record = {
        # Use explicit UTC timezone-aware timestamp (avoid deprecated utcnow)
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": event_type,
        "data": payload,
    }
    # Prefer environment override for testing / redirection
    override = os.getenv("AI_STEALTH_EVENT_LOG")
    path = Path(override) if override else LOG_PATH  # re-read in case monkeypatched
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


__all__ = ["append_event", "LOG_PATH"]
