"""Value objects for the core domain (immutable, validated)."""

import re
from dataclasses import dataclass

from ui_testing_framework_v3.core.exceptions import DomainError


@dataclass(frozen=True)
class URL:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise DomainError()
        pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"localhost|\d{1,3}(?:\.\d{1,3}){3})"
            r"(?::\d+)?(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if not pattern.match(self.value):
            raise DomainError()

    @property
    def domain(self) -> str:
        parts = self.value.replace("http://", "").replace("https://", "").split("/")[0]
        return parts.split(":")[0]


@dataclass(frozen=True)
class CSSSelector:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise DomainError()
        invalid = ("javascript:", "<script", "onclick=")
        for pat in invalid:
            if pat in self.value.lower():
                raise DomainError()

    @property
    def specificity_score(self) -> int:
        score = 0
        score += self.value.count("#") * 100
        score += self.value.count(".") * 10
        score += len([p for p in self.value.split() if not p.startswith(("#", ".", "["))])
        return score
