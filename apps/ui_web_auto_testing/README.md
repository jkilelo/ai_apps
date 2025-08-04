# Web Automation Testing Framework

A powerful, comprehensive framework for automated web testing with a 4-step workflow pipeline.

## Overview

This framework provides a complete solution for web automation testing through a structured 4-step process:

1. **Target Setup** - URL analysis & element extraction
2. **Workflow Builder** - Test case generation
3. **Test Execution** - Running automated tests
4. **Results & Report** - Comprehensive reporting

## Features

- 🎯 **Intelligent Element Extraction** - Automatically identifies and extracts web elements
- 🧪 **Smart Test Generation** - Creates test cases based on extracted elements
- 🚀 **Parallel Execution** - Run tests concurrently for faster results
- 🌐 **Cross-Browser Testing** - Test across Chrome, Firefox, Safari, and Edge
- 📊 **Comprehensive Reports** - Detailed results with metrics and insights
- 🛠️ **CLI & SDK** - Both command-line and programmatic interfaces
- 🔧 **Extensible Architecture** - Easy to extend and customize

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14+ (for Playwright)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourorg/web-automation-framework.git
cd web-automation-framework

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install
```

### Quick Install

```bash
pip install web-automation-framework
playwright install
```

## Quick Start

### Using the CLI

#### Run Complete Workflow

```bash
# Basic usage
web-automation run --url https://example.com --name "My Test Suite"

# With options
web-automation run \
  --url https://example.com \
  --name "E-commerce Test" \
  --profile qa_tester \
  --browser chrome \
  --parallel \
  --output results.json
```

#### Step-by-Step Execution

```bash
# Step 1: Analyze target URL
web-automation step target --url https://example.com --output session.json

# Step 2: Build test workflow
SESSION_ID=$(cat session.json | jq -r .session_id)
web-automation step build --session-id $SESSION_ID

# Step 3: Execute tests
web-automation step execute --session-id $SESSION_ID --parallel

# Step 4: Generate report
web-automation step report --session-id $SESSION_ID --format html --output report.html
```

### Using the SDK

```python
import asyncio
from web_automation_framework import WebAutomationSDK, WorkflowConfig, ExecutionConfig

async def run_tests():
    # Initialize SDK
    async with WebAutomationSDK() as sdk:
        # Configure workflow
        config = WorkflowConfig(
            target_url="https://example.com",
            test_name="Example Test Suite",
            profile="qa_tester",
            include_accessibility=True
        )
        
        # Run complete workflow
        results = await sdk.run_complete_workflow(config)
        
        # Print results
        print(f"Success Rate: {results['metrics']['success_rate']:.1f}%")
        print(f"Total Tests: {results['test_execution']['total_tests']}")
        print(f"Passed: {results['test_execution']['passed_tests']}")

# Run the async function
asyncio.run(run_tests())
```

## CLI Commands

### Main Commands

- `web-automation run` - Run complete 4-step workflow
- `web-automation step` - Execute individual workflow steps
- `web-automation session` - Manage workflow sessions
- `web-automation config` - Configure CLI settings

### Session Management

```bash
# List all sessions
web-automation session list

# Get session status
web-automation session status <session-id>

# Watch session progress
web-automation session status <session-id> --watch

# Delete session
web-automation session delete <session-id>
```

### Configuration

```bash
# Set API URL
web-automation config set --api-url http://localhost:8002

# Show current configuration
web-automation config show
```

## SDK Reference

### Key Classes

#### WorkflowConfig

```python
config = WorkflowConfig(
    target_url="https://example.com",        # Required
    test_name="My Test Suite",               # Optional
    description="Test description",          # Optional
    profile="qa_tester",                     # qa_tester, developer, accessibility_tester
    browser_type="chrome",                   # chrome, firefox, safari, edge
    viewport={"width": 1920, "height": 1080}, # Optional viewport size
    include_accessibility=True               # Include accessibility tests
)
```

#### ExecutionConfig

```python
execution_config = ExecutionConfig(
    execution_mode="parallel",    # sequential or parallel
    browser="chromium",          # Browser for testing
    capture_screenshots=True,    # Capture screenshots during tests
    max_retries=3,              # Maximum retries for failed tests
    timeout=300,                # Timeout in seconds
    cross_browser=True,         # Enable cross-browser testing
    browsers=["chrome", "firefox", "edge"],  # Browsers for cross-browser
    include_mobile=True         # Include mobile browser testing
)
```

### Main Methods

#### run_complete_workflow()

```python
results = await sdk.run_complete_workflow(
    config=workflow_config,
    execution_config=execution_config,
    test_types=["functional", "accessibility"],
    report_format="json"
)
```

#### Individual Step Methods

```python
# Step 1: Start workflow and extract elements
session = await sdk.start_workflow(config)
await sdk.wait_for_step_completion(session.session_id, 1)

# Step 2: Build test workflow
await sdk.build_workflow(session.session_id, test_types=["functional"])
await sdk.wait_for_step_completion(session.session_id, 2)

# Step 3: Execute tests
await sdk.execute_tests(session.session_id, execution_config)
await sdk.wait_for_step_completion(session.session_id, 3)

# Step 4: Get results
results = await sdk.get_results(session.session_id, format="json")
```

## Output Formats

### JSON Report

```json
{
  "session_info": {
    "session_id": "abc123",
    "test_name": "Example Test Suite",
    "target_url": "https://example.com"
  },
  "metrics": {
    "success_rate": 95.0,
    "coverage_score": 85.0,
    "accessibility_compliance": 92.0
  },
  "test_execution": {
    "total_tests": 20,
    "passed_tests": 19,
    "failed_tests": 1,
    "execution_time": 45.2
  }
}
```

### HTML Report

The HTML report provides:
- Interactive test results table
- Visual metrics dashboard
- Screenshots and error details
- Execution timeline

## Advanced Usage

### Cross-Browser Testing

```bash
web-automation run \
  --url https://example.com \
  --cross-browser \
  --output cross-browser-report.json
```

### Custom Test Profiles

```python
# Using different testing profiles
profiles = ["qa_tester", "developer", "accessibility_tester"]

for profile in profiles:
    config = WorkflowConfig(
        target_url="https://example.com",
        profile=profile
    )
    results = await sdk.run_complete_workflow(config)
```

### Parallel Execution

```python
# Run multiple workflows in parallel
import asyncio

async def test_multiple_sites():
    urls = [
        "https://site1.com",
        "https://site2.com",
        "https://site3.com"
    ]
    
    tasks = []
    async with WebAutomationSDK() as sdk:
        for url in urls:
            config = WorkflowConfig(target_url=url)
            task = sdk.run_complete_workflow(config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
```

## Best Practices

1. **Use Profiles Appropriately**
   - `qa_tester`: General functional testing
   - `developer`: Technical validation
   - `accessibility_tester`: WCAG compliance

2. **Manage Sessions**
   - Clean up completed sessions
   - Monitor long-running sessions
   - Use session IDs for tracking

3. **Error Handling**
   ```python
   try:
       results = await sdk.run_complete_workflow(config)
   except TimeoutError:
       print("Workflow timed out")
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **Performance Tips**
   - Use parallel execution for multiple tests
   - Enable cross-browser testing selectively
   - Set appropriate timeouts

## Troubleshooting

### Common Issues

1. **Playwright Installation**
   ```bash
   # Reinstall browsers
   playwright install --with-deps
   ```

2. **API Connection**
   ```bash
   # Check API status
   curl http://localhost:8002/health
   ```

3. **Session Errors**
   ```bash
   # Clear stuck sessions
   web-automation session list
   web-automation session delete <session-id>
   ```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://docs.webautomation.com](https://docs.webautomation.com)
- Issues: [GitHub Issues](https://github.com/yourorg/web-automation-framework/issues)
- Community: [Discord Server](https://discord.gg/webautomation)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.