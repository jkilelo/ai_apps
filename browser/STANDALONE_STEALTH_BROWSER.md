# Standalone Stealth Browser Service

## Overview

The Standalone Stealth Browser Service is a comprehensive, production-ready browser automation solution that provides maximum anti-detection capabilities while being completely independent of any specific use case. It can be used by any application - LLMs, automation tools, testing frameworks, or manual scripts.

## Key Features

### 🛡️ Maximum Stealth Capabilities
- **WebDriver Detection Bypass**: Removes all traces of automation
- **Chrome Runtime Spoofing**: Mimics real Chrome browser
- **Canvas Fingerprinting Protection**: Adds noise to canvas operations
- **WebGL Fingerprinting**: Spoofs WebGL parameters
- **Audio Context Protection**: Prevents audio fingerprinting
- **WebRTC Leak Prevention**: Blocks IP leaks
- **CDP Detection Bypass**: Evades Chrome DevTools Protocol detection
- **Battery API Spoofing**: Returns realistic battery values
- **Hardware Spoofing**: Consistent hardware fingerprint

### 🤖 Human Behavior Simulation
- **Natural Typing**: Variable delays between keystrokes
- **Bezier Mouse Movement**: Human-like cursor paths
- **Smart Scrolling**: Natural reading patterns
- **Random Delays**: Realistic wait times
- **Micro-behaviors**: Small random movements

### 🔧 Flexible Architecture
- **Standalone Operation**: No dependencies on specific use cases
- **Multiple Interfaces**: Library, REST API, WebSocket
- **Session Management**: Persist state across restarts
- **Multi-browser Support**: Chromium, Firefox, WebKit
- **Proxy Support**: Built-in proxy rotation
- **Resource Blocking**: Optimize performance

### 🎯 Advanced Bypass Techniques
- **Cloudflare Bypass**: Handle CF challenges
- **DataDome Bypass**: Evade DataDome detection
- **PerimeterX Bypass**: Handle PX challenges
- **Akamai Bot Manager**: Bypass Akamai protection
- **Kasada Protection**: Handle Kasada challenges
- **Shape Security**: Evade Shape detection

## Installation

```bash
# Install required packages
pip install playwright aiohttp websockets

# Install Playwright browsers
playwright install chromium

# Optional: Install for all browsers
playwright install
```

## Quick Start

### As a Library

```python
from standalone_stealth_browser import StealthBrowserService, BrowserConfig

async def main():
    # Create browser with default config
    browser = StealthBrowserService()
    
    # Start the service
    await browser.start()
    
    # Get a page and navigate
    page = await browser.get_page("https://example.com")
    
    # Interact with the page
    await browser.click(page, "button#submit")
    await browser.type(page, "input#search", "query")
    
    # Take screenshot
    screenshot = await browser.screenshot(page)
    
    # Stop the service
    await browser.stop()

# Run
import asyncio
asyncio.run(main())
```

### As an API Server

```bash
# Start the server
python standalone_stealth_browser.py --server --port 9222

# Use via HTTP API
curl http://localhost:9222/api/navigate -d '{"url": "https://example.com"}'
curl http://localhost:9222/api/screenshot -d '{"page_id": "..."}'
```

## Configuration

### Basic Configuration

```python
config = BrowserConfig(
    headless=False,                    # Show browser window
    browser_type="chromium",           # chromium, firefox, webkit
    stealth_level="maximum",           # basic, enhanced, maximum, ultimate
    enable_human_simulation=True,      # Simulate human behavior
    viewport_width=1920,
    viewport_height=1080,
)
```

### Advanced Configuration

```python
config = BrowserConfig(
    # Stealth settings
    hide_webdriver=True,
    spoof_canvas_fingerprint=True,
    spoof_webgl=True,
    prevent_webrtc_leak=True,
    disable_cdp_detection=True,
    
    # Bypass settings
    bypass_cloudflare=True,
    bypass_datadome=True,
    bypass_perimeter_x=True,
    
    # Human behavior
    human_typing_speed=(50, 200),      # ms between keystrokes
    human_mouse_speed=1.0,
    random_delays=True,
    delay_range=(100, 2000),           # ms
    
    # Proxy
    proxy={
        "server": "http://proxy.example.com:8080",
        "username": "user",
        "password": "pass"
    },
    
    # Performance
    block_images=True,                 # Block image loading
    block_media=True,                  # Block video/audio
    timeout=60000,                     # Page timeout
    navigation_timeout=30000,          # Navigation timeout
)
```

## API Reference

### Core Methods

#### `start() -> bool`
Start the browser service.

```python
success = await browser.start()
```

#### `stop() -> bool`
Stop the browser service and cleanup resources.

```python
await browser.stop()
```

#### `get_page(url: Optional[str], page_id: Optional[str]) -> Page`
Get a page instance. Creates new page if needed.

```python
# Create new page and navigate
page = await browser.get_page("https://example.com")

# Get existing page
page = await browser.get_page(page_id="existing_page_id")
```

#### `navigate(page: Page, url: str, wait_until: str) -> bool`
Navigate to a URL with stealth behavior.

```python
success = await browser.navigate(page, "https://example.com", "domcontentloaded")
```

#### `click(page: Page, selector: str) -> bool`
Click an element with human-like behavior.

```python
await browser.click(page, "button#submit")
```

#### `type(page: Page, selector: str, text: str) -> bool`
Type text with human-like behavior.

```python
await browser.type(page, "input#email", "user@example.com")
```

#### `screenshot(page: Page, path: Optional[str]) -> Union[bytes, bool]`
Take a screenshot.

```python
# Save to file
await browser.screenshot(page, "screenshot.png")

# Get bytes
image_bytes = await browser.screenshot(page)
```

#### `evaluate(page: Page, script: str) -> Any`
Evaluate JavaScript in the page.

```python
title = await browser.evaluate(page, "document.title")
```

#### `wait_for_selector(page: Page, selector: str, timeout: Optional[int]) -> bool`
Wait for element to appear.

```python
found = await browser.wait_for_selector(page, ".loading-complete", timeout=5000)
```

#### `get_cookies(page: Page) -> List[Dict]`
Get cookies from page.

```python
cookies = await browser.get_cookies(page)
```

#### `set_cookies(page: Page, cookies: List[Dict]) -> bool`
Set cookies for page.

```python
await browser.set_cookies(page, cookies)
```

## REST API Endpoints

When running as a server, the following endpoints are available:

### `GET /api/status`
Get browser service status.

```bash
curl http://localhost:9222/api/status
```

### `POST /api/navigate`
Navigate to a URL.

```bash
curl -X POST http://localhost:9222/api/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### `POST /api/click`
Click an element.

```bash
curl -X POST http://localhost:9222/api/click \
  -H "Content-Type: application/json" \
  -d '{"page_id": "...", "selector": "button"}'
```

### `POST /api/type`
Type text into an element.

```bash
curl -X POST http://localhost:9222/api/type \
  -H "Content-Type: application/json" \
  -d '{"page_id": "...", "selector": "input", "text": "hello"}'
```

### `POST /api/screenshot`
Take a screenshot.

```bash
curl -X POST http://localhost:9222/api/screenshot \
  -H "Content-Type: application/json" \
  -d '{"page_id": "..."}' \
  --output screenshot.png
```

### `POST /api/evaluate`
Evaluate JavaScript.

```bash
curl -X POST http://localhost:9222/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"page_id": "...", "script": "document.title"}'
```

### `GET /api/cookies`
Get cookies.

```bash
curl http://localhost:9222/api/cookies?page_id=...
```

### `POST /api/cookies`
Set cookies.

```bash
curl -X POST http://localhost:9222/api/cookies \
  -H "Content-Type: application/json" \
  -d '{"page_id": "...", "cookies": [...]}'
```

## Usage Examples

### 1. LLM/AI Agent Integration

```python
# AI agent researching a topic
async def ai_agent_research(topic: str):
    browser = StealthBrowserService()
    await browser.start()
    
    # Search on Google
    page = await browser.get_page(f"https://google.com/search?q={topic}")
    
    # Extract search results
    results = await browser.evaluate(page, """
        Array.from(document.querySelectorAll('.g')).map(r => ({
            title: r.querySelector('h3')?.textContent,
            url: r.querySelector('a')?.href,
            snippet: r.querySelector('.st')?.textContent
        }))
    """)
    
    # Visit top result
    if results:
        await browser.navigate(page, results[0]['url'])
        content = await browser.evaluate(page, "document.body.textContent")
    
    await browser.stop()
    return content
```

### 2. Web Scraping with Stealth

```python
# Scrape protected e-commerce site
async def scrape_products():
    config = BrowserConfig(
        stealth_level="ultimate",
        block_images=True,  # Faster
        enable_human_simulation=True
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    page = await browser.get_page("https://shop.example.com/products")
    
    # Human-like scrolling to load all products
    await browser.evaluate(page, "window.scrollTo(0, document.body.scrollHeight)")
    
    products = await browser.evaluate(page, """
        Array.from(document.querySelectorAll('.product')).map(p => ({
            name: p.querySelector('.name')?.textContent,
            price: p.querySelector('.price')?.textContent,
            available: !p.querySelector('.out-of-stock')
        }))
    """)
    
    await browser.stop()
    return products
```

### 3. Automated Testing

```python
# E2E test with stealth
async def test_user_flow():
    browser = StealthBrowserService()
    await browser.start()
    
    page = await browser.get_page("https://app.example.com")
    
    # Login
    await browser.type(page, "#email", "test@example.com")
    await browser.type(page, "#password", "password123")
    await browser.click(page, "#login-btn")
    
    # Wait for dashboard
    await browser.wait_for_selector(page, ".dashboard")
    
    # Verify logged in
    username = await browser.evaluate(page, 
        "document.querySelector('.username').textContent"
    )
    
    assert username == "Test User"
    
    await browser.stop()
```

### 4. Form Automation

```python
# Fill complex forms with human behavior
async def fill_application():
    config = BrowserConfig(
        enable_human_simulation=True,
        human_typing_speed=(80, 150)
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    page = await browser.get_page("https://forms.example.com/apply")
    
    # Fill form with human-like typing
    await browser.type(page, "#name", "John Doe")
    await browser.type(page, "#email", "john@example.com")
    
    # Select dropdown
    await browser.evaluate(page, """
        document.querySelector('#country').value = 'US'
    """)
    
    # Check boxes
    await browser.click(page, "#terms")
    
    # Submit
    await browser.click(page, "#submit")
    
    await browser.stop()
```

## Best Practices

### 1. Stealth Level Selection

- **Basic**: Simple sites with minimal protection
- **Enhanced**: Sites with basic bot detection
- **Maximum**: E-commerce, social media sites
- **Ultimate**: Heavily protected sites (Cloudflare, DataDome)

### 2. Human Simulation

Always enable human simulation for protected sites:

```python
config = BrowserConfig(
    enable_human_simulation=True,
    random_delays=True,
    human_typing_speed=(50, 200)
)
```

### 3. Session Management

For long-running automation, persist sessions:

```python
config = BrowserConfig(
    persist_session=True,
    cookies_file="session.json"
)
```

### 4. Resource Optimization

Block unnecessary resources for faster scraping:

```python
config = BrowserConfig(
    block_images=True,
    block_media=True,
    block_fonts=True
)
```

### 5. Error Handling

Always wrap operations in try-catch:

```python
try:
    page = await browser.get_page(url)
    await browser.click(page, selector)
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Take screenshot for debugging
    await browser.screenshot(page, "error.png")
```

## Troubleshooting

### Browser Won't Start

```python
# Check if Playwright is installed
playwright install chromium

# Use specific browser path
config = BrowserConfig()
browser = StealthBrowserService(config)
```

### Detection Issues

```python
# Increase stealth level
config = BrowserConfig(
    stealth_level="ultimate",
    enable_human_simulation=True,
    disable_cdp_detection=True
)
```

### Performance Issues

```python
# Optimize for speed
config = BrowserConfig(
    headless=True,
    block_images=True,
    block_media=True,
    block_stylesheets=True
)
```

## Advanced Features

### Custom Stealth Scripts

```python
# Add custom stealth scripts
async def add_custom_stealth(page):
    await page.add_init_script("""
        // Your custom stealth code
        Object.defineProperty(navigator, 'customProperty', {
            get: () => 'spoofed_value'
        });
    """)
```

### Proxy Rotation

```python
proxy_list = [
    {"server": "http://proxy1.com:8080"},
    {"server": "http://proxy2.com:8080"},
]

config = BrowserConfig(
    rotate_proxy=True,
    proxy_list=proxy_list
)
```

### Multi-Browser Coordination

```python
# Run multiple browsers in parallel
browsers = []
for i in range(3):
    browser = StealthBrowserService()
    await browser.start()
    browsers.append(browser)

# Use browsers concurrently
tasks = [browser.get_page(url) for browser in browsers]
pages = await asyncio.gather(*tasks)
```

## Security Considerations

1. **Never expose the API server to public internet**
2. **Use authentication for API endpoints in production**
3. **Sanitize user inputs when evaluating JavaScript**
4. **Store sensitive data (cookies, passwords) securely**
5. **Rotate proxies and user agents regularly**

## Performance Tips

1. **Use headless mode for better performance**
2. **Block unnecessary resources (images, media)**
3. **Reuse browser instances instead of creating new ones**
4. **Use appropriate timeouts to avoid hanging**
5. **Implement retry logic with exponential backoff**

## Conclusion

The Standalone Stealth Browser Service provides a robust, flexible solution for browser automation that works with any application. Its comprehensive stealth capabilities, human behavior simulation, and clean API make it ideal for:

- AI agents and LLMs requiring web access
- Web scraping protected sites
- Automated testing with anti-bot bypass
- Form automation requiring human-like behavior
- Data extraction from dynamic websites
- Screenshot services
- Any application needing undetected browser automation

The service is designed to be production-ready with proper error handling, resource management, and extensive configuration options to handle any automation scenario.