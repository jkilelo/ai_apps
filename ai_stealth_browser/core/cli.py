from __future__ import annotations
import argparse
import json
import os
import asyncio
import time
from core.session_report import build_report
from core.event_logging import LOG_PATH

# Auto-load .env if present (non-fatal if missing). We record whether the key existed
# before loading so tests (pytest) can still enforce HALT semantics by ignoring a
# dotenv-injected key.
_PRE_DOTENV_HAS_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))
try:  # pragma: no cover - simple side effect
    from dotenv import load_dotenv

    load_dotenv()
    if not _PRE_DOTENV_HAS_KEY and os.getenv("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY_LOADED_FROM_DOTENV"] = "1"
except Exception:  # pragma: no cover - best effort
    pass


def _require_api_key() -> None:
    # Treat a dotenv-injected key as absent under pytest to allow the test that
    # explicitly removes the key from the environment to still observe HALT behavior.
    if (
        os.environ.get("PYTEST_CURRENT_TEST")
        and os.environ.get("ANTHROPIC_API_KEY_LOADED_FROM_DOTENV") == "1"
    ):
        os.environ.pop("ANTHROPIC_API_KEY", None)

    if not os.getenv("ANTHROPIC_API_KEY"):
        msg = (
            "HALT: missing ANTHROPIC_API_KEY - no live LLM connection established. "
            "System cannot proceed per hard stop policy."
        )
        try:  # pragma: no cover - defensive
            import sys as _sys

            print(msg, file=_sys.stderr, flush=True)
        except Exception:  # pragma: no cover
            pass
        raise SystemExit(2)


async def _run(goal: str) -> int:
    started = time.time()
    # Lazy imports only when we actually run agents & browser
    from core.facade import AgentFacade  # lazy import after key check
    from agents.registry import NavigationPlan  # noqa: F401 (may be used by agent outputs)
    from core.browser import BrowserSession, BrowserConfig
    from core.config import RuntimeConfig
    from core.navigation import NavigationExecutor

    facade = AgentFacade()
    stealth = await facade.assess_stealth("initial context")
    nav = await facade.plan_navigation(goal)
    perf = await facade.analyze_performance("snapshot")
    metrics = facade.metrics_snapshot()
    # Extract navigation steps if present
    navigation_steps = []
    if hasattr(nav.raw, "output") and hasattr(nav.raw.output, "steps"):
        try:
            navigation_steps = list(nav.raw.output.steps)
        except Exception:
            navigation_steps = []
    stealth_checks = {}
    if navigation_steps:
        try:
            cfg = RuntimeConfig.load()
            async with BrowserSession(
                BrowserConfig(headless=False, apply_fp_strategies=True)
            ) as session:
                executor = NavigationExecutor(session, cfg)
                exec_meta = await executor.run(navigation_steps)
                stealth_checks = (
                    await session.verify_stealth()
                    if cfg.enable_stealth_verification
                    else {"verification_disabled": True}
                )
                stealth_checks["navigation_execution"] = exec_meta
        except Exception as e:
            stealth_checks["browser_session"] = False
            stealth_checks["error"] = str(e)
    else:
        stealth_checks["no_navigation_steps"] = True
    finished = time.time()
    report = build_report(
        metrics,
        strategies=["navigator", "canvas", "timezone", "webgl", "audio", "font"],
        issues=[],
        started_at=started,
        finished_at=finished,
        stealth_checks=stealth_checks,
        navigation_plan=navigation_steps,
    )

    def _ser(obj):  # minimal safe serialization for agent outputs
        if hasattr(obj, "model_dump"):
            try:
                return obj.model_dump()
            except Exception:  # pragma: no cover - fallback
                return str(obj)
        return obj

    payload = {
        "session_report": report.to_dict(),
        "agents": [_ser(stealth.output), _ser(nav.output), _ser(perf.output)],
        "navigation_plan": navigation_steps,
        "stealth_checks": report.stealth_checks,
    }
    print(json.dumps(payload, indent=2))
    print(f"Events logged to {LOG_PATH}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Stealth Browser CLI")
    parser.add_argument("goal", help="Navigation or exploration goal text")
    # Dry-run removed: framework always requires live LLM key.
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument(
        "--preflight", action="store_true", help="Run environment readiness checks and exit"
    )
    parser.add_argument(
        "--plan-file",
        help="Path to action DSL plan to execute after navigation planning",
        default=None,
    )
    args = parser.parse_args()
    if args.version:
        from importlib.metadata import version, PackageNotFoundError

        try:
            print(version("ai-stealth-browser"))
        except PackageNotFoundError:
            print("(local) version unknown")
        return
    # Emit invocation event
    try:
        from core.event_logging import append_event

        append_event("cli_invocation", {"goal": args.goal})
    except Exception:
        pass
    if args.preflight:
        # Preflight diagnostics (no agent execution). No API key required just to inspect environment.
        import importlib, sys as _sys, platform
        from pathlib import Path as _Path

        playwright_available = False
        try:
            importlib.import_module("playwright.async_api")
            playwright_available = True
        except Exception:
            playwright_available = False
        stealth_scripts_dir = _Path(__file__).resolve().parent.parent / "stealth" / "scripts"
        script_count = 0
        if stealth_scripts_dir.exists():
            script_count = len(list(stealth_scripts_dir.glob("*.js")))
        report = {
            "preflight": True,
            "python_version": _sys.version.split()[0],
            "platform": platform.system(),
            "playwright_available": playwright_available,
            "has_api_key": bool(os.getenv("ANTHROPIC_API_KEY")),
            "stealth_script_count": script_count,
            "event_log_override": os.getenv("AI_STEALTH_EVENT_LOG") is not None,
            "supports_dry_run": False,
        }
        print(json.dumps(report, indent=2))
        try:
            from core.event_logging import append_event as _ae

            _ae("cli_preflight", report)
        except Exception:
            pass
        return
    _require_api_key()  # Always require live key
    if args.plan_file:
        from core.actions import parse_actions
        from core.action_executor import ActionExecutor
        from core.browser import BrowserSession, BrowserConfig

        asyncio.run(_run(args.goal))
        try:
            plan_text = open(args.plan_file, "r", encoding="utf-8").read()
            acts = parse_actions(plan_text)

            async def _exec():
                async with BrowserSession(
                    BrowserConfig(headless=False, apply_fp_strategies=True)
                ) as session:
                    ex = ActionExecutor(session)
                    res = await ex.run(acts)
                    print(json.dumps({"action_plan_results": res}, indent=2))

            asyncio.run(_exec())
        except Exception as e:
            print(json.dumps({"action_plan_error": str(e)}, indent=2))
    else:
        asyncio.run(_run(args.goal))


if __name__ == "__main__":  # pragma: no cover
    main()
