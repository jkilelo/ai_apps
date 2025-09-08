# AI-First Stealth Smart Browser Research Dossier (2025-09-06)

This dossier consolidates current (Sept 2025) public information from key projects & standards to guide backend architecture and feature roadmap for an AI-first, maximum-stealth smart browser built with Python + Playwright + Chrome, integrating modern agent standards (MCP, A2A) and structured AI frameworks (Pydantic AI).

## 1. Strategic Goals

- Stealth Supremacy: Minimize detectable automation signals (webdriver, timing, network, fingerprint surface).
- Agent-Native Architecture: First-class support for tool calling (MCP), inter-agent task delegation (A2A), structured runs (Pydantic AI), durable workflows.
- Multi-Modal Extraction: DOM, Accessibility tree, Shadow DOM, Visual salience, (future) Vision+OCR, Layout graph.
- Trust & Adaptation Loop: Page capability profiling → dynamic strategy selection → outcome evaluation → adaptive retry.
- Parallelizable Task Fabric: Multi-tab / multi-context orchestration with safe shared state & task graphs.
- Observability & Evals: Structured run logs, action traces, stealth signal score, extraction quality metrics.

## 2. Competitive / Ecosystem Scan

| Project / Spec          | Relevance                                                               | Gap / Opportunity for Us                                                                                                    |
| ----------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| browser-use             | Mature agent controlling browser; MCP integration; DOM state mgmt focus | We can go deeper on stealth fingerprint integrity, low-level anti-bot telemetry shielding, modular extraction scoring.      |
| playwright_stealth      | Script bundle masking webdriver indicators                              | Expand: dynamic fingerprint rotation, hardware entropy shaping, network-level header harmonization, timing jitter modeling. |
| Playwright Core         | Stable cross-browser automation & isolation primitives                  | Layer adaptive navigation & resilience (anti-intervention, crash recovery) on top of contexts.                              |
| Pydantic AI             | Type-safe agents, tool schemas, eval hooks                              | Use for internal action & extraction schemas + reflection loops.                                                            |
| MCP (servers ecosystem) | Tool surface expansion (filesystem, github, search, etc.)               | Offer our browser as: (1) MCP server (automation tools), (2) MCP client (leveraging external enrichment servers).           |
| A2A Protocol            | Inter-agent task routing & composition                                  | Map browser tasks into A2A task lifecycle; allow delegation (e.g., one agent for extraction, another for reasoning).        |

## 3. Core Capability Pillars

1. Stealth & Fingerprinting Layer
   - Navigator / WebGL / Canvas / Audio / Battery / Permissions spoof (already partial).
   - JA3/TLS fingerprint shaping (future via upstream proxy / mitm adapter).
   - Time domain perturbation (consistent monotonic offsets; avoid random-only anomalies).
   - Resource Loading Policy: block *known bot classifier endpoints* with dynamic allowlist.
2. Human Simulation Engine
   - Current: B-spline mouse, log-normal delays, micro-behaviors.
   - Next: Scroll context awareness (stop near semantic blocks), simulated tab switches, partial read-path heatmap generation.
3. Extraction Intelligence
   - Present: DOM, Visual prominence, Accessibility, Shadow DOM.
   - Next Iterations:
     - Heuristic scoring fusion → unified ElementConfidence (score components: visibility, interactivity, semantic role, spatial prominence).
     - Layout graph (parent-child-sibling roles) + action affordance classification.
     - Optional lightweight vision embedding (CLIP/Tiny-VLM) for button/icon intent disambiguation.
4. Resilience & Recovery
   - Existing: Health check + reload.
   - Planned: Tiered recovery (soft reload → context recreate → browser relaunch) with causal tagging (crash, nav hang, script stall).
5. Agent Interface Surfaces
   - Python API (present)
   - MCP Server Mode: expose tools: navigate, extract, click(selector|semantic), type, screenshot, evaluate_js, get_dom_snapshot.
   - A2A Adapter: translate inbound A2A task → internal action plan; emit progress events; support cancellation.
6. Observability & Evals
   - Structured JSON traces (actions, timings, stealth mutations, detection signals).
   - Metrics: mean extraction latency, element recall vs. heuristic baseline, CAPTCHA encounter rate, recovery MTTR.
   - Pydantic AI eval harness for regression on target benchmark pages.

## 4. Proposed Incremental Backend Architecture

Layered modules (some inferred directories to add):

```text
/stealth          # fingerprint & script injectors (current)
/human            # movement, delays, behavior modeling (current in HumanSimulator -> refactor)
/extraction       # strategy interfaces + fusion scorer + future ML hooks
/agent            # orchestration, task graphs, reflection, retry logic
/protocols/mcp    # MCP server wrapper + tool registration
/protocols/a2a    # A2A client/server bridge (task encode/decode)
/observability    # logging, metrics, traces, eval hooks, run IDs
/models           # Pydantic models (Element, ActionPlan, MetricsReport, ToolSchemas)
```

## 5. Key Data Models (Target State)

- Element (existing `ElementData`) → extend: `prominence_score`, `semantic_labels: List[str]`, `actions: List[ActionAffordance]`.
- ActionAffordance: type (click|input|navigate|submit|expand), confidence, selector set.
- PageSnapshot: url, title, timestamp, elements[], raw_dom_hash, scroll_pos.
- StealthSignalProfile: flags applied, fingerprint hash, entropy metrics.
- RunTrace: run_id, steps[], metrics.
- Metrics: extraction_time, elements_count, dom_coverage_ratio, recoveries, captcha_detected.

## 6. MCP Integration Plan

Expose the browser as an MCP server (tools):

- tool: navigate(url: string, wait: enum) -> { success, status_code, final_url }
- tool: extract(mode: enum[strategy|all]) -> PageSnapshot
- tool: click(query: union[css, xpath, semantic]) -> { success }
- tool: type(query, text, submit: bool=False) -> { success }
- tool: screenshot(full: bool=True) -> { path | b64 }
- tool: eval(js_code) -> { result_json }
- tool: metrics() -> { latest_metrics }

Optional semantic resolution: internal fuzzy match across element corpus.

## 7. A2A Interop Concepts

Mapping:

- A2A Task.types: BROWSER_NAVIGATE, BROWSER_INTERACT, BROWSER_EXTRACT
- Lifecycle: accept → plan (derive ActionGraph) → execute steps with event streaming (progress, partial snapshot) → complete with artifact references (screenshots, extracted JSON).
- Security: sandbox allowed origins (policy), rate limit external delegation.

## 8. Pydantic AI Usage

- Wrap each browser operation as a tool with validated inputs/outputs.
- Compose an Agent for: "Goal-Oriented Browsing" using a loop: interpret goal → plan (list[BrowserAction]) → execute → reflect (compare expected vs. actual state) → continue or finish.
- Introduce evaluation suites: known pages (login forms, article pages, e-commerce product pages) produce deterministic metric baselines.

## 9. Near-Term Enhancement Backlog (Backend)

Priority P1 (next iteration):

1. Fusion scoring + unified result serializer (extend `ElementData`).
2. Stealth entropy profiler (collect which spoof modules active + export profile hash).
3. Basic MCP server scaffold (stdio) exposing navigate + extract.
4. Resilience tiered recovery (context recreate path).
5. Structured trace logger (JSONL per run).

Priority P2:

1. Semantic element resolution (keyword → candidate set ranked by text/role/class similarity + Levenshtein).
2. Vision optional classification hook behind feature flag.
3. A2A adapter skeleton (task ingestion + dispatch).
4. Pydantic AI integration (ActionPlan model + agent loop prototype).
5. Metrics aggregator + simple eval harness.

Priority P3:

1. Network fingerprint shaping via external proxy integration interface.
2. Workflow parallel task fabric (multi-context pool manager).
3. Durable session resume (persist snapshots + replay plan).
4. Active CAPTCHA mitigation plugin interface.

## 10. Risks & Mitigations

- Fingerprint Drift / Inconsistency → Maintain deterministic seed per session; apply noise deterministically.
- Detection by Timing Correlation → Bound random jitter within human plausible distribution quantiles.
- Strategy Explosion Complexity → Pluggable registry with capability introspection & weighted selection.
- Tool Surface Creep → Versioned protocol schema; deprecations via capability negotiation.
- Resource Leaks (async tasks) → Central task supervisor; health watchdog enumerating pending tasks.

## 11. Suggested File Additions (Next Step)

- `models/element_extensions.py`
- `extraction/fusion.py`
- `protocols/mcp/server.py`
- `observability/trace.py`
- `agent/action_plan.py`

(Implementation not yet added—awaiting confirmation to proceed.)

## 12. Metrics & Evaluation Framework Draft

- Element Recall Proxy: (#interactive elements discovered)/(#interactive in baseline manual map).
- Latency: nav_time, extraction_time, first_click_time.
- Stability: crash_rate, recovery_success_rate.
- Stealth Score (heuristic): penalties for presence of webdriver flag, missing plugins, unnatural hardware ratios, canvas hash stability across sessions.
- Export Format: JSONL lines keyed by run_id.

## 13. Minimal MCP Server Sketch (Concept)

```python
# Pseudo-outline
class MCPBrowserServer:
    def __init__(self, browser): ...
    async def handle_request(self, msg):
        if msg.tool == 'navigate':
            return await browser.navigate(msg.params['url'])
        if msg.tool == 'extract':
            return serialize(await browser.extract_elements())
        # ... other tools
```

Transport: start with stdio (compatible with Claude Desktop), JSON-RPC framing.

## 14. Immediate Recommendations

1. Approve creation of new modular directories (see §11) and migrate relevant logic out of monolith progressively.
2. Implement fusion scoring & extended serialization (safe incremental change).
3. Stand up skeleton MCP server (even if wrapping current monolith) to validate integration.
4. Add trace logger capturing each action + timestamp + outcome.

## 15. Appendix: Source Highlights Referenced

- `playwright_stealth`: Basic stealth APIs (we supersede with richer, dynamic injection model already present).
- `browser-use`: MCP integration pattern, multi-agent vision, roadmap priorities (DOM extraction depth, parallelization) aligning with our backlog.
- `Pydantic AI`: Strong typed agents, dependency injection, evals; ideal for formalizing ActionPlan & Tool IO.
- `A2A`: Defines inter-agent semantics; we map our capabilities into task types & streaming events.
- `Playwright`: Multi-context isolation & shadow DOM piercing—foundation for parallel & deep extraction.

---

Generated: 2025-09-06
