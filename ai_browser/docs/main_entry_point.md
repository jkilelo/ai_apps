# Main Entry Point Documentation

## Overview

The `src/main.py` file serves as the primary CLI interface for the AI-First Smart Browser v2.0.0. It orchestrates all five architectural layers to execute natural language tasks through intelligent browser automation.

**File**: src/main.py  
**Status**: Production Ready  
**Version**: 2.0.0

## Architecture Integration

The main entry point coordinates all 5 layers:

```
User Input (CLI)
    ↓
main.py (AIBrowser)
    ↓
┌─────────────────────────────────┐
│ 1. Initialize Memory Layer      │
│ 2. Load Extensibility (Plugins) │
│ 3. Setup Execution Layer        │
│ 4. Configure Perception Layer   │
│ 5. Initialize Cognition Layer   │
└─────────────────────────────────┘
    ↓
Task Execution Loop
    ↓
Result Output
```

## Core Components

### TaskConfig Class

Pydantic model for task configuration:

```python
class TaskConfig(BaseModel):
    task: str                          # Natural language task
    url: Optional[str]                 # Starting URL
    headless: bool = True             # Browser visibility
    timeout: int = 60000              # Task timeout (ms)
    max_steps: int = 50               # Max action steps
    screenshot_on_error: bool = True  # Error screenshots
    debug: bool = False               # Debug mode
    config_file: Optional[str]        # Config file path
    test_stealth: bool = False        # Stealth testing
    plugin_dir: Optional[str]         # Custom plugins
    disable_plugins: List[str]        # Plugins to disable
```

### AIBrowser Class

Main orchestrator that coordinates all layers:

```python
class AIBrowser:
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    async def initialize(self, task_config: TaskConfig) -> None
    async def execute_task(self, task_config: TaskConfig) -> Dict[str, Any]
    async def test_stealth(self) -> Dict[str, Any]
    async def cleanup(self) -> None
```

## CLI Interface

### Basic Usage

```bash
python src/main.py --task "Your task here" --url "https://example.com"
```

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--task` | string | - | Natural language task to execute |
| `--url` | string | - | Starting URL for the task |
| `--headless` | bool | true | Run browser in headless mode |
| `--timeout` | int | 60000 | Task timeout in milliseconds |
| `--max-steps` | int | 50 | Maximum number of action steps |
| `--config` | string | - | Path to configuration file |
| `--plugin-dir` | string | - | Additional plugin directory |
| `--disable-plugin` | string | - | Disable specific plugin(s) |
| `--test-stealth` | flag | - | Run stealth capability tests |
| `--debug` | flag | - | Enable debug mode |
| `--screenshot-on-error` | bool | true | Capture screenshots on error |
| `--log-level` | string | INFO | Logging level |
| `--log-file` | string | - | Log file path |

### Examples

#### Basic Task Execution
```bash
python src/main.py --task "Search for Python tutorials" --url "https://google.com"
```

#### Form Automation
```bash
python src/main.py --task "Fill contact form with name John Doe" \
                   --url "https://example.com/contact" \
                   --headless false
```

#### Stealth Testing
```bash
python src/main.py --test-stealth
```

#### Debug Mode
```bash
python src/main.py --task "Debug navigation" \
                   --url "https://example.com" \
                   --debug \
                   --headless false \
                   --log-level DEBUG
```

#### Production Configuration
```bash
python src/main.py --task "Production task" \
                   --config configs/production.json
```

#### Custom Plugins
```bash
python src/main.py --task "Task with custom plugin" \
                   --plugin-dir /path/to/custom/plugins \
                   --disable-plugin default_plugin
```

## Task Execution Flow

### 1. Initialization Phase

```python
# Layer initialization order (critical!)
1. Memory Layer      # Others may use it
2. Extensibility     # Plugin loading
3. Execution Layer   # Browser setup
4. Perception Layer  # State capture
5. Cognition Layer   # AI reasoning
```

### 2. Main Execution Loop

```python
while steps < max_steps:
    # 1. Capture current state
    state = await state_observer.capture_state(page)
    
    # 2. Store state in memory
    await memory_manager.store_page_state(state)
    
    # 3. Plan next action
    action = await orchestrator.plan_next_action(task, state, previous_actions)
    
    # 4. Execute hooks (PreToolUse)
    hook_result = await hook_system.emit("PreToolUse", {...})
    
    # 5. Execute action
    result = await action_executor.execute_action(action, context)
    
    # 6. Execute hooks (PostToolUse)
    await hook_system.emit("PostToolUse", {...})
    
    # 7. Check completion
    if action.type == "complete":
        break
```

### 3. Result Structure

```python
{
    "task": "Original task description",
    "status": "completed|failed|timeout",
    "start_time": "2025-01-05T10:00:00",
    "end_time": "2025-01-05T10:01:30",
    "actions": [
        {
            "step": 1,
            "type": "click",
            "parameters": {...},
            "success": true,
            "error": null
        }
    ],
    "final_url": "https://example.com/result",
    "screenshots": ["screenshots/task_20250105_100130.png"],
    "error": null
}
```

## Hook System Integration

The main entry point triggers these hooks:

### SessionStart
```python
await hook_system.emit("SessionStart", {
    "timestamp": datetime.now().isoformat(),
    "config": task_config.dict()
})
```

### UserPromptSubmit
```python
await hook_system.emit("UserPromptSubmit", {
    "prompt": task_config.task,
    "url": task_config.url
})
```

### PreToolUse / PostToolUse
```python
# Before action execution
hook_result = await hook_system.emit("PreToolUse", {
    "action": action.dict(),
    "step": steps
})

# After action execution
await hook_system.emit("PostToolUse", {
    "action": action.dict(),
    "result": action_result.dict(),
    "step": steps
})
```

### Stop
```python
await hook_system.emit("Stop", {
    "task": task_config.task,
    "status": result["status"],
    "steps": steps
})
```

## Stealth Testing

The `--test-stealth` flag runs comprehensive bot detection tests:

### Test Sites
1. **bot.sannysoft.com** - Basic bot detection
2. **arh.antoinevastel.com** - Headless detection
3. **fingerprint.com/demo** - Advanced fingerprinting

### Test Output
```
STEALTH TEST RESULTS
============================
Overall Score: 3/3 (100.0% passed)

Detailed Results:
https://bot.sannysoft.com/:
  Status: ✅ PASSED
  WebDriver: undefined
  Plugins: 5
  Screenshot: screenshots/stealth_bot_20250105_100000.png
```

## Error Handling

### Timeout Handling
```python
if elapsed_time > task_config.timeout:
    result["status"] = "timeout"
    result["error"] = f"Task exceeded timeout of {task_config.timeout}ms"
```

### Screenshot on Error
```python
if task_config.screenshot_on_error and error_occurred:
    screenshot_path = f"screenshots/error_{timestamp}.png"
    await page.screenshot(path=screenshot_path)
    result["screenshots"].append(screenshot_path)
```

### Graceful Cleanup
```python
try:
    # Task execution
    result = await browser.execute_task(task_config)
except KeyboardInterrupt:
    logger.warning("Execution interrupted by user")
finally:
    await browser.cleanup()  # Always cleanup
```

## Configuration Files

### Production Configuration
Located at `configs/production.json`:
- Headless mode enabled
- Stealth plugins loaded
- Performance optimizations
- Security hardening
- Monitoring enabled

### Custom Configuration
```json
{
  "browser": {
    "headless": true,
    "viewport_width": 1920,
    "viewport_height": 1080
  },
  "cognition": {
    "default_provider": "openai",
    "temperature": 0.7
  },
  "execution": {
    "action_timeout": 30000,
    "retry_attempts": 3
  }
}
```

## Logging

### Log Levels
- **DEBUG**: Detailed execution info
- **INFO**: Task milestones (default)
- **WARNING**: Recoverable issues
- **ERROR**: Failures requiring attention

### Log Format
```
2025-01-05 10:00:00 | INFO | main:execute_task:209 - Executing task: Search for Python
2025-01-05 10:00:01 | INFO | main:execute_task:274 - Step 1: Executing type action
2025-01-05 10:00:02 | SUCCESS | main:execute_task:259 - Task completed successfully
```

### Log Files
```bash
# Logs rotate at 10MB, kept for 7 days
logs/ai_browser.log
logs/ai_browser.2025-01-05.log
```

## Performance Considerations

### Resource Management
- Browser contexts are created per task
- Automatic cleanup after task completion
- Memory is released after each session
- Plugins are loaded lazily

### Optimization Tips
1. Use `--headless true` for better performance
2. Adjust `--max-steps` based on task complexity
3. Use `--config` for consistent settings
4. Disable unnecessary plugins with `--disable-plugin`

## Troubleshooting

### Common Issues

#### Browser Won't Launch
```bash
# Install browser binaries
playwright install chromium
```

#### Plugin Loading Errors
```bash
# Check plugin directory
ls plugins/stealth/
# Disable problematic plugin
python src/main.py --task "..." --disable-plugin problematic_plugin
```

#### Memory Issues
```bash
# Reduce max steps
python src/main.py --task "..." --max-steps 10
```

#### Timeout Errors
```bash
# Increase timeout
python src/main.py --task "..." --timeout 120000
```

## Security Notes

### API Key Management
- Store keys in `.env` file
- Never pass keys via CLI
- Keys are masked in logs

### Safe Execution
- Plugins run in sandbox
- Resource limits enforced
- Hooks have timeout protection

## Integration Examples

### Python Script Integration
```python
import asyncio
from src.main import AIBrowser, TaskConfig

async def run_task():
    browser = AIBrowser()
    config = TaskConfig(
        task="Your task",
        url="https://example.com",
        headless=True
    )
    
    await browser.initialize(config)
    result = await browser.execute_task(config)
    await browser.cleanup()
    
    return result

result = asyncio.run(run_task())
```

### Shell Script Integration
```bash
#!/bin/bash
# Run multiple tasks
tasks=("Search for news" "Check weather" "Find recipes")

for task in "${tasks[@]}"; do
    python src/main.py --task "$task" --url "https://google.com"
    sleep 2
done
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 130 | Interrupted (Ctrl+C) |

---

*Last Updated: 2025-01-05 | Component: Main Entry Point | Status: Production Ready*