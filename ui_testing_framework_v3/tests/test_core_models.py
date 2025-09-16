import pytest

from ui_testing_framework_v3.core.exceptions import InvalidElementError
from ui_testing_framework_v3.core.models import Element, ElementType


def test_element_interaction_and_priority():
    e = Element("#submit", "button", ElementType.BUTTON, {"data-testid": "btn"}, "Go")
    assert e.is_interactive is True
    assert 0.0 < e.interaction_score <= 1.0
    assert e.test_priority in {"high", "medium", "low"}


def test_element_validation_failure():
    with pytest.raises(InvalidElementError):
        Element("", "button", ElementType.BUTTON)
