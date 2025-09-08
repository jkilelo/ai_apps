## AI Stealth Browser (Alpha)

AI-first stealth automation framework with resilient multi-agent orchestration and layered fingerprint mitigation.

### Core Capabilities

- Pydantic v2 agent layer (stealth, navigation, security, performance, learning, architect) via unified facade.
- Resilience: retry + timeout + circuit breaker (with transition events).
- Fingerprint defenses: navigator, canvas noise, timezone masking, WebGL vendor spoof, AudioContext noise, font masking.
- Human interaction simulation (cursor path + occasional scroll) with easing and noise.
- Strategy randomization (disable with `FIXED_STEALTH_ORDER=1`).
- Structured JSONL event logging (`event_traces.jsonl`).
- Session reporting aggregator.
- CLI with `--version`.

### Install (editable)

```powershell
pip install -e .
```

### Environment Variables

| Name                          | Purpose                                                                                      |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| ANTHROPIC_API_KEY             | Required for live agent runs (HALT if missing). Loaded automatically from `.env` if present. |
| FIXED_STEALTH_ORDER=1         | Preserve static strategy order (no shuffle).                                                 |
| (removed) AI_STEALTH_DRY_RUN  | Dry-run mode eliminated; framework always requires live key.                                 |
| AI_STEALTH_EVENT_LOG=path     | Override event log path (default `event_traces.jsonl`).                                      |
| AI_STEALTH_NAV_MAX_STEPS      | Limit executed navigation steps (default 5).                                                 |
| AI_STEALTH_HUMAN_SIM=0/1      | Enable per-step human pause simulation (default 1).                                          |
| AI_STEALTH_VERIFY=0/1         | Enable post-navigation stealth verification (default 1).                                     |
| AI_STEALTH_HUMAN_PAUSE_MIN_MS | Lower bound for pause jitter between steps (default 150).                                    |
| AI_STEALTH_HUMAN_PAUSE_MAX_MS | Upper bound for pause jitter between steps (default 400).                                    |

`.env` auto-loading: A `.env` file in the project root is read automatically on CLI startup (using `python-dotenv`).

### CLI Usage

Live (requires key):

```powershell
ai-stealth-browser "Explore product catalog"
```

Dry run (no external API calls):



Version:

```powershell
ai-stealth-browser --version goal-placeholder
```

Preflight (environment diagnostics only, no agent runs):

```powershell
ai-stealth-browser --preflight goal-placeholder
```

Output: JSON containing `session_report` + agent outputs. Events appended to `event_traces.jsonl` (override with `AI_STEALTH_EVENT_LOG`).

Preflight output includes:

- Python & platform
- Playwright availability
- Presence of API key (after `.env` load)
- Count of bundled stealth scripts
- Event log override flag

New fields:

- `navigation_plan`: ordered list of navigation steps (empty if agent produced none).
- `stealth_checks`: dictionary of post-init browser stealth verification booleans.

### Testing

```powershell
pytest -q
```

For future live (real browser + LLM) tests you can designate:

```python
import pytest

@pytest.mark.live
async def test_live_browser_flow():
	...  # requires ANTHROPIC_API_KEY and playwright browsers installed
```

Then run normal suite excluding live:

```powershell
pytest -q -m "not live"
```

Or only live tests:

```powershell
pytest -q -m live
```

Add a `pytest.ini` marker declaration later to silence warnings:

```ini
[pytest]
markers =
	live: tests requiring real external services (excluded by default)
```

### Alpha Usage Example



Sample trimmed output:

```json
{ "session_report": { "agent_stats": [ { "agent": "stealth", "runs": 1 } ] } }
```

### Circuit Breaker Events

`circuit_transition` events emitted on state changes (`open`, `half-open` via auto transition, `closed`).

### Development Roadmap (Post-Alpha)

- Client Hints & MediaDevices spoofing.
- Keystroke & dwell-time simulation.
- Adaptive strategy selection heuristics.
- Rich metrics endpoint / OpenTelemetry exporter.
- Multi-browser backend abstraction.
- Navigation executor richer step taxonomy (form fill, click selectors, file upload).
- RuntimeConfig surfaced via `--preflight` for transparency.

### License

MIT

### HALT Policy

Execution without a live `ANTHROPIC_API_KEY` raises an immediate SystemExit (HALT). No fallback, no dry-run path.

## Alpha 0.1.0a1 Notes

- See `CHANGELOG.md` for detailed list.
- New: Action DSL `--plan-file` execution, structured extraction engine, MCP server stub.
- Serialization hardened to avoid pydantic object TypeErrors.

### Action Plan Example

Create `example.plan`:

```text
NAV https://example.com
WAIT 1.0
EXTRACT title css=h1
```

Run with:

```powershell
ai-stealth-browser "Browse example" --plan-file example.plan
```

### MCP Stub

A minimal experimental stub lives in `core/mcp_server.py` exposing:

- `list_tools()`
- `call_tool()` for `navigate` and `extract`

Future: full MCP protocol serve mode and external tool orchestration.

---
