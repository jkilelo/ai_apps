# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and adheres to Semantic Versioning.

## [0.1.0a1] - 2025-09-06

### Added

- Core CLI with hard HALT policy when ANTHROPIC_API_KEY missing (unless --dry-run).
- Multi-agent facade (stealth, navigation, performance) using pydantic-ai with resilience (retry, timeout, circuit breaker).
- Stealth fingerprint strategies (navigator, canvas, timezone, webgl, audio, font) with randomized ordering and verification hook.
- Human interaction simulation (basic cursor + scroll) framework.
- Action DSL (NAV/CLICK/TYPE/WAIT/EXTRACT) + parser & executor with retry logic.
- Structured extraction engine (CSS selectors -> pydantic models).
- Navigation executor integrating planned steps & reporting.
- JSONL event logging with environment override.
- Session report aggregation (strategies, metrics, navigation plan, stealth checks).
- Dry-run mode (no API usage) with deterministic placeholder outputs.
- .env auto-loading plus pytest safeguard for HALT enforcement.
- MCP server stub (list_tools, call_tool for navigate & extract) for future protocol expansion.
- Roadmap task registry with meta tests enforcing test coverage for implemented tasks.
- Headless=False enforced globally to ensure real browser visibility.

### Changed

- Upgraded packaging metadata for alpha release (version 0.1.0a1, classifiers).

### Notes

This is an alpha build intended for early adopters and contributors. Expect breaking changes before 0.1.0 stable.
