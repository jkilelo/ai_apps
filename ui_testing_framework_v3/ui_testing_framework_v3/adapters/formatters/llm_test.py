"""Formatter that prepares element data for LLM-based test generation (stub)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ui_testing_framework_v3.ports.formatter import IFormatter

if TYPE_CHECKING:  # pragma: no cover
    from ui_testing_framework_v3.core.models import Element


class LLMTestFormatter(IFormatter):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    def format(self, elements: list[Element]) -> dict[str, Any]:
        by_type: dict[str, list[dict[str, Any]]] = {}
        for e in elements:
            key = e.element_type.value
            by_type.setdefault(key, []).append(
                {
                    "selector": e.selector,
                    "tag": e.tag_name,
                    "interactive": e.is_interactive,
                    "priority": e.test_priority,
                }
            )
        return {"elements": by_type, "counts": {k: len(v) for k, v in by_type.items()}}

    @property
    def format_type(self) -> str:
        return "llm-test"


def register(registry: Any) -> None:
    registry.register("formatter", LLMTestFormatter, name="llm_test")
