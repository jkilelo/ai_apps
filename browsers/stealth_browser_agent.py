"""
LangGraph Stealth Browser Agent - Intelligent browser automation with AI reasoning.

This agent combines:
1. LangGraph wrapper for LLM reasoning
2. UltimateStealthBrowser for anti-detection browsing
3. Tool-based architecture for browser actions
4. State management for complex workflows
"""

import asyncio
import json
import logging
from typing import TypedDict, Annotated, List, Dict, Any, Optional, Sequence
from enum import Enum
from pathlib import Path
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import our LangGraph wrapper
from langgraph_wrapper import get_langgraph_llm

# Import stealth browser
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_stealth_browser'))
from ai_stealth_browser.stealth_browser import (
    UltimateStealthBrowser, 
    StealthConfig, 
    StealthLevel,
    ElementData,
    quick_extract
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Browser Tools - Wrapped browser actions as LangChain tools
# ============================================================================

class BrowserInstance:
    """Singleton browser instance for tool usage."""
    _instance = None
    _browser = None
    
    @classmethod
    async def get_browser(cls) -> UltimateStealthBrowser:
        """Get or create browser instance."""
        if cls._browser is None:
            config = StealthConfig(
                stealth_level=StealthLevel.MAXIMUM,
                simulate_human_behavior=True,
                random_delays=True,
                cookie_acceptance=True
            )
            cls._browser = UltimateStealthBrowser(config)
            await cls._browser.initialize()
        return cls._browser
    
    @classmethod
    async def cleanup(cls):
        """Clean up browser instance."""
        if cls._browser:
            await cls._browser.cleanup()
            cls._browser = None


@tool
async def navigate_to_url(url: str) -> Dict[str, Any]:
    """Navigate to a URL with stealth mode."""
    browser = await BrowserInstance.get_browser()
    success = await browser.navigate(url)
    
    if success:
        # Extract key information about the page
        elements = await browser.extract_elements(strategies=["semantic"])
        title = await browser.execute_javascript("document.title")
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "element_count": len(elements),
            "key_elements": [
                {"text": e.text[:100], "type": e.element_type} 
                for e in elements[:5]
            ]
        }
    return {"success": False, "error": "Failed to navigate"}


@tool
async def click_element(selector: str) -> Dict[str, Any]:
    """Click an element on the page."""
    browser = await BrowserInstance.get_browser()
    success = await browser.click_element(selector)
    
    return {
        "success": success,
        "selector": selector,
        "action": "click"
    }


@tool
async def type_text(selector: str, text: str) -> Dict[str, Any]:
    """Type text into an input field."""
    browser = await BrowserInstance.get_browser()
    success = await browser.type_text(selector, text, human_like=True)
    
    return {
        "success": success,
        "selector": selector,
        "text": text[:50] + "..." if len(text) > 50 else text,
        "action": "type"
    }


@tool
async def extract_page_content() -> Dict[str, Any]:
    """Extract structured content from the current page."""
    browser = await BrowserInstance.get_browser()
    
    # Extract using multiple strategies
    elements = await browser.extract_elements(
        strategies=["semantic", "visual", "accessibility"]
    )
    
    # Organize content by type
    content = {
        "buttons": [],
        "links": [],
        "inputs": [],
        "text": [],
        "images": []
    }
    
    for elem in elements:
        if elem.element_type == "button":
            content["buttons"].append({
                "text": elem.text,
                "selector": elem.selector
            })
        elif elem.element_type == "link":
            content["links"].append({
                "text": elem.text,
                "href": elem.attributes.get("href", ""),
                "selector": elem.selector
            })
        elif elem.element_type in ["input", "textarea"]:
            content["inputs"].append({
                "type": elem.attributes.get("type", "text"),
                "placeholder": elem.attributes.get("placeholder", ""),
                "selector": elem.selector
            })
        elif elem.element_type == "image":
            content["images"].append({
                "alt": elem.attributes.get("alt", ""),
                "src": elem.attributes.get("src", ""),
                "selector": elem.selector
            })
        elif elem.text:
            content["text"].append(elem.text[:200])
    
    # Limit results for readability
    for key in content:
        content[key] = content[key][:10]
    
    return content


@tool
async def take_screenshot(filename: str = "screenshot.png") -> Dict[str, Any]:
    """Take a screenshot of the current page."""
    browser = await BrowserInstance.get_browser()
    screenshot_data = await browser.take_screenshot(filename)
    
    return {
        "success": screenshot_data is not None,
        "filename": filename if screenshot_data else None,
        "size": len(screenshot_data) if screenshot_data else 0
    }


@tool
async def execute_javascript(script: str) -> Any:
    """Execute JavaScript on the page."""
    browser = await BrowserInstance.get_browser()
    result = await browser.execute_javascript(script)
    return {"result": str(result), "script": script[:100]}


@tool
async def wait_for_element(selector: str, timeout: int = 30) -> Dict[str, Any]:
    """Wait for an element to appear on the page."""
    browser = await BrowserInstance.get_browser()
    found = await browser.wait_for_selector(selector, timeout)
    
    return {
        "success": found,
        "selector": selector,
        "timeout": timeout
    }


# ============================================================================
# Agent State and Logic
# ============================================================================

class BrowserTask(Enum):
    """Types of browser tasks the agent can perform."""
    SCRAPE = "scrape"
    FILL_FORM = "fill_form"
    SEARCH = "search"
    MONITOR = "monitor"
    AUTOMATE = "automate"
    TEST = "test"


class BrowserAgentState(TypedDict):
    """State for the browser agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task: str
    current_url: Optional[str]
    target_url: Optional[str]
    extracted_data: Dict[str, Any]
    actions_taken: List[Dict[str, Any]]
    task_complete: bool
    error: Optional[str]


class StealthBrowserAgent:
    """
    Intelligent browser agent that combines LLM reasoning with stealth browsing.
    """
    
    def __init__(self, temperature: float = 0.3):
        self.llm = get_langgraph_llm(temperature=temperature)
        self.tools = {
            "navigate_to_url": navigate_to_url,
            "click_element": click_element,
            "type_text": type_text,
            "extract_page_content": extract_page_content,
            "take_screenshot": take_screenshot,
            "execute_javascript": execute_javascript,
            "wait_for_element": wait_for_element
        }
        self.graph = self._build_graph()
        self.memory = MemorySaver()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph."""
        workflow = StateGraph(BrowserAgentState)
        
        # Add nodes
        workflow.add_node("analyze_task", self._analyze_task)
        workflow.add_node("plan_actions", self._plan_actions)
        workflow.add_node("execute_action", self._execute_action)
        workflow.add_node("extract_data", self._extract_data)
        workflow.add_node("evaluate_progress", self._evaluate_progress)
        workflow.add_node("synthesize_results", self._synthesize_results)
        
        # Set entry point
        workflow.set_entry_point("analyze_task")
        
        # Add edges
        workflow.add_edge("analyze_task", "plan_actions")
        workflow.add_edge("plan_actions", "execute_action")
        workflow.add_edge("execute_action", "extract_data")
        workflow.add_edge("extract_data", "evaluate_progress")
        
        # Conditional routing from evaluate_progress
        workflow.add_conditional_edges(
            "evaluate_progress",
            self._should_continue,
            {
                "continue": "plan_actions",
                "complete": "synthesize_results",
                "error": END
            }
        )
        
        workflow.add_edge("synthesize_results", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _analyze_task(self, state: BrowserAgentState) -> BrowserAgentState:
        """Analyze the user's task and determine approach."""
        user_message = state["messages"][-1].content
        
        analysis_prompt = f"""Analyze this browser automation task:

Task: {user_message}

Determine:
1. What type of task this is (scraping, form filling, searching, etc.)
2. What URL(s) need to be visited
3. What data needs to be extracted or actions performed
4. Success criteria for the task

Provide a structured analysis."""
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert browser automation analyst."),
            HumanMessage(content=analysis_prompt)
        ])
        
        # Parse the response to extract key information
        analysis = response.content
        
        # Extract target URL if mentioned
        import re
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, user_message + " " + analysis)
        target_url = urls[0] if urls else None
        
        return {
            **state,
            "task": analysis,
            "target_url": target_url,
            "messages": state["messages"] + [AIMessage(content=f"Task analyzed: {analysis[:200]}...")]
        }
    
    async def _plan_actions(self, state: BrowserAgentState) -> BrowserAgentState:
        """Plan the next browser action based on current state."""
        
        planning_prompt = f"""Based on the current state, plan the next browser action:

Task: {state['task'][:500]}
Current URL: {state.get('current_url', 'Not navigated yet')}
Target URL: {state.get('target_url', 'Not specified')}
Actions taken: {len(state.get('actions_taken', []))}
Extracted data keys: {list(state.get('extracted_data', {}).keys())}

Available actions:
1. navigate_to_url(url) - Navigate to a URL
2. click_element(selector) - Click an element
3. type_text(selector, text) - Type text into a field
4. extract_page_content() - Extract page content
5. wait_for_element(selector) - Wait for element
6. execute_javascript(script) - Execute JavaScript
7. take_screenshot(filename) - Take screenshot

What should be the next action? Respond with:
ACTION: [action_name]
PARAMS: [parameters]
REASON: [why this action]"""
        
        response = self.llm.invoke([
            SystemMessage(content="You are a browser automation expert. Plan the next action."),
            HumanMessage(content=planning_prompt)
        ])
        
        return {
            **state,
            "messages": state["messages"] + [response]
        }
    
    async def _execute_action(self, state: BrowserAgentState) -> BrowserAgentState:
        """Execute the planned browser action."""
        last_message = state["messages"][-1].content
        
        # Parse action from message
        action = None
        params = {}
        
        if "navigate_to_url" in last_message.lower():
            if state.get("target_url"):
                action = "navigate_to_url"
                params = {"url": state["target_url"]}
        elif "extract" in last_message.lower():
            action = "extract_page_content"
            params = {}
        elif "click" in last_message.lower():
            # Extract selector from message
            if "selector:" in last_message.lower():
                selector = last_message.split("selector:")[-1].split("\n")[0].strip()
                action = "click_element"
                params = {"selector": selector}
        elif "type" in last_message.lower():
            # Extract selector and text
            if "selector:" in last_message.lower() and "text:" in last_message.lower():
                selector = last_message.split("selector:")[-1].split("\n")[0].strip()
                text = last_message.split("text:")[-1].split("\n")[0].strip()
                action = "type_text"
                params = {"selector": selector, "text": text}
        elif "screenshot" in last_message.lower():
            action = "take_screenshot"
            params = {"filename": f"screenshot_{len(state.get('actions_taken', []))}.png"}
        
        # Execute the action
        result = {"error": "No action identified"}
        if action and action in self.tools:
            try:
                tool_func = self.tools[action]
                result = await tool_func.ainvoke(params)
                
                # Update current URL if navigation succeeded
                if action == "navigate_to_url" and result.get("success"):
                    state["current_url"] = params["url"]
                
            except Exception as e:
                result = {"error": str(e)}
        
        # Record action
        actions_taken = state.get("actions_taken", [])
        actions_taken.append({
            "action": action,
            "params": params,
            "result": result
        })
        
        return {
            **state,
            "actions_taken": actions_taken,
            "messages": state["messages"] + [
                AIMessage(content=f"Executed {action}: {json.dumps(result)[:200]}")
            ]
        }
    
    async def _extract_data(self, state: BrowserAgentState) -> BrowserAgentState:
        """Extract data from the current page."""
        # Only extract if we're on a page
        if not state.get("current_url"):
            return state
        
        try:
            content = await extract_page_content.ainvoke({})
            
            # Add to extracted data
            extracted_data = state.get("extracted_data", {})
            extracted_data[state["current_url"]] = content
            
            return {
                **state,
                "extracted_data": extracted_data,
                "messages": state["messages"] + [
                    AIMessage(content=f"Extracted data from {state['current_url']}")
                ]
            }
        except Exception as e:
            return {
                **state,
                "error": str(e)
            }
    
    async def _evaluate_progress(self, state: BrowserAgentState) -> BrowserAgentState:
        """Evaluate if the task is complete or needs more actions."""
        
        evaluation_prompt = f"""Evaluate the progress on this browser task:

Original Task: {state['task'][:500]}
Actions Taken: {len(state.get('actions_taken', []))}
Data Extracted: {bool(state.get('extracted_data'))}
Current URL: {state.get('current_url')}
Last Action Result: {state['actions_taken'][-1] if state.get('actions_taken') else 'None'}

Is the task complete? Do we need more actions? Was there an error?

Respond with one of:
- COMPLETE: Task successfully completed
- CONTINUE: Need more actions
- ERROR: Task failed

Provide reasoning."""
        
        response = self.llm.invoke([
            SystemMessage(content="You are evaluating browser automation progress."),
            HumanMessage(content=evaluation_prompt)
        ])
        
        # Determine next step
        response_text = response.content.upper()
        if "COMPLETE" in response_text:
            state["task_complete"] = True
        elif "ERROR" in response_text:
            state["error"] = "Task evaluation indicated failure"
        
        return {
            **state,
            "messages": state["messages"] + [response]
        }
    
    def _should_continue(self, state: BrowserAgentState) -> str:
        """Determine next step based on evaluation."""
        if state.get("error"):
            return "error"
        elif state.get("task_complete"):
            return "complete"
        elif len(state.get("actions_taken", [])) > 10:  # Prevent infinite loops
            return "complete"
        else:
            return "continue"
    
    async def _synthesize_results(self, state: BrowserAgentState) -> BrowserAgentState:
        """Synthesize final results from the browser automation."""
        
        synthesis_prompt = f"""Synthesize the results of this browser automation task:

Task: {state['task'][:500]}
Actions Performed: {[a['action'] for a in state.get('actions_taken', [])]}
Data Extracted: {json.dumps(state.get('extracted_data', {}))[:1000]}

Provide a clear summary of:
1. What was accomplished
2. Key data extracted
3. Any issues encountered
4. Recommendations for next steps"""
        
        response = self.llm.invoke([
            SystemMessage(content="You are synthesizing browser automation results."),
            HumanMessage(content=synthesis_prompt)
        ])
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "task_complete": True
        }
    
    async def run(self, task: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Run the browser agent on a task."""
        if config is None:
            config = {"configurable": {"thread_id": "browser-session"}}
        
        initial_state = {
            "messages": [HumanMessage(content=task)],
            "task": "",
            "current_url": None,
            "target_url": None,
            "extracted_data": {},
            "actions_taken": [],
            "task_complete": False,
            "error": None
        }
        
        try:
            result = await self.graph.ainvoke(initial_state, config)
            return {
                "success": result.get("task_complete", False),
                "data": result.get("extracted_data", {}),
                "actions": result.get("actions_taken", []),
                "summary": result["messages"][-1].content if result["messages"] else "No summary"
            }
        finally:
            # Always cleanup browser
            await BrowserInstance.cleanup()


# ============================================================================
# High-Level API Functions
# ============================================================================

async def scrape_with_agent(url: str, instructions: str = "Extract all content") -> Dict[str, Any]:
    """
    Scrape a website using the intelligent browser agent.
    
    Args:
        url: URL to scrape
        instructions: Specific instructions for what to extract
    
    Returns:
        Extracted data and execution summary
    """
    agent = StealthBrowserAgent(temperature=0.3)
    task = f"Navigate to {url} and {instructions}"
    return await agent.run(task)


async def automate_task(task_description: str) -> Dict[str, Any]:
    """
    Automate a complex browser task using natural language.
    
    Args:
        task_description: Natural language description of the task
    
    Returns:
        Task results and execution summary
    """
    agent = StealthBrowserAgent(temperature=0.5)
    return await agent.run(task_description)


async def test_form_filling(url: str, form_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Test form filling on a website.
    
    Args:
        url: URL with the form
        form_data: Dictionary of field names/selectors and values
    
    Returns:
        Test results
    """
    agent = StealthBrowserAgent(temperature=0.3)
    
    form_instructions = f"Navigate to {url} and fill the form with: "
    for field, value in form_data.items():
        form_instructions += f"\n- {field}: {value}"
    
    return await agent.run(form_instructions)


# ============================================================================
# Demo and Testing
# ============================================================================

async def demo_agent():
    """Demonstrate the stealth browser agent capabilities."""
    print("=" * 70)
    print("STEALTH BROWSER AGENT DEMONSTRATION")
    print("=" * 70)
    
    # Example 1: Simple scraping
    print("\n[Example 1] Intelligent Web Scraping")
    print("-" * 40)
    
    result = await scrape_with_agent(
        "https://example.com",
        "Extract the main heading and any contact information"
    )
    
    print(f"Success: {result['success']}")
    print(f"Actions taken: {len(result['actions'])}")
    print(f"Summary: {result['summary'][:300]}...")
    
    # Example 2: Complex automation
    print("\n[Example 2] Complex Task Automation")
    print("-" * 40)
    
    result = await automate_task(
        "Search for 'Python' on Google, click the first result, and extract the page title and main content"
    )
    
    print(f"Success: {result['success']}")
    print(f"Actions taken: {[a['action'] for a in result['actions']]}")
    
    # Example 3: Form testing
    print("\n[Example 3] Form Filling Test")
    print("-" * 40)
    
    result = await test_form_filling(
        "https://example.com/contact",
        {
            "#name": "John Doe",
            "#email": "john@example.com",
            "#message": "Test message from browser agent"
        }
    )
    
    print(f"Form test result: {result['success']}")
    
    print("\n" + "=" * 70)
    print("AGENT CAPABILITIES DEMONSTRATED:")
    print("=" * 70)
    print("""
✅ Intelligent task analysis and planning
✅ Stealth browser control with anti-detection
✅ Dynamic action execution based on page state
✅ Content extraction and data synthesis
✅ Error handling and recovery
✅ Natural language task descriptions
✅ Complex multi-step automation
    """)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_agent())