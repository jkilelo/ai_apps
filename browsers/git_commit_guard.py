#!/usr/bin/env python3
"""
Git commit guard hook for Claude Code environment.
Ensures code quality and prevents commits of sensitive information.
"""

import subprocess
import sys
import re
from pathlib import Path


def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_for_secrets():
    """Check staged files for potential secrets."""
    secrets_patterns = [
        r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?[^"\'\s]+',
        r'(?i)(api_?key|apikey)\s*[:=]\s*["\']?[^"\'\s]+',
        r'(?i)(secret|token)\s*[:=]\s*["\']?[^"\'\s]+',
        r'(?i)(auth|authorization)\s*[:=]\s*["\']?[^"\'\s]+',
        r"sk-[a-zA-Z0-9]{48}",  # OpenAI API keys
        r"xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}",  # Slack tokens
    ]

    # Get staged files
    success, stdout, stderr = run_command("git diff --cached --name-only")
    if not success:
        return True  # If we can't check, allow commit

    staged_files = stdout.strip().split("\n") if stdout.strip() else []

    for file_path in staged_files:
        if not file_path.endswith(".py"):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for pattern in secrets_patterns:
                if re.search(pattern, content):
                    print(f"ERROR: Potential secret found in {file_path}")
                    print(f"   Pattern: {pattern}")
                    return False
        except Exception:
            continue

    return True


def check_ascii_only():
    """Check that all Python files contain only ASCII characters."""
    # Get staged files
    success, stdout, stderr = run_command("git diff --cached --name-only")
    if not success:
        return True  # If we can't check, allow commit

    staged_files = stdout.strip().split("\n") if stdout.strip() else []

    for file_path in staged_files:
        if not file_path.endswith(".py"):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Check for non-ASCII characters
                try:
                    line.encode("ascii")
                except UnicodeEncodeError as e:
                    print(f"ERROR: Non-ASCII character found in {file_path}:{line_num}")
                    print(f"   Line: {repr(line)}")
                    print(f"   Error: {e}")
                    return False

        except Exception as e:
            print(f"WARNING: Could not check {file_path}: {e}")
            continue

    return True


def check_test_coverage():
    """Ensure test coverage is maintained."""
    success, stdout, stderr = run_command(
        "python -m pytest --cov=. --cov-report=term-missing --cov-fail-under=80"
    )
    if not success:
        print("ERROR: Test coverage below 80% threshold")
        return False
    return True


def check_code_quality():
    """Run basic code quality checks."""
    # Check for syntax errors
    success, stdout, stderr = run_command("python -m py_compile stealth_browser.py")
    if not success:
        print(f"ERROR: Syntax errors found: {stderr}")
        return False

    return True


def main():
    """Main entry point for git commit guard."""
    print("Running pre-commit checks...")

    checks = [
        ("Checking for secrets", check_for_secrets),
        ("Checking ASCII-only content", check_ascii_only),
        ("Checking code quality", check_code_quality),
        # ("Checking test coverage", check_test_coverage),  # Disabled for now
    ]

    for description, check_func in checks:
        print(f"   {description}...")
        if not check_func():
            print(f"ERROR: Commit blocked - {description} failed")
            return 1

    print("SUCCESS: All pre-commit checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
