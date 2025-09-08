# 🔧 Troubleshooting Guide - AI Browser

## Quick Diagnostic Commands

```bash
# Check environment setup
python -c "import sys; print(f'Python: {sys.version}')"
uv --version
uvx ruff --version

# Test browser installation
uv run python -c "from playwright.async_api import async_playwright; print('Playwright OK')"
uv run playwright install --help

# Verify LLM keys
python -c "import os; print('OpenAI:', 'OPENAI_API_KEY' in os.environ)"
python -c "import os; print('Anthropic:', 'ANTHROPIC_API_KEY' in os.environ)"
python -c "import os; print('Google:', 'GOOGLE_API_KEY' in os.environ)"

# Check memory services
docker ps | grep -E "qdrant|falkordb"
curl -s http://localhost:6333/health | jq .
```

## 🌐 Browser Issues

### TimeoutError: Timeout 30000ms exceeded

**Symptoms:**
```python
playwright._impl._api_types.TimeoutError: Timeout 30000ms exceeded
```

**Causes & Solutions:**

1. **Selector not found**
   ```python
   # Bad: Brittle selector
   await page.click("div.content > span:nth-child(3)")
   
   # Good: Robust selector
   await page.get_by_role("button", name="Submit").click()
   ```

2. **Page not loaded**
   ```python
   # Add explicit wait
   await page.goto(url)
   await page.wait_for_load_state("networkidle")
   await page.wait_for_selector(".main-content", state="visible")
   ```

3. **JavaScript-rendered content**
   ```python
   # Wait for dynamic content
   await page.wait_for_function(
       "document.querySelectorAll('.item').length > 0"
   )
   ```

### Browser Detection Blocked

**Symptoms:**
- "Access Denied" pages
- Cloudflare challenges
- "Unusual traffic detected"

**Solutions:**

1. **Enable stealth plugins**
   ```python
   # Check stealth status
   python -c "from src.execution.stealth_manager import StealthManager; sm = StealthManager(); print(sm.list_plugins())"
   
   # Test stealth
   uv run python src/main.py --test-stealth
   ```

2. **Rotate user agents**
   ```python
   user_agents = [
       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
   ]
   ```

3. **Add delays between actions**
   ```python
   import random
   import asyncio
   
   # Human-like delays
   await asyncio.sleep(random.uniform(0.5, 2.0))
   ```

### Browser Crash/Hang

**Symptoms:**
- Browser process terminated
- Unresponsive browser
- Memory errors

**Solutions:**

1. **Increase resources**
   ```python
   browser = await playwright.chromium.launch(
       args=[
           '--disable-dev-shm-usage',
           '--no-sandbox',
           '--disable-gpu',
           '--disable-web-security'
       ]
   )
   ```

2. **Enable crash dumps**
   ```bash
   export PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers
   export DEBUG=pw:api
   ```

3. **Use browser contexts**
   ```python
   # Isolate each task
   context = await browser.new_context()
   page = await context.new_page()
   # ... do work ...
   await context.close()  # Cleanup
   ```

## 🤖 LLM Issues

### Rate Limit Errors

**Symptoms:**
```
openai.RateLimitError: Rate limit reached for gpt-4
anthropic.RateLimitError: Request limit exceeded
```

**Solutions:**

1. **Implement exponential backoff**
   ```python
   from tenacity import retry, wait_exponential, stop_after_attempt
   
   @retry(
       wait=wait_exponential(multiplier=1, min=4, max=60),
       stop=stop_after_attempt(5)
   )
   async def call_llm():
       return await llm.generate(prompt)
   ```

2. **Switch providers on failure**
   ```python
   providers = ["openai", "anthropic", "google"]
   for provider in providers:
       try:
           return await call_provider(provider, prompt)
       except RateLimitError:
           continue
   ```

3. **Track usage**
   ```python
   # Monitor token usage
   tokens_used = response.usage.total_tokens
   if tokens_used > DAILY_LIMIT * 0.8:
       logger.warning(f"Approaching token limit: {tokens_used}/{DAILY_LIMIT}")
   ```

### Token Limit Exceeded

**Symptoms:**
```
This model's maximum context length is 8192 tokens
```

**Solutions:**

1. **Compress prompts**
   ```python
   def compress_dom(dom_text: str, max_length: int = 6000) -> str:
       # Remove comments, excessive whitespace
       compressed = re.sub(r'<!--.*?-->', '', dom_text)
       compressed = re.sub(r'\s+', ' ', compressed)
       
       # Truncate if needed
       if len(compressed) > max_length:
           compressed = compressed[:max_length] + "..."
       
       return compressed
   ```

2. **Use summarization**
   ```python
   # Summarize long content first
   summary = await llm.summarize(long_content, max_tokens=500)
   final_response = await llm.analyze(summary)
   ```

### Hallucinations/Invalid Actions

**Symptoms:**
- LLM suggests non-existent selectors
- Invalid action sequences
- Contradictory responses

**Solutions:**

1. **Validate outputs**
   ```python
   async def validate_action(action: Dict, page) -> bool:
       selector = action.get("selector")
       
       # Check if element exists
       element = await page.query_selector(selector)
       if not element:
           logger.warning(f"Invalid selector: {selector}")
           return False
       
       # Check if action is possible
       is_visible = await element.is_visible()
       is_enabled = await element.is_enabled()
       
       return is_visible and is_enabled
   ```

2. **Use structured outputs**
   ```python
   from pydantic import BaseModel, validator
   
   class AgentAction(BaseModel):
       action: Literal["click", "type", "select", "wait"]
       selector: str
       value: Optional[str] = None
       
       @validator('selector')
       def validate_selector(cls, v):
           if not v or v.strip() == "":
               raise ValueError("Selector cannot be empty")
           return v
   ```

## 💾 Memory/Database Issues

### Connection Failed

**Symptoms:**
```
ConnectionRefusedError: [Errno 111] Connection refused
qdrant_client.exceptions.UnexpectedResponse: Connection error
```

**Solutions:**

1. **Check services**
   ```bash
   # Start services
   docker-compose up -d
   
   # Check health
   curl http://localhost:6333/health  # Qdrant
   redis-cli ping  # FalkorDB
   ```

2. **Fallback to SQLite**
   ```python
   try:
       vector_store = QdrantClient("localhost:6333")
   except ConnectionError:
       logger.warning("Qdrant unavailable, using SQLite fallback")
       vector_store = SQLiteVectorStore("./data/vectors.db")
   ```

### Slow Queries

**Symptoms:**
- Query timeout
- High latency
- CPU spike

**Solutions:**

1. **Add indexes**
   ```sql
   CREATE INDEX idx_timestamp ON actions(timestamp);
   CREATE INDEX idx_url ON page_states(url);
   CREATE INDEX idx_task_id ON conversations(task_id);
   ```

2. **Implement caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   async def get_cached_embeddings(text: str):
       return await generate_embeddings(text)
   ```

## 🔌 Plugin Issues

### Plugin Failed to Load

**Symptoms:**
```
ImportError: cannot import name 'IStealthPlugin'
ModuleNotFoundError: No module named 'plugin_name'
```

**Solutions:**

1. **Check plugin structure**
   ```python
   # plugins/my_plugin/__init__.py
   from .main import MyPlugin
   
   __all__ = ["MyPlugin"]
   ```

2. **Verify interface**
   ```python
   class MyPlugin(IStealthPlugin):
       async def apply(self, context):
           # Implementation
           pass
       
       def get_metadata(self):
           return {"name": "my_plugin", "version": "1.0.0"}
   ```

### Plugin Conflicts

**Symptoms:**
- Conflicting browser modifications
- Race conditions
- Unexpected behavior

**Solutions:**

1. **Set plugin priorities**
   ```yaml
   # plugins/config.yaml
   plugins:
     webdriver_fix:
       priority: 1  # Runs first
     canvas_noise:
       priority: 2  # Runs second
   ```

2. **Use plugin isolation**
   ```python
   # Run plugins in separate contexts
   for plugin in plugins:
       try:
           await plugin.apply(context)
       except Exception as e:
           logger.error(f"Plugin {plugin.name} failed: {e}")
           # Continue with other plugins
   ```

## 🐛 Development Issues

### Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
ImportError: attempted relative import with no known parent package
```

**Solutions:**

1. **Fix Python path**
   ```bash
   # Add to .env or shell
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Or in code
   import sys
   sys.path.append(str(Path(__file__).parent.parent))
   ```

2. **Use absolute imports**
   ```python
   # Bad
   from ..execution import BrowserManager
   
   # Good
   from src.execution import BrowserManager
   ```

### Type Checking Errors

**Symptoms:**
```
error: Incompatible types in assignment
error: Missing type parameters for generic type
```

**Solutions:**

1. **Add type stubs**
   ```bash
   uv add --dev types-aiofiles types-redis types-requests
   ```

2. **Use type ignores sparingly**
   ```python
   # Only when necessary
   result = await some_untyped_function()  # type: ignore[no-untyped-call]
   ```

## 📊 Performance Issues

### Slow Browser Operations

**Solutions:**

1. **Profile performance**
   ```python
   import time
   
   start = time.perf_counter()
   await page.goto(url)
   elapsed = time.perf_counter() - start
   
   if elapsed > 5:
       logger.warning(f"Slow page load: {elapsed:.2f}s")
   ```

2. **Optimize selectors**
   ```python
   # Slow: Complex CSS
   await page.click("body > div:nth-child(2) > form > button")
   
   # Fast: ID or data attribute
   await page.click("#submit-btn")
   await page.click("[data-test='submit']")
   ```

3. **Disable unnecessary features**
   ```python
   context = await browser.new_context(
       bypass_csp=True,
       ignore_https_errors=True,
       extra_http_headers={"Accept-Language": "en-US"},
       # Disable images for speed
       route=lambda route: route.abort() if route.request.resource_type == "image" else route.continue_()
   )
   ```

### High Memory Usage

**Solutions:**

1. **Close resources properly**
   ```python
   try:
       page = await browser.new_page()
       # ... work ...
   finally:
       await page.close()
   ```

2. **Limit concurrent operations**
   ```python
   from asyncio import Semaphore
   
   semaphore = Semaphore(3)  # Max 3 concurrent browsers
   
   async def process_with_limit(url):
       async with semaphore:
           return await process_url(url)
   ```

## 🆘 Emergency Recovery

### Complete Reset

```bash
# 1. Stop all services
docker-compose down
pkill -f playwright
pkill -f chromium

# 2. Clear caches
rm -rf ~/.cache/ms-playwright
rm -rf ./data/*
rm -rf ./logs/*

# 3. Reinstall
uv sync --reinstall
uv run playwright install chromium

# 4. Restart services
docker-compose up -d

# 5. Test
uv run python src/main.py --test
```

### Debug Mode

```python
# Enable maximum debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Playwright debug
DEBUG=pw:api uv run python src/main.py

# Save debug artifacts
PWDEBUG=1 uv run python src/main.py
```

## 📞 Getting Help

### Collect Diagnostic Info

```bash
# Create diagnostic bundle
python scripts/collect_diagnostics.py

# This collects:
# - System info
# - Package versions  
# - Recent logs
# - Configuration
# - Test results
```

### Report Issues

Include in bug reports:
1. Error message and full traceback
2. Steps to reproduce
3. Environment (OS, Python version, browser)
4. Diagnostic bundle
5. Relevant code snippet

### Community Resources

- GitHub Issues: Report bugs and feature requests
- Discord: Real-time help and discussions
- Stack Overflow: Tag with `ai-browser`
- Documentation: Check latest docs for updates

---
*Last Updated: 2025-09-05 | Version: 1.0.0*