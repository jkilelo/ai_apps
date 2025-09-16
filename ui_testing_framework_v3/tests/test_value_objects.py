from __future__ import annotations

import pytest

from ui_testing_framework_v3.core.exceptions import DomainError
from ui_testing_framework_v3.core.value_objects import URL, CSSSelector


def test_url_domain_and_validation() -> None:
    u = URL("https://example.com/path")
    assert u.domain == "example.com"
    with pytest.raises(DomainError):
        URL("")


def test_css_selector_specificity() -> None:
    s = CSSSelector("#id .class tag")
    assert s.specificity_score >= 111
    with pytest.raises(DomainError):
        CSSSelector("")
