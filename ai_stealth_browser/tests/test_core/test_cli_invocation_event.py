import json
import os
import subprocess
import sys


def run_cli(args, env=None):
    cmd = [sys.executable, "-m", "core.cli"] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_cli_invocation_event_with_key(tmp_path):
    target = tmp_path / "events.jsonl"
    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = "dummy-key-placeholder-12345678901234567890"
    env["AI_STEALTH_EVENT_LOG"] = str(target)
    r = run_cli(["Goal X"], env=env)
    # Will likely fail if actual Anthropic call attempted without valid key; expect non-zero
    # but event file should still have invocation record before failure.
    assert target.exists(), "events file not created"
    lines = target.read_text(encoding="utf-8").splitlines()
    events = [json.loads(l) for l in lines]
    inv = [e for e in events if e.get("event") == "cli_invocation"]
    assert inv, "cli_invocation event missing"
    payload = inv[-1]["data"]
    assert payload.get("goal") == "Goal X"
