"""Headless browser abstraction with stealth-oriented hooks.

This file was rewritten to resolve indentation and parsing issues while
retaining previously introduced capabilities:
 - Async context manager based session (when Playwright available)
 - Fingerprint mitigation strategy interface + three simple strategies
 - Timing jitter helper
 - User-Agent rotation via fake-useragent (with fallback UA)

Tests exercise only the ability to inject init scripts, so the Playwright
integration path remains lightweight and lazily imported.
"""

from __future__ import annotations

import asyncio
import contextlib
import random
import os
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Protocol, Any
from core.human_simulation import HumanInteractionSimulator

try:  # optional dependency
    from playwright.async_api import async_playwright  # type: ignore
except Exception:  # pragma: no cover
    async_playwright = None  # type: ignore

import fake_useragent  # type: ignore


class FingerprintStrategy(Protocol):
    async def apply(self, page: Any) -> None:  # pragma: no cover - interface placeholder
        ...


@dataclass
class BrowserConfig:
    # Always run with a visible browser window (user request / enforced)
    headless: bool = False
    navigation_timeout_ms: int = 15000
    jitter_range: tuple[float, float] = (0.05, 0.25)  # seconds
    user_agent: Optional[str] = None
    apply_fp_strategies: bool = True
    # New stealth surface diversity controls
    locale: str = "en-US"
    timezone: Optional[str] = None  # If None we'll randomize from a safe pool
    randomize_viewport: bool = True

    # Advanced JS stealth toggles (allow quick experimentation / ablation)
    inject_advanced_stealth: bool = True
    spoof_hardware: bool = True
    spoof_permissions: bool = True
    spoof_webrtc: bool = True
    spoof_battery: bool = True
    patch_function_tostring: bool = True
    hide_webdriver_property: bool = True
    plugin_spoof_count: int = 5


def _random_user_agent() -> str:
    """Generate a plausible modern Chrome UA.

    We still attempt fake_useragent first (wide variety) but sometimes its DB is stale
    which increases detection. Fallback builds a fresh UA with a random minor/patch.
    """
    try:
        return fake_useragent.UserAgent().random  # type: ignore
    except Exception:  # pragma: no cover - fallback path
        major = random.choice([123, 124, 125, 126, 127])
        build = random.randint(6000, 7000)
        patch = random.randint(0, 150)
        return (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major}.0.{build}.{patch} Safari/537.36"
        )


class BrowserSession:
    """Stealth-capable browser session (lightweight wrapper around Playwright)."""

    def __init__(
        self,
        config: Optional[BrowserConfig] = None,
        *,
        rng: Optional[random.Random] = None,
        fp_strategies: Optional[list[FingerprintStrategy]] = None,
    ) -> None:
        # Configuration & RNG
        self.config = config or BrowserConfig()
        if self.config.headless:
            self.config.headless = False
        self._rng = rng or random.Random()

        # Playwright runtime handles (populated in __aenter__)
        self._playwright: Any = None
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None

        # Fingerprint strategies & human simulation helper
        base = fp_strategies or _default_fp_strategies()
        # Deterministic shuffle using provided rng for reproducibility
        self._fp_strategies = list(base)
        if len(self._fp_strategies) > 1 and not os.getenv("FIXED_STEALTH_ORDER"):
            self._rng.shuffle(self._fp_strategies)
        self._human_sim = HumanInteractionSimulator(rng=self._rng)
        # Detection tracking
        self._detection_events_total = 0
        self._detection_consecutive = 0
        self._last_detection_signals: list[str] = []
        self._last_detection_ts = None  # type: ignore[assignment]
        self._abandon_flag = False
        # Domain cooldown registry: domain -> epoch seconds when usable again
        self._domain_cooldowns = {}

    async def __aenter__(self) -> "BrowserSession":
        if async_playwright is None:
            raise RuntimeError("playwright not available - ensure dependency installed")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.config.headless)
        ua = self.config.user_agent or _random_user_agent()

        # Randomize timezone if not provided (small vetted pool to avoid unrealistic combos)
        if not self.config.timezone:
            self.config.timezone = random.choice(
                [
                    "America/New_York",
                    "America/Chicago",
                    "Europe/Berlin",
                    "Europe/Amsterdam",
                    "Asia/Singapore",
                    "Asia/Tokyo",
                ]
            )

        viewport = None
        if self.config.randomize_viewport:
            # Choose among common desktop resolutions
            viewport = random.choice(
                [
                    {"width": 1920, "height": 1080},
                    {"width": 1680, "height": 1050},
                    {"width": 1600, "height": 900},
                    {"width": 1536, "height": 864},
                    {"width": 1366, "height": 768},
                ]
            )
        self._context = await self._browser.new_context(
            user_agent=ua,
            locale=self.config.locale,
            timezone_id=self.config.timezone,
            **({"viewport": viewport} if viewport else {}),
        )
        self._page = await self._context.new_page()
        if self.config.apply_fp_strategies:
            for strat in self._fp_strategies:
                with contextlib.suppress(Exception):
                    await strat.apply(self._page)
        # Advanced stealth injection (single pass) after baseline strategies
        if self.config.inject_advanced_stealth:
            with contextlib.suppress(Exception):
                await _inject_advanced_stealth(self._page, self.config)
        return self

    async def refresh_identity(self) -> None:
        """Rotate high-signal surfaces (UA, timezone, viewport) within the same browser.

        Some anti-bot systems track context-level identifiers. We keep the underlying
        Browser (process) but swap to a fresh context with new randomized parameters.
        """
        if self._browser is None:
            raise RuntimeError("Browser not started")
        # Close old context
        with contextlib.suppress(Exception):
            if self._context:
                await self._context.close()
        # Randomize config aspects (unless user fixed them)
        self.config.user_agent = None  # force regeneration
        # New timezone randomization
        self.config.timezone = None
        ua = self.config.user_agent or _random_user_agent()
        if not self.config.timezone:
            self.config.timezone = random.choice(
                [
                    "America/Los_Angeles",
                    "Europe/London",
                    "Europe/Paris",
                    "Asia/Hong_Kong",
                    "Asia/Seoul",
                    "Australia/Sydney",
                ]
            )
        viewport = None
        if self.config.randomize_viewport:
            viewport = random.choice(
                [
                    {"width": 1920, "height": 1080},
                    {"width": 1440, "height": 900},
                    {"width": 1366, "height": 768},
                ]
            )
        self._context = await self._browser.new_context(
            user_agent=ua,
            locale=self.config.locale,
            timezone_id=self.config.timezone,
            **({"viewport": viewport} if viewport else {}),
        )
        self._page = await self._context.new_page()
        if self.config.apply_fp_strategies:
            for strat in self._fp_strategies:
                with contextlib.suppress(Exception):
                    await strat.apply(self._page)
        if self.config.inject_advanced_stealth:
            with contextlib.suppress(Exception):
                await _inject_advanced_stealth(self._page, self.config)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        with contextlib.suppress(Exception):
            if self._context:
                await self._context.close()
        with contextlib.suppress(Exception):
            if self._browser:
                await self._browser.close()
        with contextlib.suppress(Exception):
            if self._playwright:
                await self._playwright.stop()

    @property
    def page(self) -> Any:
        if self._page is None:
            raise RuntimeError("BrowserSession not started")
        return self._page

    async def navigate(self, url: str, *, wait_until: str = "load") -> None:
        p = self.page
        await p.goto(url, wait_until=wait_until, timeout=self.config.navigation_timeout_ms)
        await self._jitter()

    async def content(self) -> str:
        return await self.page.content()

    async def evaluate(self, script: str) -> Any:
        return await self.page.evaluate(script)

    async def _jitter(self) -> None:
        low, high = self.config.jitter_range
        if high <= 0:
            return
        delay = self._rng.uniform(low, high)
        await asyncio.sleep(delay)

    async def simulate_human(self, *, duration_s: float = 1.0) -> int:
        if self._page is None:
            raise RuntimeError("BrowserSession not started")
        # We deliberately do not sleep between events for speed; can be toggled later.
        return await self._human_sim.perform(self._page, duration_s=duration_s, sleep=False)

    async def verify_stealth(self) -> dict[str, bool]:
        """Lightweight post-init verification of core spoofed surfaces.

        Returns a dict mapping check name -> bool. Failing or exceptioned checks return False.
        Designed to be best-effort (never raises) so callers can include results in reports.
        """
        results: dict[str, bool] = {}
        if self._page is None:
            return {"session_started": False}
        checks = {
            "navigator_properties": "(() => { try { return !!(navigator.languages && navigator.platform); } catch { return false; } })();",
            "canvas_noise": "(() => { try { const c=document.createElement('canvas'); const ctx=c.getContext('2d'); ctx.fillStyle='#f00'; ctx.fillRect(0,0,10,10); return typeof c.toDataURL==='string'; } catch { return false; } })();",
            "timezone_mask": "(() => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone !== undefined; } catch { return false; } })();",
            "webdriver_hidden": "(() => { try { return navigator.webdriver === undefined; } catch { return false; } })();",
            "chrome_runtime": "(() => { try { return !!(window.chrome && window.chrome.runtime); } catch { return false; } })();",
            "plugins_spoofed": "(() => { try { return (navigator.plugins||[]).length >= 3; } catch { return false; } })();",
            "hardware_concurrency": "(() => { try { return navigator.hardwareConcurrency && navigator.hardwareConcurrency >= 4; } catch { return false; } })();",
        }
        for name, script in checks.items():
            try:
                val = await self.evaluate(script)
                results[name] = bool(val)
            except Exception:  # pragma: no cover - defensive
                results[name] = False
        return results

    # ---------------- Detection & Adaptive Identity Utilities -----------------
    def record_detection(self, signals: list[str]) -> dict[str, Any]:
        """Record detection signals and compute severity & adaptive guidance.

        Severity heuristic:
          HIGH: contains 'captcha' or 'cloudflare' or 'are you a robot'
          MEDIUM: contains 'unusual traffic' / 'verify you are human'
          LOW: anything else (fallback)

        Adaptive suggestions encoded:
          rotate_identity: bool
          abandon: bool (if too many consecutive HIGH events)
          backoff_seconds: float (progressive)
        """
        now = asyncio.get_event_loop().time()
        self._detection_events_total += 1
        self._detection_consecutive += 1
        self._last_detection_signals = list(signals)
        self._last_detection_ts = now

        sig_low = [s.lower() for s in signals]
        high_markers = ["captcha", "cloudflare", "are you a robot"]
        medium_markers = ["unusual traffic", "verify you are human"]

        severity = "LOW"
        if any(m in sig for sig in sig_low for m in high_markers):
            severity = "HIGH"
        elif any(m in sig for sig in sig_low for m in medium_markers):
            severity = "MEDIUM"

        # Progressive backoff (quadratic-ish growth but bounded)
        backoff = min(30.0, 1.5 * (self._detection_consecutive**2)) if severity != "LOW" else 0.0

        rotate_identity = severity in {"HIGH", "MEDIUM"}
        abandon = False
        if severity == "HIGH" and self._detection_consecutive >= 3:
            abandon = True
            self._abandon_flag = True

        return {
            "severity": severity,
            "rotate_identity": rotate_identity,
            "abandon": abandon,
            "backoff_seconds": backoff,
            "consecutive": self._detection_consecutive,
            "total": self._detection_events_total,
        }

    async def apply_backoff(self, seconds: float) -> None:
        if seconds > 0:
            await asyncio.sleep(seconds)

    def reset_detection_streak(self) -> None:
        self._detection_consecutive = 0

    def detection_stats(self) -> dict[str, Any]:
        return {
            "events_total": self._detection_events_total,
            "consecutive": self._detection_consecutive,
            "last_signals": self._last_detection_signals,
            "last_ts": self._last_detection_ts,
            "abandon_flag": self._abandon_flag,
        }

    # ---------------- Domain Cooldown Management ------------------------------
    def schedule_domain_cooldown(self, domain: str, seconds: float) -> None:
        if seconds <= 0:
            return
        now = time.time()
        prev = self._domain_cooldowns.get(domain, 0.0)
        target = max(prev, now + seconds)
        self._domain_cooldowns[domain] = target

    async def ensure_domain_ready(self, domain: str) -> None:
        ts = self._domain_cooldowns.get(domain)
        if not ts:
            return
        now = time.time()
        if ts <= now:
            return
        await asyncio.sleep(min(60.0, ts - now))


# --- Stealth script loading & strategies -------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "stealth" / "scripts"


def _load_script(name: str) -> str:
    path = SCRIPTS_DIR / name
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"// missing stealth script: {name}"


class _NavigatorSpoofStrategy:
    async def apply(self, page: Any) -> None:  # pragma: no cover - minimal
        await page.add_init_script(_load_script("navigator_spoof.js"))  # type: ignore[attr-defined]


class _CanvasNoiseStrategy:
    async def apply(self, page: Any) -> None:  # pragma: no cover - minimal
        await page.add_init_script(_load_script("canvas_noise.js"))  # type: ignore[attr-defined]


class _TimezoneMaskStrategy:
    async def apply(self, page: Any) -> None:  # pragma: no cover - minimal
        await page.add_init_script(_load_script("timezone_mask.js"))  # type: ignore[attr-defined]


class _WebGLVendorStrategy:
    async def apply(self, page: Any) -> None:  # pragma: no cover - minimal
        await page.add_init_script(_load_script("webgl_vendor.js"))  # type: ignore[attr-defined]


class _AudioContextNoiseStrategy:
    async def apply(self, page: Any) -> None:  # pragma: no cover - minimal
        await page.add_init_script(_load_script("audio_context_noise.js"))  # type: ignore[attr-defined]


class _FontMaskStrategy:
    async def apply(self, page: Any) -> None:  # pragma: no cover - minimal
        await page.add_init_script(_load_script("font_mask.js"))  # type: ignore[attr-defined]


def _default_fp_strategies() -> list[FingerprintStrategy]:  # pragma: no cover simple list
    # Order intentionally shuffled-like (can randomize later) to reduce static signature
    return [
        _NavigatorSpoofStrategy(),
        _CanvasNoiseStrategy(),
        _TimezoneMaskStrategy(),
        _WebGLVendorStrategy(),
        _AudioContextNoiseStrategy(),
        _FontMaskStrategy(),
    ]


async def _inject_advanced_stealth(page: Any, config: BrowserConfig) -> None:
    """Inject a consolidated advanced stealth script.

    The goal is to collapse multiple high-signal surfaces into realistic values *early*.
    We keep it in a single init_script to reduce ordering race conditions.
    """
    # Build JS dynamically allowing toggles
    js_parts: list[str] = ["(() => { try {"]

    if config.hide_webdriver_property:
        js_parts.append(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined}); delete window.__playwright; delete window.__puppeteer; delete window.__selenium;"
        )

    # Chrome runtime skeleton
    js_parts.append(
        "if(!window.chrome){window.chrome={runtime:{},app:{},csi:()=>{},loadTimes:()=>{}};} if(!window.chrome.runtime) window.chrome.runtime={};"
    )

    # Permissions spoof (notifications) & toString patch
    if config.spoof_permissions:
        js_parts.append(
            "const _permQ=navigator.permissions && navigator.permissions.query; if(_permQ){navigator.permissions.query=(p)=>p && p.name==='notifications'?Promise.resolve({state:Notification.permission}):_permQ(p);}"
        )

    if config.patch_function_tostring:
        js_parts.append(
            "const _fts=Function.prototype.toString; Function.prototype.toString=function(){const m=['navigator.permissions.query','chrome.runtime.sendMessage']; for(const k of m){ if(this && this.name && k.endsWith(this.name)) return 'function '+this.name+'() { [native code] }'; } return _fts.call(this); };"
        )

    # Plugins & languages
    js_parts.append(
        f"Object.defineProperty(navigator,'plugins',{{get:()=>Array({max(3,min(10,config.plugin_spoof_count))}).fill(0).map((_,i)=>({{name:'Plugin'+i,filename:'plugin'+i+'.dll',description:'',length:1}}))}});"
    )
    js_parts.append("Object.defineProperty(navigator,'languages',{get:()=>['en-US','en']});")

    # Hardware spoof
    if config.spoof_hardware:
        js_parts.append(
            "Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>8}); if('deviceMemory' in navigator){Object.defineProperty(navigator,'deviceMemory',{get:()=>8});}"
        )
        js_parts.append(
            "Object.defineProperty(screen,'colorDepth',{get:()=>24}); Object.defineProperty(screen,'pixelDepth',{get:()=>24});"
        )

    # Battery
    if config.spoof_battery:
        js_parts.append(
            "if(navigator.getBattery){navigator.getBattery=()=>Promise.resolve({charging:true,chargingTime:0,dischargingTime:Infinity,level:0.96,addEventListener:()=>{},removeEventListener:()=>{}});}"
        )

    # WebRTC leak blocking
    if config.spoof_webrtc:
        js_parts.append(
            "if(window.RTCPeerConnection){const ORTC=window.RTCPeerConnection; window.RTCPeerConnection=new Proxy(ORTC,{construct(t,a){const pc=new t(...a); const _co=pc.createOffer; pc.createOffer=async()=>({type:'offer',sdp:''}); return pc;}});}"
        )

    # Minor timing jitter for setTimeout 0 -> 1-5ms
    js_parts.append(
        "const _sto=setTimeout; window.setTimeout=function(cb,ms,...r){ if(ms===0){ms=1+Math.floor(Math.random()*5);} return _sto(cb,ms,...r); };"
    )

    js_parts.append("}catch(e){/* swallow */}})();")

    await page.add_init_script("\n".join(js_parts))  # type: ignore[attr-defined]


__all__ = [
    "BrowserSession",
    "BrowserConfig",
    "FingerprintStrategy",
]
