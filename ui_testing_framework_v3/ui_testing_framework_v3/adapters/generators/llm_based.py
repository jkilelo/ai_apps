"""LLM-backed test generator adapter.

Converts formatted element data into a structured prompt and calls the
project's LLM integration (llm.py) to generate concrete TestCase objects.

Design goals:
- No LLM logic in core domain; this remains an adapter plugin.
- Robust parsing: expect JSON output; fall back to simple extraction.
- Safe: failures return an empty list rather than raising.
"""

from __future__ import annotations

import json
from typing import Any, TypedDict, cast

from ui_testing_framework_v3.core.models import TestCase
from ui_testing_framework_v3.ports.test_generator import ITestGenerator

# Optional top-level import; if unavailable, adapter will no-op
llm_mod: Any | None
try:  # pragma: no cover - exercised via unit tests with mocking
    import llm as _llm_import

    llm_mod = cast("Any", _llm_import)
except Exception:  # pragma: no cover - defensive
    llm_mod = None


class _Msg(TypedDict):
    role: str
    content: str


def _build_prompt(formatted: dict[str, Any]) -> list[_Msg]:
    """Build a provider-agnostic chat prompt from formatted data."""
    # Summarize in a string to avoid overly strict typing; good enough for LLM prompt
    try:
        summary_str = json.dumps(formatted.get("counts") or formatted.get("elements") or {})
    except Exception:
        summary_str = str(formatted.get("counts") or formatted.get("elements") or {})
    system = (
        "You are a senior QA engineer. Generate concise, executable UI test cases. "
        'Return ONLY valid JSON: {\n"tests": [ {\n'
        '  "name": str, "description": str, \n'
        '  "steps": [str], "assertions": [str], \n'
        "  \"priority\": one of ['low','medium','high','critical'], \n"
        '  "tags": [str]\n} ] }'
    )
    user = (
        "Formatted element summary (by type):\n" + summary_str + "\n\n"
        "Focus on critical paths (forms, buttons, nav). "
        "At least 1-3 tests. Keep steps/assertions specific."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _parse_tests(payload: str) -> list[TestCase]:
    """Parse JSON content into a list of TestCase objects."""

    def _coerce_case(obj: dict[str, Any]) -> TestCase:
        name = str(obj.get("name", "Unnamed Test"))
        desc = str(obj.get("description", name))
        steps = [str(s) for s in obj.get("steps", [])]
        assertions = [str(a) for a in obj.get("assertions", [])]
        priority = str(obj.get("priority", "medium"))
        tags = [str(t) for t in obj.get("tags", [])]
        return TestCase(
            name=name,
            description=desc,
            steps=steps,
            assertions=assertions,
            priority=priority,
            tags=tags,
        )

    # Try direct JSON
    try:
        data: Any = json.loads(payload)
    except Exception:
        # Try to find the first JSON object/array heuristically
        start_obj = payload.find("{")
        start_arr = payload.find("[")
        start = (
            min(x for x in [start_obj, start_arr] if x != -1)
            if (start_obj != -1 or start_arr != -1)
            else -1
        )
        if start == -1:
            return []
        try:
            data = json.loads(payload[start:])
        except Exception:
            return []

    tests_raw: list[dict[str, Any]] = []
    if isinstance(data, dict):
        data_dict = cast("dict[str, Any]", data)
        tests_val: Any = data_dict.get("tests")
        if isinstance(tests_val, list):
            tests_raw.extend(
                [
                    cast("dict[str, Any]", item)
                    for item in cast("list[Any]", tests_val)
                    if isinstance(item, dict)
                ]
            )
        else:
            return []
    elif isinstance(data, list):
        tests_raw.extend(
            [
                cast("dict[str, Any]", item)
                for item in cast("list[Any]", data)
                if isinstance(item, dict)
            ]
        )
    else:
        return []

    return [_coerce_case(t) for t in tests_raw]


class LLMTestGenerator(ITestGenerator):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    async def generate(self, formatted_data: dict[str, Any]) -> list[TestCase]:
        try:
            messages = _build_prompt(formatted_data)

            if llm_mod is None:
                return []

            provider_any = self._config.get("provider")
            model_any = self._config.get("model")
            provider = provider_any if isinstance(provider_any, str) else None
            model = model_any if isinstance(model_any, str) else None

            llm = llm_mod  # already Any-typed
            msg_models = [
                llm.Message(role=cast("Any", m["role"]), content=m["content"]) for m in messages
            ]
            resp = (
                llm.call_default_llm(messages=msg_models, provider=provider, model=model)
                if (provider or model)
                else llm.call_default_llm(messages=msg_models)
            )

            content = getattr(resp, "content", "")
            tests = _parse_tests(content)
            return [t for t in tests if t.validate()]
        except Exception:
            return []

    def get_supported_types(self) -> list[str]:
        return ["llm", "llm-test"]


def register(registry: Any) -> None:
    registry.register("test_generator", LLMTestGenerator, name="llm")
