import json
import os
import subprocess
import sys


def run_cli(args, env=None):
    cmd = [sys.executable, "-m", "core.cli"] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def extract_json(stdout: str):
    start = stdout.find("{")
    depth = 0
    in_str = False
    esc = False
    for i, ch in enumerate(stdout[start:], start=start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(stdout[start : i + 1])
    raise AssertionError("JSON block not found")


def test_cli_preflight_report_fields(monkeypatch):
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    r = run_cli(["--preflight", "Goal"], env=env)
    assert r.returncode == 0
    data = extract_json(r.stdout)
    assert data.get("preflight") is True
    assert "stealth_script_count" in data
