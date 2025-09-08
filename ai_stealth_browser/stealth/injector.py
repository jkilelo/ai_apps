"""Stealth script injection extracted from monolith (phase 1).

Future work:
- Split script templates into discrete strategy units
- Add checksum/versioning and caching
- Provide evaluation hooks for detection surface deltas
"""

from __future__ import annotations
from playwright.async_api import Page  # type: ignore
from .config import StealthConfig, StealthLevel
import logging

logger = logging.getLogger(__name__)


class StealthInjector:
    @staticmethod
    async def inject_stealth(page: Page, config: StealthConfig) -> None:
        await StealthInjector._inject_basic_stealth(page, config)
        if config.level in [StealthLevel.ENHANCED, StealthLevel.MAXIMUM, StealthLevel.PARANOID]:
            await StealthInjector._inject_enhanced_stealth(page, config)
        if config.level in [StealthLevel.MAXIMUM, StealthLevel.PARANOID]:
            await StealthInjector._inject_maximum_stealth(page, config)
        if config.level == StealthLevel.PARANOID:
            await StealthInjector._inject_paranoid_stealth(page, config)
        logger.debug("Stealth injection complete: %s", config.level.value)

    @staticmethod
    async def _inject_basic_stealth(
        page: Page, config: StealthConfig
    ) -> None:  # pragma: no cover (script pass-through)
        script = """
        () => {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {}, app: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US','en'] });
            delete window.__playwright; delete window.__puppeteer; delete window.__selenium;
        }
        """
        await page.add_init_script(script)

    @staticmethod
    async def _inject_enhanced_stealth(
        page: Page, config: StealthConfig
    ) -> None:  # pragma: no cover
        script = "() => { /* enhanced runtime stubs */ }"
        await page.add_init_script(script)

    @staticmethod
    async def _inject_maximum_stealth(
        page: Page, config: StealthConfig
    ) -> None:  # pragma: no cover
        script = "() => { /* maximum fingerprint spoofing */ }"
        await page.add_init_script(script)

    @staticmethod
    async def _inject_paranoid_stealth(
        page: Page, config: StealthConfig
    ) -> None:  # pragma: no cover
        script = "() => { /* paranoid level anti-detection */ }"
        await page.add_init_script(script)


__all__ = ["StealthInjector"]
