"""
Custom Browser-Use Tools Framework
Extensible framework for creating custom browser automation tools
"""

import asyncio
import inspect
from typing import Any, Callable, Optional, Type, List, Dict
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field

from browser_use import ChatGoogle
from browser_use.agent.service import Agent
from browser_use.browser.session import BrowserSession
from browser_use.tools.service import Tools
from browser_use.tools.registry.service import Registry


class ToolCounterParams(BaseModel):
    """Parameters for the tool counter action"""
    include_custom: bool = Field(
        default=True,
        description="Include custom tools in the count"
    )
    include_default: bool = Field(
        default=True,
        description="Include default browser-use tools in the count"
    )
    detailed: bool = Field(
        default=False,
        description="Return detailed information about each tool"
    )


class FileAnalyzerParams(BaseModel):
    """Parameters for file analyzer tool"""
    file_path: str = Field(description="Path to the file to analyze")
    analysis_type: str = Field(
        default="basic",
        description="Type of analysis: basic, detailed, security"
    )


class NetworkMonitorParams(BaseModel):
    """Parameters for network monitoring"""
    duration: int = Field(
        default=10,
        description="Duration to monitor network requests (in seconds)"
    )
    filter_type: Optional[str] = Field(
        default=None,
        description="Filter for specific request types (xhr, fetch, document, etc.)"
    )


class ElementExtractorParams(BaseModel):
    """Parameters for advanced element extraction"""
    selector_type: str = Field(
        default="all",
        description="Type of elements to extract: all, buttons, links, forms, inputs"
    )
    include_hidden: bool = Field(
        default=False,
        description="Include hidden elements in extraction"
    )
    extract_attributes: bool = Field(
        default=True,
        description="Extract element attributes"
    )


@dataclass
class ToolInfo:
    """Information about a registered tool"""
    name: str
    description: str
    function: Callable
    param_model: Optional[Type[BaseModel]]
    is_custom: bool
    created_at: datetime


class CustomToolsManager:
    """Manager for custom browser-use tools"""

    def __init__(self, include_defaults: bool = True):
        """
        Initialize custom tools manager

        Args:
            include_defaults: Whether to include default browser-use tools
        """
        self.tools = Tools() if include_defaults else Tools(exclude_actions=['*'])
        self.custom_tools: Dict[str, ToolInfo] = {}
        self.default_tool_count = 0

        # Register custom tools
        self._register_custom_tools()

        # Count default tools if included
        if include_defaults:
            self._count_default_tools()

    def _count_default_tools(self):
        """Count the default browser-use tools"""
        try:
            # Access the registry's actions
            if hasattr(self.tools.registry, 'registry') and hasattr(self.tools.registry.registry, 'actions'):
                self.default_tool_count = len(self.tools.registry.registry.actions)
            else:
                # Fallback: estimate based on typical browser-use tools
                self.default_tool_count = 20  # Approximate count
        except Exception as e:
            print(f"Could not count default tools: {e}")
            self.default_tool_count = 0

    def _register_custom_tools(self):
        """Register all custom tools"""

        # Tool 1: Tool Counter
        @self.tools.registry.action(
            'Count all available tools (custom and default) with optional detailed information',
            param_model=ToolCounterParams
        )
        async def count_tools(params: ToolCounterParams, browser_session: BrowserSession):
            """Count and analyze available tools"""
            result = {
                "timestamp": datetime.now().isoformat(),
                "custom_tools": 0,
                "default_tools": 0,
                "total_tools": 0,
                "details": {}
            }

            # Count custom tools
            if params.include_custom:
                result["custom_tools"] = len(self.custom_tools)
                if params.detailed:
                    result["details"]["custom"] = [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "created_at": tool.created_at.isoformat()
                        }
                        for tool in self.custom_tools.values()
                    ]

            # Count default tools
            if params.include_default:
                result["default_tools"] = self.default_tool_count
                if params.detailed:
                    # Try to get default tool names
                    try:
                        if hasattr(self.tools.registry, 'registry') and hasattr(self.tools.registry.registry, 'actions'):
                            result["details"]["default"] = [
                                {
                                    "name": action.name,
                                    "description": action.description
                                }
                                for action in self.tools.registry.registry.actions.values()
                            ]
                    except Exception as e:
                        result["details"]["default_error"] = str(e)

            result["total_tools"] = result["custom_tools"] + result["default_tools"]

            # Display results in browser
            html_content = f"""
            <html>
            <head>
                <title>Tool Count Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                    .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
                    .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                    .stat-value {{ font-size: 2em; font-weight: bold; }}
                    .stat-label {{ margin-top: 5px; opacity: 0.9; }}
                    .details {{ margin-top: 30px; }}
                    .tool-list {{ list-style: none; padding: 0; }}
                    .tool-item {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #007bff; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔧 Tool Count Report</h1>
                    <p>Generated at: {result['timestamp']}</p>

                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-value">{result['custom_tools']}</div>
                            <div class="stat-label">Custom Tools</div>
                        </div>
                        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                            <div class="stat-value">{result['default_tools']}</div>
                            <div class="stat-label">Default Tools</div>
                        </div>
                        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                            <div class="stat-value">{result['total_tools']}</div>
                            <div class="stat-label">Total Tools</div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Navigate to data URL to display the report
            data_url = f"data:text/html,{html_content}"
            await browser_session.navigate_to(data_url)

            return result

        # Store tool info
        self.custom_tools["count_tools"] = ToolInfo(
            name="count_tools",
            description="Count all available tools",
            function=count_tools,
            param_model=ToolCounterParams,
            is_custom=True,
            created_at=datetime.now()
        )

        # Tool 2: Advanced Element Extractor
        @self.tools.registry.action(
            'Extract and analyze page elements with advanced filtering and attribute extraction',
            param_model=ElementExtractorParams
        )
        async def extract_elements_advanced(params: ElementExtractorParams, browser_session: BrowserSession):
            """Advanced element extraction with filtering"""

            # JavaScript to extract elements
            js_code = """
            (function() {
                const selectorMap = {
                    'all': '*',
                    'buttons': 'button, input[type="button"], input[type="submit"]',
                    'links': 'a[href]',
                    'forms': 'form',
                    'inputs': 'input, textarea, select'
                };

                const selector = selectorMap['""" + params.selector_type + """'] || '*';
                const elements = document.querySelectorAll(selector);
                const includeHidden = """ + str(params.include_hidden).lower() + """;
                const extractAttributes = """ + str(params.extract_attributes).lower() + """;

                const result = [];

                elements.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    const isVisible = rect.width > 0 && rect.height > 0 &&
                                     window.getComputedStyle(el).display !== 'none' &&
                                     window.getComputedStyle(el).visibility !== 'hidden';

                    if (!includeHidden && !isVisible) return;

                    const elementInfo = {
                        tagName: el.tagName.toLowerCase(),
                        text: el.textContent.trim().substring(0, 100),
                        visible: isVisible,
                        position: {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height
                        }
                    };

                    if (extractAttributes) {
                        elementInfo.attributes = {};
                        for (const attr of el.attributes) {
                            elementInfo.attributes[attr.name] = attr.value;
                        }
                    }

                    result.push(elementInfo);
                });

                return {
                    count: result.length,
                    elements: result,
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                };
            })();
            """

            # Execute JavaScript in browser
            result = await browser_session.evaluate(js_code)

            # Create summary report
            summary_html = f"""
            <html>
            <head>
                <title>Element Extraction Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background: #f0f2f5; }}
                    .report {{ max-width: 1200px; margin: 0 auto; }}
                    h1 {{ color: #1a73e8; }}
                    .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                    .element-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }}
                    .element-card {{ background: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; }}
                    .element-tag {{ display: inline-block; background: #1a73e8; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="report">
                    <h1>📊 Element Extraction Report</h1>
                    <div class="summary">
                        <h2>Summary</h2>
                        <p>URL: {result.get('url', 'N/A')}</p>
                        <p>Total Elements Found: {result.get('count', 0)}</p>
                        <p>Filter Type: {params.selector_type}</p>
                        <p>Include Hidden: {params.include_hidden}</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Display summary
            await browser_session.evaluate(f"document.body.innerHTML = `{summary_html}`;")

            return result

        self.custom_tools["extract_elements_advanced"] = ToolInfo(
            name="extract_elements_advanced",
            description="Advanced element extraction",
            function=extract_elements_advanced,
            param_model=ElementExtractorParams,
            is_custom=True,
            created_at=datetime.now()
        )

        # Tool 3: Network Monitor
        @self.tools.registry.action(
            'Monitor and log network requests for a specified duration',
            param_model=NetworkMonitorParams
        )
        async def monitor_network(params: NetworkMonitorParams, browser_session: BrowserSession):
            """Monitor network activity"""

            # JavaScript to setup network monitoring
            setup_js = """
            window.networkLog = [];
            const originalFetch = window.fetch;
            const originalXHR = window.XMLHttpRequest.prototype.open;

            // Override fetch
            window.fetch = function(...args) {
                const startTime = Date.now();
                const url = args[0];

                return originalFetch.apply(this, args).then(response => {
                    window.networkLog.push({
                        type: 'fetch',
                        url: url,
                        status: response.status,
                        duration: Date.now() - startTime,
                        timestamp: new Date().toISOString()
                    });
                    return response;
                });
            };

            // Override XMLHttpRequest
            window.XMLHttpRequest.prototype.open = function(method, url, ...args) {
                this._startTime = Date.now();
                this._url = url;
                this._method = method;

                this.addEventListener('load', function() {
                    window.networkLog.push({
                        type: 'xhr',
                        url: this._url,
                        method: this._method,
                        status: this.status,
                        duration: Date.now() - this._startTime,
                        timestamp: new Date().toISOString()
                    });
                });

                return originalXHR.apply(this, [method, url, ...args]);
            };

            console.log('Network monitoring initialized');
            """

            await browser_session.evaluate(setup_js)

            # Wait for the specified duration
            await asyncio.sleep(params.duration)

            # Collect network logs
            logs = await browser_session.evaluate("window.networkLog || []")

            # Filter if requested
            if params.filter_type:
                logs = [log for log in logs if log.get('type') == params.filter_type]

            result = {
                "duration": params.duration,
                "total_requests": len(logs),
                "requests": logs,
                "timestamp": datetime.now().isoformat()
            }

            return result

        self.custom_tools["monitor_network"] = ToolInfo(
            name="monitor_network",
            description="Monitor network activity",
            function=monitor_network,
            param_model=NetworkMonitorParams,
            is_custom=True,
            created_at=datetime.now()
        )

    def get_tools_instance(self) -> Tools:
        """Get the Tools instance with all custom tools registered"""
        return self.tools

    def list_custom_tools(self) -> List[Dict[str, Any]]:
        """List all registered custom tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.param_model.schema() if tool.param_model else None,
                "created_at": tool.created_at.isoformat()
            }
            for tool in self.custom_tools.values()
        ]

    def add_custom_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        param_model: Optional[Type[BaseModel]] = None
    ):
        """
        Add a new custom tool dynamically

        Args:
            name: Tool name
            description: Tool description
            function: Async function to execute
            param_model: Pydantic model for parameters
        """
        # Register with browser-use
        self.tools.registry.action(description, param_model=param_model)(function)

        # Store tool info
        self.custom_tools[name] = ToolInfo(
            name=name,
            description=description,
            function=function,
            param_model=param_model,
            is_custom=True,
            created_at=datetime.now()
        )

        return self