#!/usr/bin/env python3
"""Blueprint Example: FULL CAPABILITY DEMONSTRATION (MULTI-SITE, HIGH DETECTION SURFACES)

Purpose:
    This is the canonical end‑to‑end blueprint exercising every major capability against
    a set of sites known for stricter bot / automation defenses (search, CDN / edge, dynamic news):
        - Google Search (query based)
        - Cloudflare marketing site (common challenge vocabulary)
        - Hacker News (dynamic but simple markup; good extraction variety)

Features Demonstrated:
    - Live LLM agents (stealth, navigation, performance, security, learning, architect)
    - Strategy evaluation (HumanSimulationStrategy, DetectionMitigationStrategy)
    - Single persistent BrowserSession to preserve a coherent fingerprint
    - Per-site: pre stealth advisory, navigation planning, Action DSL synthesis, execution
    - Structured extraction via ExtractionPlan (site-specific CSS selectors)
    - Per-site bot / challenge signal heuristics (captcha, cloudflare, unusual traffic)
    - Adaptive learning invocation when extraction is sparse or detection signals present
    - Performance & security contextual analyses referencing actual HTML snapshot stats
    - Architecture agent used for meta orchestration documentation
    - Stealth verification (global + per-site snapshot before/after groups)
    - Aggregated SessionReport + Extended comprehensive report (per-site details + detection summary)

HALT policy: requires ANTHROPIC_API_KEY (no mocks / dry-run permitted).

Output:
    examples/outputs/blueprint_report.json containing:
        {
            "session_report": <standard session report>,
            "sites": [ { per-site rich object }... ],
            "detection_summary": { aggregated counts },
            "agent_metrics": <raw metrics snapshot>,
            "architecture_plan": <meta plan>,
            "stealth_global_pre": {..}, "stealth_global_post": {..}
        }
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import re

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.browser import BrowserSession  # type: ignore
from core.facade import AgentFacade  # type: ignore
from core.actions import parse_actions  # type: ignore
from core.action_executor import ActionExecutor  # type: ignore
from core.extraction import ExtractionPlan, run_extraction  # type: ignore
from core.session_report import build_report  # type: ignore

OUTPUT_DIR = Path("examples/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


DETECTION_SIGNATURES = [
    "unusual traffic",
    "are you a robot",
    "captcha",
    "verify you are human",
    "cloudflare",
    "attention required",
]

TARGET_SITES: List[Dict[str, Any]] = [
    {
        "label": "google_search",
        "url": "https://www.google.com/search?q=stealth+automation",
        "selectors": ["#search", "h3", "title"],
    },
    {
        "label": "cloudflare_marketing",
        "url": "https://www.cloudflare.com/",
        "selectors": ["h1", "title", "nav a"],
    },
    {
        "label": "hacker_news",
        "url": "https://news.ycombinator.com/",
        "selectors": ["title", ".hnname", "a.storylink", "span.titleline a"],
    },
]


async def _synthesize_dsl(steps: List[str], url: str, selectors: List[str]) -> str:
    lines: List[str] = [f"NAV {url}"]
    for st in steps:
        low = st.lower()
        if "wait" in low:
            lines.append("WAIT 500")
        if "click" in low and ("more" in low or "accept" in low or "consent" in low):
            # heuristic consent/cookie click attempt
            lines.append("CLICK button,button[aria-label*='accept'],text=Accept")
    for sel in selectors:
        lines.append(f"EXTRACT {sel}")
    return "\n".join(lines)


def _detect_signals(html: str) -> List[str]:
    found = []
    low = html.lower()
    for sig in DETECTION_SIGNATURES:
        if sig in low:
            found.append(sig)
    return found


async def _process_site(
    idx: int, site: Dict[str, Any], session: BrowserSession, facade: AgentFacade
) -> Dict[str, Any]:
    label = site["label"]
    url = site["url"]
    selectors: List[str] = site.get("selectors", [])
    site_start = time.time()
    parsed = urlparse(url)
    domain = parsed.netloc
    # Ensure any pre-scheduled cooldown for this domain is respected
    try:
        await session.ensure_domain_ready(domain)
    except Exception:
        pass

    stealth_pre = await facade.assess_stealth(f"Pre-site stealth advisory for {label}")
    plan_goal = f"Plan minimal safe steps to load {url} and prepare for extraction of key content"
    nav_plan_run = await facade.plan_navigation(plan_goal)
    nav_steps: List[str] = (
        getattr(nav_plan_run.output, "steps", []) if not nav_plan_run.error else []
    )
    dsl_script = await _synthesize_dsl(nav_steps, url, selectors)
    actions = parse_actions(dsl_script)

    executor = ActionExecutor(session)
    try:
        await session.simulate_human(duration_s=0.6)
    except Exception:
        pass
    action_result = await executor.run(actions)
    stealth_verification_pre = await session.verify_stealth()
    extraction_plan = ExtractionPlan(items=list(dict.fromkeys(selectors)))
    extracted_items = await run_extraction(session, extraction_plan)
    html_snapshot = await session.page.content()
    detection_signals = _detect_signals(html_snapshot)
    identity_rotated = False
    adaptive_meta: Dict[str, Any] = {}
    stealth_verification_post_rotation: Optional[Dict[str, bool]] = None
    stealth_diff: Optional[Dict[str, Dict[str, bool]]] = None
    high_snapshot_paths: List[str] = []
    scheduled_cooldown = 0.0

    # Helper to persist high severity snapshot
    def _persist_snapshot(html: str, severity: str) -> Optional[str]:
        if severity != "HIGH":
            return None
        snap_dir = OUTPUT_DIR / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        # Basic sanitization: drop <script> content to reduce risk of active code if later viewed
        safe_html = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        fp = snap_dir / f"{label}_{ts}.html"
        try:
            fp.write_text(safe_html, encoding="utf-8")
            return str(fp)
        except Exception:
            return None

    if detection_signals:
        adaptive_meta = session.record_detection(detection_signals)
        # Backoff if required before identity rotation attempt
        await session.apply_backoff(adaptive_meta.get("backoff_seconds", 0.0))
        if adaptive_meta.get("rotate_identity") and not adaptive_meta.get("abandon"):
            try:
                await session.refresh_identity()
                identity_rotated = True
                await session.navigate(url)
                html_snapshot = await session.page.content()
                detection_signals = _detect_signals(html_snapshot)  # re-evaluate
                stealth_verification_post_rotation = await session.verify_stealth()
                if stealth_verification_post_rotation:
                    stealth_diff = {}
                    for k in set(stealth_verification_pre.keys()) | set(
                        stealth_verification_post_rotation.keys()
                    ):
                        pre_v = stealth_verification_pre.get(k)
                        post_v = stealth_verification_post_rotation.get(k)
                        if pre_v != post_v:
                            stealth_diff[k] = {"before": bool(pre_v), "after": bool(post_v)}
            except Exception:
                pass
        if adaptive_meta.get("abandon"):
            # Skip further heavy actions on this site; mark truncated
            sev = adaptive_meta.get("severity", "")
            snap = _persist_snapshot(html_snapshot, sev)
            if snap:
                high_snapshot_paths.append(snap)
            # Schedule domain cooldown based on severity heuristics
            sev_cd = {"LOW": 0, "MEDIUM": 20, "HIGH": 60}
            scheduled_cooldown = float(sev_cd.get(sev, 0))
            if scheduled_cooldown:
                session.schedule_domain_cooldown(domain, scheduled_cooldown)
            return {
                "label": label,
                "url": url,
                "abandoned": True,
                "detection_signals": detection_signals,
                "adaptive_meta": adaptive_meta,
                "high_detection_snapshots": high_snapshot_paths,
                "scheduled_cooldown": scheduled_cooldown,
            }
        # Schedule cooldown if not abandoning but detection occurred
        sev = adaptive_meta.get("severity", "")
        sev_cd = {"LOW": 0, "MEDIUM": 10, "HIGH": 40}
        scheduled_cooldown = float(sev_cd.get(sev, 0))
        if scheduled_cooldown:
            session.schedule_domain_cooldown(domain, scheduled_cooldown)
        snap = _persist_snapshot(html_snapshot, sev)
        if snap:
            high_snapshot_paths.append(snap)

    # Iterative selector refinement loop (max 2 additional passes)
    refinement_runs: List[Dict[str, Any]] = []

    def _extraction_sparse(items: List[Any]) -> bool:
        return sum(1 for it in items if (getattr(it, "text", "") or "").strip()) < max(
            1, len(selectors) // 3
        )

    sparse_initial = _extraction_sparse(extracted_items)
    if sparse_initial and not adaptive_meta.get("abandon"):
        for loop_idx in range(2):
            try:
                learn = await facade.adaptive_learning_update(
                    f"Refinement loop {loop_idx+1} for {label}; sparse extraction; propose improved selectors"
                )
            except Exception as e:  # pragma: no cover
                break
            suggested = []
            if learn.output:
                # Try structured attribute first
                if hasattr(learn.output, "suggested_selectors"):
                    try:
                        suggested = [
                            s
                            for s in getattr(learn.output, "suggested_selectors") or []
                            if isinstance(s, str)
                        ]
                    except Exception:
                        suggested = []
                # Fallback: regex scrape plausible selectors from string repr
                if not suggested:
                    blob = str(learn.output)
                    cand = re.findall(r"[#.][a-zA-Z0-9_-]{3,30}", blob)
                    suggested = list(dict.fromkeys(cand))[:10]
            if suggested:
                merged = list(dict.fromkeys(selectors + suggested))
                extraction_plan = ExtractionPlan(items=merged)
                extracted_items = await run_extraction(session, extraction_plan)
            refinement_runs.append(
                {
                    "loop": loop_idx + 1,
                    "suggested": suggested,
                    "new_count": len(extracted_items),
                    "sparse": _extraction_sparse(extracted_items),
                }
            )
            # Break early if no longer sparse
            if not _extraction_sparse(extracted_items):
                break

    perf_run = await facade.analyze_performance(
        f"Site {label} HTML length={len(html_snapshot)} detection_signals={len(detection_signals)}"
    )
    sec_run = await facade.summarize_security(
        f"Security surface quick review for {label}; heuristic only, no headers captured here."
    )

    sparse = sum(1 for it in extracted_items if (it.text or "").strip()) < max(
        1, len(selectors) // 3
    )
    learning_run = None
    if sparse or detection_signals:
        learning_run = await facade.adaptive_learning_update(
            f"Site {label} sparse={sparse} detection={bool(detection_signals)} refine selectors or timing"
        )
    stealth_post = await facade.assess_stealth(f"Post-site stealth advisory for {label}")
    site_end = time.time()

    site_payload: Dict[str, Any] = {
        "label": label,
        "url": url,
        "nav_plan": nav_steps,
        "dsl": dsl_script,
        "actions_result": action_result,
        "extracted": [x.model_dump() for x in extracted_items],
        "detection_signals": detection_signals,
        "identity_rotated": identity_rotated,
        "adaptive_meta": adaptive_meta,
        "stealth_post_rotation": stealth_verification_post_rotation,
        "stealth_diff": stealth_diff,
        "stealth_pre": (
            getattr(stealth_pre.output, "model_dump", lambda: stealth_pre.output)()
            if stealth_pre.output
            else {"error": stealth_pre.error}
        ),
        "stealth_verification": stealth_verification_pre,
        "stealth_post": (
            getattr(stealth_post.output, "model_dump", lambda: stealth_post.output)()
            if stealth_post.output
            else {"error": stealth_post.error}
        ),
        "performance": (
            getattr(perf_run.output, "model_dump", lambda: perf_run.output)()
            if perf_run.output
            else {"error": perf_run.error}
        ),
        "security": (
            getattr(sec_run.output, "model_dump", lambda: sec_run.output)()
            if sec_run.output
            else {"error": sec_run.error}
        ),
        "learning": (
            getattr(learning_run.output, "model_dump", lambda: learning_run.output)()
            if learning_run and learning_run.output
            else ({"skipped": True} if not learning_run else {"error": learning_run.error})
        ),
        "elapsed_ms": (site_end - site_start) * 1000,
        "sparse_extraction": sparse,
        "refinement_runs": refinement_runs,
        "high_detection_snapshots": high_snapshot_paths,
        "scheduled_cooldown": scheduled_cooldown,
    }
    return site_payload


async def run_blueprint() -> Dict[str, Any]:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("HALT: ANTHROPIC_API_KEY missing – blueprint requires live LLM")

    facade = AgentFacade()
    overall_start = time.time()
    stealth_global_pre = await facade.assess_stealth(
        "Global pre-session advisory across multiple high-detection targets"
    )

    site_results: List[Dict[str, Any]] = []
    async with BrowserSession() as session:
        try:
            await session.simulate_human(duration_s=1.0)
        except Exception:
            pass
        for idx, site in enumerate(TARGET_SITES):
            site_results.append(await _process_site(idx, site, session, facade))
        global_detection_stats = session.detection_stats()

    # Architecture agent for meta plan after collecting sites
    architect_run = await facade.architecture_plan(
        "Document orchestration of multi-site stealth browsing and adaptive extraction"
    )
    stealth_global_post = await facade.assess_stealth("Global post-session advisory")

    # Aggregate detection counts
    detection_counter: Dict[str, int] = {}
    for r in site_results:
        for sig in r.get("detection_signals", []) or []:
            detection_counter[sig] = detection_counter.get(sig, 0) + 1

    metrics = facade.metrics_snapshot()
    overall_end = time.time()
    # Build base session report (global stealth verification not aggregated per site; choose union of last site verification)
    last_verification = site_results[-1]["stealth_verification"] if site_results else {}
    combined_nav_steps: List[str] = []
    for r in site_results:
        combined_nav_steps.extend(r.get("nav_plan", []))
    report = build_report(
        metrics,
        strategies=["HumanSimulationStrategy", "DetectionMitigationStrategy"],
        issues=[],
        started_at=overall_start,
        finished_at=overall_end,
        stealth_checks=last_verification,
        navigation_plan=combined_nav_steps,
    )

    payload: Dict[str, Any] = {
        "session_report": report.to_dict(),
        "sites": site_results,
        "detection_summary": detection_counter,
        "agent_metrics": metrics,
        "detection_stats_global": global_detection_stats,
        "architecture_plan": (
            getattr(architect_run.output, "model_dump", lambda: architect_run.output)()
            if architect_run.output
            else {"error": architect_run.error}
        ),
        "stealth_global_pre": (
            getattr(stealth_global_pre.output, "model_dump", lambda: stealth_global_pre.output)()
            if stealth_global_pre.output
            else {"error": stealth_global_pre.error}
        ),
        "stealth_global_post": (
            getattr(stealth_global_post.output, "model_dump", lambda: stealth_global_post.output)()
            if stealth_global_post.output
            else {"error": stealth_global_post.error}
        ),
        "aggregate_extracted_items": sum(len(r.get("extracted", [])) for r in site_results),
    }

    out_path = OUTPUT_DIR / "blueprint_report.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return {"output_file": str(out_path), "sites": [r["label"] for r in site_results]}


def main() -> None:  # pragma: no cover
    try:
        result = asyncio.run(run_blueprint())
        print(result)
    except SystemExit as se:
        print(str(se))
        raise
    except KeyboardInterrupt:
        print("Interrupted")
    except Exception as e:
        print(f"Failure: {e}")


if __name__ == "__main__":  # pragma: no cover
    main()
