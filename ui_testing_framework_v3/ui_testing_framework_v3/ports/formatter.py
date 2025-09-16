"""Port for formatting extracted elements for various use cases."""

from typing import Any, Protocol, runtime_checkable

from ui_testing_framework_v3.core.models import Element


@runtime_checkable
class IFormatter(Protocol):
    def format(self, elements: list[Element]) -> dict[str, Any]:
        """Format elements and return a data structure for downstream usage."""

    @property
    def format_type(self) -> str:  # pragma: no cover - trivial property in protocols
        """Identifier for the formatter output type."""
