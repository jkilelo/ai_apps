"""Simple test generator that maps formatted data into trivial test cases."""

from __future__ import annotations

from typing import Any

from ui_testing_framework_v3.core.models import TestCase
from ui_testing_framework_v3.ports.test_generator import ITestGenerator


class SimpleTestGenerator(ITestGenerator):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    async def generate(self, formatted_data: dict[str, Any]) -> list[TestCase]:
        tests: list[TestCase] = []
        for group, items in formatted_data.get("elements", {}).items():
            name = f"Smoke - {group} present"
            steps = [f"Assert presence of {len(items)} {group} elements"]
            assertions = [f"At least 1 {group} element exists"]
            tests.append(TestCase(name=name, description=name, steps=steps, assertions=assertions))
        return tests

    def get_supported_types(self) -> list[str]:
        return ["llm-test"]


def register(registry: Any) -> None:
    registry.register("test_generator", SimpleTestGenerator, name="simple")
