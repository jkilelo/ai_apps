import pytest

from ui_testing_framework_v3.core.exceptions import DomainError, InvalidElementError
from ui_testing_framework_v3.core.models import Element, ElementType, TestCase
from ui_testing_framework_v3.core.value_objects import URL, CSSSelector


def test_element_scores_and_priorities() -> None:
    # High priority: button with rich attrs
    e_high = Element(
        "#submit",
        "button",
        ElementType.BUTTON,
        {"aria-label": "Submit", "aria-describedby": "desc", "id": "s", "data-testid": "t"},
        "Go",
    )
    assert e_high.is_interactive is True
    assert e_high.interaction_score >= 0.7
    assert e_high.test_priority == "high"

    # Medium priority: link with id only
    e_med = Element("a.link", "a", ElementType.LINK, {"id": "i"})
    assert 0.4 <= e_med.interaction_score < 0.7
    assert e_med.test_priority == "medium"

    # Low priority: plain text
    e_low = Element("div.text", "div", ElementType.TEXT, {})
    assert e_low.is_interactive is False
    assert e_low.test_priority == "low"

    # Validation: missing tag_name
    with pytest.raises(InvalidElementError):
        Element("#x", "", ElementType.BUTTON)


def test_testcase_validation_and_duration() -> None:
    tc = TestCase(
        name="Checkout",
        description="Checkout flow",
        steps=["Open", "Fill", "Submit"],
        assertions=["Success"],
        priority="critical",
    )
    assert tc.validate() is True
    assert tc.estimated_duration() > 0

    # Invalid cases
    assert TestCase(name="", description="d", steps=["s"], assertions=["a"]).validate() is False
    assert TestCase(name="n", description="d", steps=[], assertions=["a"]).validate() is False
    assert TestCase(name="n", description="d", steps=["s"], assertions=[]).validate() is False


def test_value_objects_more_validation() -> None:
    with pytest.raises(DomainError):
        URL("ftp://example.com")
    with pytest.raises(DomainError):
        CSSSelector("onclick=evil()")
