# Browser-Use Custom Tools Framework

A powerful, extensible framework for creating custom browser automation tools that integrate seamlessly with the browser-use library.

## Overview

This framework provides:
- **Easy tool creation** - Simple decorator-based tool registration
- **Tool counting** - Built-in tool to count all available tools (custom + default)
- **Dynamic tool addition** - Add new tools at runtime
- **Advanced extensions** - Security scanning, SEO analysis, accessibility auditing, and more

## Files Structure

```
ai_agents/
├── custom_tools.py              # Core framework with basic custom tools
├── demo_custom_tools.py         # Demonstration script showing usage
├── advanced_tools_extension.py  # Advanced tools (security, SEO, accessibility)
└── README_CUSTOM_TOOLS.md       # This documentation
```

## Quick Start

```python
from custom_tools import CustomToolsManager
from browser_use import ChatGoogle, Agent

# Create custom tools manager
manager = CustomToolsManager(include_defaults=True)

# Get tools instance for agent
tools = manager.get_tools_instance()

# Create agent with custom tools
llm = ChatGoogle(model="gemini-2.0-flash-exp")
agent = Agent(task="Count all available tools", llm=llm, tools=tools)
await agent.run()
```

## Built-in Custom Tools

### 1. Tool Counter
Counts all available tools (custom and default) with optional detailed information.

**Parameters:**
- `include_custom` (bool): Include custom tools in count
- `include_default` (bool): Include default browser-use tools
- `detailed` (bool): Return detailed information about each tool

**Usage:**
```python
task = "Use count_tools to get detailed information about all available tools"
```

### 2. Advanced Element Extractor
Extracts and analyzes page elements with advanced filtering.

**Parameters:**
- `selector_type` (str): Type of elements to extract (all, buttons, links, forms, inputs)
- `include_hidden` (bool): Include hidden elements
- `extract_attributes` (bool): Extract element attributes

**Usage:**
```python
task = "Use extract_elements_advanced to find all buttons and links on the page"
```

### 3. Network Monitor
Monitors and logs network requests for a specified duration.

**Parameters:**
- `duration` (int): Duration to monitor in seconds
- `filter_type` (str): Filter for specific request types (xhr, fetch, document)

**Usage:**
```python
task = "Monitor network activity for 10 seconds and identify all API calls"
```

## Advanced Tools (Extension)

### 1. Security Scanner
Performs comprehensive security vulnerability scanning.

**Features:**
- XSS vulnerability detection
- CSRF protection checking
- Security header analysis
- Sensitive data exposure detection

**Parameters:**
- `scan_depth` (str): basic, moderate, or deep
- `check_types` (list): Types of checks to perform

### 2. Structured Data Extractor
Extracts structured data from web pages.

**Features:**
- Table extraction
- JSON-LD structured data
- Price extraction
- Email and phone number extraction

**Parameters:**
- `extraction_type` (str): auto, table, json-ld, prices, emails, phones
- `output_format` (str): json, csv, table

### 3. Accessibility Auditor
Performs WCAG compliance checking.

**Features:**
- Missing alt text detection
- Heading hierarchy analysis
- Form label checking
- Keyboard accessibility testing
- Color contrast checking

**Parameters:**
- `wcag_level` (str): A, AA, or AAA
- `include_warnings` (bool): Include warnings in report

### 4. SEO Analyzer
Analyzes page SEO and provides recommendations.

**Features:**
- Meta tag analysis
- Heading structure checking
- Image optimization detection
- Link analysis
- Schema markup detection

**Parameters:**
- `check_categories` (list): Categories to analyze
- `include_recommendations` (bool): Include improvement recommendations

## Adding Custom Tools Dynamically

You can add new tools at runtime:

```python
from pydantic import BaseModel, Field

class MyToolParams(BaseModel):
    param1: str = Field(description="First parameter")
    param2: int = Field(default=10, description="Second parameter")

@manager.tools.registry.action(
    'Description of what your tool does',
    param_model=MyToolParams
)
async def my_custom_tool(params: MyToolParams, browser_session):
    # Your tool implementation
    result = await browser_session.evaluate("/* JavaScript code */")
    return result
```

## Running the Demos

### Basic Demo
```bash
python demo_custom_tools.py
# Select option 1 for basic tools demo
```

### Advanced Demo
```bash
python advanced_tools_extension.py
# Runs comprehensive website analysis
```

## Best Practices

1. **Tool Naming**: Use descriptive, action-oriented names
2. **Parameter Models**: Always use Pydantic models for parameters
3. **Error Handling**: Include try-catch blocks in JavaScript code
4. **Visual Feedback**: Display results in the browser for better UX
5. **Documentation**: Provide clear descriptions for all tools

## Architecture

The framework follows a modular architecture:

```
CustomToolsManager
├── Tools (browser-use)
│   └── Registry
│       ├── Default Tools
│       └── Custom Tools
└── ToolInfo Storage
    └── Metadata
```

## Integration with Existing Code

The framework integrates seamlessly with your existing browser-use code:

```python
# Your existing code
from browser_use import Agent, ChatGoogle

# Add custom tools
from ai_agents.custom_tools import CustomToolsManager

# Create manager
manager = CustomToolsManager(include_defaults=True)

# Use with your agent
agent = Agent(
    task="Your task",
    llm=your_llm,
    tools=manager.get_tools_instance()  # Use custom tools
)
```

## Tool Categories

Tools are organized into categories:

1. **Analysis Tools**: Element extraction, network monitoring
2. **Security Tools**: Vulnerability scanning, security headers
3. **Accessibility Tools**: WCAG compliance, keyboard navigation
4. **SEO Tools**: Meta tags, structured data, performance
5. **Utility Tools**: Tool counting, screenshot capture
6. **Data Tools**: Table extraction, form filling

## Performance Considerations

- Tools execute JavaScript in the browser context
- Large DOM operations may impact performance
- Network monitoring adds minimal overhead
- Security scans are throttled to avoid overwhelming the page

## Future Enhancements

Potential areas for expansion:
- Visual regression testing
- AI-powered element detection
- Cross-browser compatibility testing
- Performance profiling tools
- Automated form testing
- Cookie and storage analysis
- WebSocket monitoring
- Service worker inspection

## Contributing

To add new tools:
1. Create a new Pydantic model for parameters
2. Implement the tool function with browser_session
3. Register with the tools registry
4. Add documentation and examples

## License

This framework is part of the ai_agents module and follows the project's licensing terms.