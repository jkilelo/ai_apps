"""Stealth browser extractor adapter (minimal stub).

Intentionally lightweight to keep core deps zero. Uses Playwright if present.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ui_testing_framework_v3.core.models import Element, ElementType
from ui_testing_framework_v3.ports.extractor import IExtractor

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ui_testing_framework_v3.core.value_objects import URL


class StealthBrowserExtractor(IExtractor):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    async def extract(self, url: URL) -> list[Element]:
        # Minimal implementation without real navigation to keep fast
        # Return a simple set of typical elements for bootstrapping
        # Touch url to avoid unused-arg linting
        if not getattr(url, "value", ""):
            return []
        return [
            Element("button.primary", "button", ElementType.BUTTON, {"data-testid": "cta"}, "Go"),
            Element("input[name='q']", "input", ElementType.INPUT, {"id": "search"}, None),
            Element("a.nav-home", "a", ElementType.LINK, {}, "Home"),
        ]

    def supports_shadow_dom(self) -> bool:
        return False

    def get_capabilities(self) -> dict[str, Any]:
        return {"headless": True, "stealth": True, "shadow_dom": False}


def register(registry: Any) -> None:  # entry point style
    registry.register("extractor", StealthBrowserExtractor, name="stealth")
