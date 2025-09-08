"""Structured extraction engine.

Provides simple CSS-based extraction into Pydantic models.
Designed to be extended with heuristics later.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedItem(BaseModel):
    selector: str
    text: Optional[str] = None


class ExtractionPlan(BaseModel):
    items: List[str] = Field(default_factory=list, description="CSS selectors")


async def run_extraction(session, plan: ExtractionPlan) -> list[ExtractedItem]:
    out: list[ExtractedItem] = []
    page = session.page
    for sel in plan.items:
        txt = None
        try:
            el = await page.query_selector(sel)  # type: ignore[attr-defined]
            if el:
                raw = await el.text_content()
                txt = raw.strip() if raw else None
        except Exception:
            txt = None
        out.append(ExtractedItem(selector=sel, text=txt))
    return out


__all__ = ["ExtractedItem", "ExtractionPlan", "run_extraction"]
