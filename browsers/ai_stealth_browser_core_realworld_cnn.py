"""Real-world CNN category news extraction utility.

Fetches 5-7 prominent recent articles from a CNN category page by
visiting the listing page, collecting candidate article URLs, then
opening each article to extract structured fields.

This intentionally avoids any LLM usage so it can run without an
API key (useful for real-world smoke validation of the browser layer).

NOTE: CNN page structures can change; selectors are best-effort and
defensively wrapped.
"""

from __future__ import annotations

import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field

from core.browser import BrowserSession, BrowserConfig


class Article(BaseModel):
    headline: str = Field(...)
    url: str = Field(...)
    author: Optional[str] = None
    published: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None


async def _dismiss_overlays(session: BrowserSession) -> None:
    page = session.page
    # Try a handful of common consent / subscription dismiss patterns.
    candidates = ["Accept", "AGREE", "I Agree", "Consent", "Continue", "Close"]
    for text in candidates:
        try:
            btn = await page.query_selector(f"button:has-text('{text}')")  # type: ignore[arg-type]
            if btn:
                await btn.click(timeout=1500)
        except Exception:
            pass


async def _collect_listing_article_urls(
    session: BrowserSession, category: str, limit: int = 12
) -> List[str]:
    page = session.page
    # Heuristic extraction via h3/h2 anchors.
    script = f"""
    (() => {{
      const anchors = Array.from(document.querySelectorAll('h3 a, h2 a'));
      const seen = new Set();
      const out = [];
      for (const a of anchors) {{
        if (!a.href) continue;
        if (!a.href.includes('cnn.com')) continue;
        if (a.href.includes('/videos/')) continue; // skip videos
        // loosen category filter to increase recall
        if (!seen.has(a.href)) {{
          seen.add(a.href);
          out.push(a.href);
        }}
        if (out.length >= {limit}) break;
      }}
      return out;
    }})()
    """
    try:
        urls = await page.evaluate(script)
        return list(urls)[:limit]
    except Exception:
        return []


async def _extract_article(session: BrowserSession, url: str, category: str) -> Optional[Article]:
    try:
        await session.navigate(url)
    except Exception:
        return None
    page = session.page
    await _dismiss_overlays(session)
    extract_script = """
    (() => {
      function txt(sel){ const el = document.querySelector(sel); return el ? el.textContent.trim() : null; }
      function meta(name, attr='content'){ const el = document.querySelector(`meta[name="${name}"]`) || document.querySelector(`meta[property="${name}"]`); return el ? el.getAttribute(attr) : null; }
      const headline = txt('h1') || meta('og:title') || meta('twitter:title');
      const author = txt('[data-type="byline-area"] a') || txt('.byline__names') || meta('author');
      const published = meta('og:pubdate') || meta('pubdate') || meta('article:published_time') || txt('time');
      const summary = meta('description') || meta('og:description');
      const image = meta('og:image') || meta('twitter:image');
      return {headline, author, published, summary, image};
    })()
    """
    try:
        data = await page.evaluate(extract_script)
    except Exception:
        return None
    if not data or not data.get("headline"):
        return None
    return Article(
        headline=data.get("headline") or url,
        url=url,
        author=data.get("author"),
        published=data.get("published"),
        summary=data.get("summary"),
        category=category,
        image=data.get("image"),
    )


async def fetch_cnn_category_articles(category: str, *, max_articles: int = 7) -> list[Article]:
    """Fetch up to `max_articles` articles for a CNN category.

    Category examples: 'world', 'business', 'technology', 'politics'.
    """
    base_url = f"https://www.cnn.com/{category.strip('/')}/"
    articles: list[Article] = []
    async with BrowserSession(BrowserConfig(headless=False, apply_fp_strategies=True)) as session:
        await session.navigate(base_url)
        await _dismiss_overlays(session)
        urls = await _collect_listing_article_urls(session, category)
        for u in urls:
            art = await _extract_article(session, u, category)
            if art:
                articles.append(art)
            if len(articles) >= max_articles:
                break
    return articles


def run_cnn_extraction(category: str) -> dict:
    async def _inner():
        try:
            arts = await fetch_cnn_category_articles(category)
            return {
                "category": category,
                "count": len(arts),
                "articles": [
                    (a.model_dump() if hasattr(a, "model_dump") else a.dict()) for a in arts
                ],  # pydantic v2 (fallback for older)
            }
        except Exception as e:  # pragma: no cover - runtime safety
            return {"category": category, "error": str(e), "articles": []}

    return asyncio.run(_inner())


__all__ = ["fetch_cnn_category_articles", "run_cnn_extraction", "Article"]
