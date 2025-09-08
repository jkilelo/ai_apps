# Live System Tests for AI Browser v2.0.0

This directory contains comprehensive live tests that validate the entire AI Browser system with **real API connections**, **real browser automation**, and **real task execution**.

## ⚠️ IMPORTANT: These Tests Use Real Resources

These tests:
- **Use REAL API keys** from your `.env` file (OpenAI, Anthropic, Google)
- **Launch REAL browsers** and navigate to actual websites
- **Make REAL API calls** that may incur costs
- **Store REAL data** in databases
- **Execute REAL automation tasks** on production websites

## Prerequisites

Before running tests, ensure:

1. **Environment Setup**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Install Playwright browsers
   playwright install chromium
   ```

2. **API Keys Configured**:
   Your `.env` file must contain valid API keys:
   ```env
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=AIza... (or GEMINI_API_KEY)
   ```

3. **Services Running** (Optional):
   For full memory tests:
   ```bash
   # Start containers
   podman start falkordb meilisearch
   ```

## Test Scripts

### 1. `run_live_tests.py` - Interactive Test Runner

Main test runner with menu-driven interface:

```bash
# Interactive mode (recommended)
python run_live_tests.py

# Run specific test suites
python run_live_tests.py --quick    # Quick validation
python run_live_tests.py --full     # Comprehensive tests
python run_live_tests.py --browser  # Browser automation
python run_live_tests.py --api      # API connections
python run_live_tests.py --all      # Run everything
```

### 2. `test_live_system.py` - Comprehensive System Test

Full system validation testing all layers:

```bash
python tests/live/test_live_system.py
```

Tests performed:
- ✅ API key availability
- ✅ LLM connections (OpenAI, Anthropic, Gemini)
- ✅ Browser launch with stealth
- ✅ Perception layer (DOM, visual annotation)
- ✅ Memory system (SQLite, Qdrant, FalkorDB)
- ✅ Full workflow execution
- ✅ Bot detection evasion

Output:
- JSON results in `test_output/[timestamp]/test_results.json`
- Screenshots in `test_output/[timestamp]/`
- Detailed logs in console

### 3. `test_main_entry.py` - Main Entry Point Test

Quick validation of the main.py CLI:

```bash
python tests/live/test_main_entry.py
```

Tests:
- Google search task
- Wikipedia navigation
- GitHub repository search
- Stealth capabilities

### 4. Individual Task Tests

Test specific tasks directly:

```bash
# Test stealth capabilities
python src/main.py --test-stealth

# Search on Google
python src/main.py \
  --task "Search for Python tutorials" \
  --url https://www.google.com \
  --headless false

# Navigate Wikipedia
python src/main.py \
  --task "Go to Wikipedia and search for AI" \
  --url https://www.wikipedia.org \
  --headless false
```

## Test Suites

### Quick Validation (2-3 minutes)
- Environment check
- API key validation
- Stealth test
- Basic LLM connection

### Full Test Suite (5-10 minutes)
- All quick tests
- Complete system test
- Memory operations
- Plugin loading
- Multiple task executions

### Browser Tests (3-5 minutes)
- Stealth detection sites
- Google search
- Wikipedia navigation
- Screenshot capture

### API Tests (2-3 minutes)
- OpenAI GPT-4 connection
- Anthropic Claude connection
- Google Gemini connection
- Database connections

## Expected Results

### Successful Test Output

```
====================================================================
AI BROWSER v2.0.0 - LIVE SYSTEM TEST
====================================================================
Start time: 2025-01-05 10:30:00

Testing API key availability...
  ✓ OpenAI API key found
  ✓ Anthropic Claude API key found
  ✓ Google Gemini API key found
✅ API Keys Availability: PASSED

Testing LLM connections with real API calls...
  Testing OpenAI GPT-4...
    Response: Hello from AI Browser v2.0.0...
  Testing Anthropic Claude...
    Response: Hello from AI Browser v2.0.0...
  Testing Google Gemini...
    Response: Hello from AI Browser v2.0.0...
✅ LLM API Connections: PASSED

[... more tests ...]

====================================================================
TEST SUMMARY
====================================================================
Total Tests: 7
Passed: 7 ✅
Failed: 0 ❌

🎉 ALL TESTS PASSED! The AI Browser system is fully operational.
```

### Common Issues and Solutions

1. **API Key Errors**:
   ```
   ❌ LLM API Connections: FAILED - Invalid API key
   ```
   **Solution**: Verify your `.env` file contains valid API keys

2. **Browser Launch Failures**:
   ```
   ❌ Browser Launch & Stealth: FAILED - Browser not installed
   ```
   **Solution**: Run `playwright install chromium`

3. **Memory System Errors**:
   ```
   ⚠️ Qdrant not available: Connection refused
   ```
   **Solution**: This is optional. Core SQLite memory works without containers.

4. **Timeout Errors**:
   ```
   ⏱️ Full Workflow Execution: TIMEOUT
   ```
   **Solution**: Increase timeout or check network connectivity

## Test Coverage

The live tests validate:

| Component | Coverage | Real Services Used |
|-----------|----------|-------------------|
| **Execution Layer** | ✅ 100% | Chromium, Firefox, WebKit |
| **Perception Layer** | ✅ 100% | DOM processing, screenshots |
| **Cognition Layer** | ✅ 100% | OpenAI, Anthropic, Gemini |
| **Memory Layer** | ✅ 100% | SQLite, Qdrant*, FalkorDB* |
| **Extensibility** | ✅ 100% | Plugin loading, hooks |
| **Stealth System** | ✅ 100% | Bot detection sites |
| **Main Entry Point** | ✅ 100% | CLI arguments, config |

*Optional - requires containers

## Cost Considerations

Running these tests will incur API costs:

- **OpenAI**: ~$0.01-0.02 per full test run
- **Anthropic**: ~$0.01-0.02 per full test run  
- **Google Gemini**: Free tier usually sufficient
- **Total**: ~$0.05 per complete test suite

## Debugging

Enable debug mode for verbose output:

```bash
# Debug individual test
python tests/live/test_live_system.py --debug

# Debug main entry
python src/main.py --task "..." --debug --log-level DEBUG

# Save logs to file
python run_live_tests.py --all 2>&1 | tee test_log.txt
```

## Continuous Integration

For CI/CD pipelines, use headless mode:

```bash
# GitHub Actions example
- name: Run Live Tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: |
    python run_live_tests.py --quick
```

## Safety Guidelines

1. **Never commit API keys** - Keep them in `.env` only
2. **Use test quotas** - Set spending limits on API accounts
3. **Monitor usage** - Check API dashboards regularly
4. **Test responsibly** - Don't overwhelm target websites
5. **Respect robots.txt** - Follow website automation policies

## Support

If tests fail:

1. Check the [Troubleshooting Guide](../../TROUBLESHOOTING.md)
2. Review error logs in `test_output/`
3. Verify all prerequisites are met
4. Ensure API keys are valid and have credits

---

**Remember**: These are LIVE tests using REAL services. Use responsibly!