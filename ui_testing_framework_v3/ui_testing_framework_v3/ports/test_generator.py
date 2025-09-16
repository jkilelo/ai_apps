"""Port for generating tests from formatted data."""

from typing import Any, Protocol, runtime_checkable

from ui_testing_framework_v3.core.models import TestCase


@runtime_checkable
class ITestGenerator(Protocol):
    async def generate(self, formatted_data: dict[str, Any]) -> list[TestCase]:
        """Generate a list of test cases from formatted data."""

    def get_supported_types(self) -> list[str]:
        """Return supported test generation types."""
