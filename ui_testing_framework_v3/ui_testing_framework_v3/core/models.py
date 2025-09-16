"""Domain models: immutable data structures with business rules.
Only Python built-ins are used in this module.
"""

from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import Any

from ui_testing_framework_v3.core.exceptions import InvalidElementError


class ElementType(Enum):
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    SELECT = "select"
    TEXTAREA = "textarea"
    IMAGE = "image"
    TEXT = "text"
    CONTAINER = "container"


@dataclass(frozen=True)
class Element:
    """Immutable domain model representing a UI element."""

    selector: str
    tag_name: str
    element_type: ElementType
    attributes: dict[str, Any] = field(default_factory=dict)
    text: str | None = None

    def __post_init__(self) -> None:
        if not self.selector:
            raise InvalidElementError()
        if not self.tag_name:
            raise InvalidElementError()

    @cached_property
    def is_interactive(self) -> bool:
        return self.element_type in (
            ElementType.BUTTON,
            ElementType.INPUT,
            ElementType.LINK,
            ElementType.SELECT,
            ElementType.TEXTAREA,
        )

    @cached_property
    def interaction_score(self) -> float:
        score = 0.0
        # Base score by type
        if self.element_type == ElementType.BUTTON:
            score += 0.4
        elif self.element_type == ElementType.INPUT:
            score += 0.35
        elif self.element_type == ElementType.LINK:
            score += 0.3
        elif self.element_type in (ElementType.SELECT, ElementType.TEXTAREA):
            score += 0.25

        # Accessibility
        if self.attributes.get("aria-label"):
            score += 0.2
        if self.attributes.get("aria-describedby"):
            score += 0.1

        # Testability
        if self.attributes.get("id"):
            score += 0.15
        if self.attributes.get("data-testid"):
            score += 0.2

        return min(score, 1.0)

    @cached_property
    def test_priority(self) -> str:
        high_threshold = 0.7
        medium_threshold = 0.4
        if self.interaction_score >= high_threshold:
            return "high"
        if self.interaction_score >= medium_threshold:
            return "medium"
        return "low"


@dataclass
class TestCase:
    """Domain model for test cases with business-rule validation."""

    name: str
    description: str
    steps: list[str]
    assertions: list[str]
    priority: str = "medium"
    tags: list[str] = field(default_factory=list)

    def validate(self) -> bool:
        if not self.name:
            return False
        if len(self.steps) == 0:
            return False
        if len(self.assertions) == 0:
            return False
        return self.priority in ("low", "medium", "high", "critical")

    def estimated_duration(self) -> int:
        base_time = len(self.steps) * 2
        assertion_time = len(self.assertions) * 1
        if self.priority == "critical":
            multiplier = 1.5
        elif self.priority == "high":
            multiplier = 1.2
        else:
            multiplier = 1.0
        return int((base_time + assertion_time) * multiplier)
