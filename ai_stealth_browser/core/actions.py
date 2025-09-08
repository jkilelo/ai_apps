"""Action grammar & parsing for navigation/extraction steps.

Defines a very small DSL mapping each non-empty trimmed line to an Action.
Supported forms:
  NAV <url>
  CLICK <css>
  TYPE <css> => <text>
  WAIT <ms>
  EXTRACT <css>

Unknown lines raise ValueError. Comments start with '#'.

This is intentionally minimal; expansion (JS, conditional, loops) belongs to
future tasks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union


@dataclass
class Action:
    raw: str


@dataclass
class Nav(Action):
    url: str


@dataclass
class Click(Action):
    selector: str


@dataclass
class Type(Action):
    selector: str
    text: str


@dataclass
class Wait(Action):
    ms: int


@dataclass
class Extract(Action):
    selector: str


ActionT = Union[Nav, Click, Type, Wait, Extract]


def parse_actions(script: str) -> List[ActionT]:
    actions: List[ActionT] = []
    for line in script.splitlines():
        raw = line.rstrip("\n")
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if not parts:
            continue
        op = parts[0].upper()
        rest = parts[1] if len(parts) > 1 else ""
        if op == "NAV":
            actions.append(Nav(raw=raw, url=rest.strip()))
        elif op == "CLICK":
            actions.append(Click(raw=raw, selector=rest.strip()))
        elif op == "TYPE":
            if "=>" not in rest:
                raise ValueError(f"TYPE action missing '=>': {raw}")
            sel, txt = rest.split("=>", 1)
            actions.append(Type(raw=raw, selector=sel.strip(), text=txt.strip()))
        elif op == "WAIT":
            ms = int(rest.strip()) if rest.strip().isdigit() else 0
            actions.append(Wait(raw=raw, ms=ms))
        elif op == "EXTRACT":
            actions.append(Extract(raw=raw, selector=rest.strip()))
        else:
            raise ValueError(f"Unknown action: {raw}")
    return actions


__all__ = ["Action", "Nav", "Click", "Type", "Wait", "Extract", "parse_actions"]
