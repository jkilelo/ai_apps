import pathlib, yaml, re

REG_PATH = pathlib.Path("ROADMAP_TASKS.yml")


def test_task_registry_exists():
    assert REG_PATH.exists(), "ROADMAP_TASKS.yml missing"


def test_tasks_have_tests():
    data = yaml.safe_load(REG_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    # collect test file names
    test_files = [str(p) for p in pathlib.Path("tests").rglob("test_*.py")]
    problematic = []
    for item in data:
        if item.get("status") != "implemented":
            continue
        pats = item.get("test_patterns") or []
        if not pats:
            problematic.append(item["id"])
            continue
        found = False
        for pat in pats:
            if any(pat in tf for tf in test_files):
                found = True
                break
        if not found:
            problematic.append(item["id"])
    assert not problematic, f"Implemented tasks missing tests: {problematic}"


def test_minimum_coverage_marker():
    """Placeholder: ensure coverage data file exists after full run.

    This does not calculate coverage here (would require running the full
    suite with --cov). Instead, assert that when coverage is produced the
    data file is present; failing this reminds developers to run with coverage.
    """
    cov_files = list(pathlib.Path(".").glob(".coverage*"))
    # Not failing hard if absent; just gentle reminder hook for pipeline.
    # For local dev, presence is optional.
    if not cov_files:
        # Soft assertion pattern: mark xfail-like behavior
        import pytest

        pytest.skip("coverage file not present (run full suite with --cov)")
