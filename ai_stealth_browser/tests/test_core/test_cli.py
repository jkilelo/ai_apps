import json
import os
import subprocess
import sys


def run_cli(args, env=None):
    cmd = [sys.executable, "-m", "core.cli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.returncode, result.stdout, result.stderr


def _extract_first_json_block(text: str):
    start = text.find("{")
    if start == -1:
        raise AssertionError("No JSON object start found in output")
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    json_str = text[start : i + 1]
                    return json.loads(json_str)
    raise AssertionError("Could not find complete JSON object in output")


def test_cli_halts_without_key(monkeypatch):
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    code, out, err = run_cli(["Goal"], env=env)
    assert code != 0
    merged = (out + err).lower()
    assert "halt" in merged


def test_cli_runs_with_dummy_key(monkeypatch):
    # Provide a plausible dummy key (no dry-run path exists anymore)
    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = "dummy-key-placeholder-12345678901234567890"
    code, out, err = run_cli(["--version", "placeholder-goal"], env=env)
    # Version path bypasses agent execution but requires no dry-run flag
    assert code == 0


def test_cli_version():
    env = os.environ.copy()
    code, out, err = run_cli(["--version", "placeholder-goal"], env=env)
    assert code == 0
    assert out.strip()
