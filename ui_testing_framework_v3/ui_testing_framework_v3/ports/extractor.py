"""Port for element extraction (contract only)."""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:  # pragma: no cover
    from ui_testing_framework_v3.core.models import Element
    from ui_testing_framework_v3.core.value_objects import URL


@runtime_checkable
class IExtractor(Protocol):
    async def extract(self, url: "URL") -> list["Element"]:
        """Extract elements from the given URL."""

    def supports_shadow_dom(self) -> bool:
        """Return True if extractor supports shadow DOM."""

    def get_capabilities(self) -> dict[str, Any]:
        """Return capability flags for this extractor implementation."""
