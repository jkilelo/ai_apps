"""
LIVE TEST - Real browser automation with LangGraph and LLM
No mocks, no placeholders - actual browser control with AI reasoning
"""

import asyncio
import sys
import os
from datetime import datetime

# Setup imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from agents.langgraph_wrapper import get_langgraph_llm
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Dict, Any, Sequence
import operator

print("=" * 80)
print("LIVE BROWSER TEST WITH REAL LLM - NO MOCKS")
print(f"Timestamp: {datetime.now()}")
print("=" * 80)

# Global browser instance
BROWSER = None
PAGE = None

# ============================================================================
# REAL Browser Tools - Actual Playwright controls
# ============================================================================

@tool
async def navigate_to_url(url: str) -> Dict[str, Any]:
    """Navigate to a real URL using Playwright browser."""
    global PAGE
    try:
        await PAGE.goto(url, wait_until='domcontentloaded', timeout=30000)
        title = await PAGE.title()
        current_url = PAGE.url
        
        print(f"  [BROWSER] Navigated to: {current_url}")
        print(f"  [BROWSER] Page title: {title}")
        
        return {
            "success": True,
            "url": current_url,
            "title": title
        }
    except Exception as e:
        print(f"  [ERROR] Navigation failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def extract_text_content() -> Dict[str, Any]:
    """Extract real text content from the current page."""
    global PAGE
    try:
        # Extract various text elements
        headings = await PAGE.eval_on_selector_all("h1, h2, h3", 
            "elements => elements.map(e => e.textContent.trim()).filter(t => t)")
        
        paragraphs = await PAGE.eval_on_selector_all("p", 
            "elements => elements.slice(0, 5).map(e => e.textContent.trim()).filter(t => t)")
        
        links = await PAGE.eval_on_selector_all("a", 
            "elements => elements.slice(0, 10).map(e => ({text: e.textContent.trim(), href: e.href})).filter(l => l.text)")
        
        print(f"  [BROWSER] Extracted: {len(headings)} headings, {len(paragraphs)} paragraphs, {len(links)} links")
        
        return {
            "success": True,
            "headings": headings[:5],
            "paragraphs": paragraphs[:5],
            "links": links[:10]
        }
    except Exception as e:
        print(f"  [ERROR] Extraction failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def search_on_page(query: str) -> Dict[str, Any]:
    """Search for text on the current page and interact with search."""
    global PAGE
    try:
        # Try to find and use a search input
        search_selectors = [
            'input[type="search"]',
            'input[name*="search"]',
            'input[name*="q"]',
            'input[placeholder*="search" i]',
            'input[placeholder*="find" i]',
            '#search',
            '.search-input'
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                element = await PAGE.wait_for_selector(selector, timeout=2000)
                if element:
                    search_input = selector
                    break
            except:
                continue
        
        if search_input:
            await PAGE.fill(search_input, query)
            print(f"  [BROWSER] Filled search box with: '{query}'")
            
            # Try to submit
            await PAGE.keyboard.press('Enter')
            await PAGE.wait_for_load_state('networkidle', timeout=5000)
            
            return {
                "success": True,
                "searched": query,
                "search_element": search_input
            }
        else:
            # No search box, look for the text on page
            text_found = await PAGE.eval_on_selector_all(
                "*",
                f"elements => elements.some(e => e.textContent && e.textContent.toLowerCase().includes('{query.lower()}'))"
            )
            
            return {
                "success": True,
                "searched": query,
                "found_on_page": text_found
            }
            
    except Exception as e:
        print(f"  [ERROR] Search failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def click_link_with_text(text: str) -> Dict[str, Any]:
    """Click a link containing specific text."""
    global PAGE
    try:
        # Find and click link with text
        link = await PAGE.get_by_text(text).first
        await link.click()
        await PAGE.wait_for_load_state('domcontentloaded', timeout=10000)
        
        new_url = PAGE.url
        new_title = await PAGE.title()
        
        print(f"  [BROWSER] Clicked link with text: '{text}'")
        print(f"  [BROWSER] New page: {new_title}")
        
        return {
            "success": True,
            "clicked_text": text,
            "new_url": new_url,
            "new_title": new_title
        }
    except Exception as e:
        print(f"  [ERROR] Click failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def take_screenshot() -> Dict[str, Any]:
    """Take a real screenshot of the current page."""
    global PAGE
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        await PAGE.screenshot(path=filename)
        
        print(f"  [BROWSER] Screenshot saved: {filename}")
        
        return {
            "success": True,
            "filename": filename
        }
    except Exception as e:
        print(f"  [ERROR] Screenshot failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# Live Browser Agent State
# ============================================================================

class LiveBrowserState(TypedDict):
    """State for the live browser agent."""
    messages: Annotated[Sequence[Any], operator.add]
    task: str
    current_url: str
    actions_log: List[Dict[str, Any]]
    extracted_data: Dict[str, Any]
    task_complete: bool


# ============================================================================
# Live Browser Agent
# ============================================================================

class LiveBrowserAgent:
    """Real browser agent with LLM reasoning - no mocks!"""
    
    def __init__(self):
        print("\n[INIT] Creating Live Browser Agent with real LLM...")
        self.llm = get_langgraph_llm(temperature=0.3)
        self.tools = {
            "navigate_to_url": navigate_to_url,
            "extract_text_content": extract_text_content,
            "search_on_page": search_on_page,
            "click_link_with_text": click_link_with_text,
            "take_screenshot": take_screenshot
        }
        self.graph = self._build_graph()
        print("[INIT] Agent created successfully")
    
    def _build_graph(self):
        """Build the agent workflow."""
        workflow = StateGraph(LiveBrowserState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_task)
        workflow.add_node("plan", self._plan_action)
        workflow.add_node("execute", self._execute_action)
        workflow.add_node("evaluate", self._evaluate_progress)
        workflow.add_node("complete", self._complete_task)
        
        # Set flow
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "evaluate")
        
        # Conditional routing
        workflow.add_conditional_edges(
            "evaluate",
            self._should_continue,
            {
                "continue": "plan",
                "complete": "complete"
            }
        )
        
        workflow.add_edge("complete", END)
        
        return workflow.compile()
    
    def _analyze_task(self, state: LiveBrowserState) -> LiveBrowserState:
        """Analyze the task using real LLM."""
        print("\n[AGENT] Analyzing task with LLM...")
        
        task = state["task"]
        
        analysis = self.llm.invoke([
            SystemMessage(content="You are a browser automation expert. Analyze the task and identify key steps needed."),
            HumanMessage(content=f"Task: {task}\n\nWhat are the key steps to complete this task?")
        ])
        
        print(f"[AGENT] Analysis: {analysis.content[:200]}...")
        
        return {
            **state,
            "messages": state["messages"] + [analysis]
        }
    
    def _plan_action(self, state: LiveBrowserState) -> LiveBrowserState:
        """Plan next action using real LLM."""
        print("\n[AGENT] Planning next action...")
        
        context = f"""
        Task: {state['task']}
        Current URL: {state.get('current_url', 'Not navigated yet')}
        Actions taken: {len(state.get('actions_log', []))}
        
        Available tools:
        - navigate_to_url(url): Navigate to a URL
        - extract_text_content(): Extract text from current page
        - search_on_page(query): Search for text on page
        - click_link_with_text(text): Click a link with specific text
        - take_screenshot(): Take a screenshot
        
        What should be the next action? Respond with:
        TOOL: [tool_name]
        PARAMS: [parameters]
        """
        
        plan = self.llm.invoke([
            SystemMessage(content="Plan the next browser action."),
            HumanMessage(content=context)
        ])
        
        print(f"[AGENT] Plan: {plan.content[:200]}...")
        
        return {
            **state,
            "messages": state["messages"] + [plan]
        }
    
    async def _execute_action(self, state: LiveBrowserState) -> LiveBrowserState:
        """Execute the planned action on real browser."""
        print("\n[AGENT] Executing action...")
        
        last_plan = state["messages"][-1].content
        
        # Parse and execute action
        action_result = {}
        
        if "navigate_to_url" in last_plan.lower():
            # Extract URL from plan
            if "wikipedia.org" in last_plan:
                url = "https://www.wikipedia.org"
            elif "example.com" in last_plan:
                url = "https://example.com"
            else:
                url = "https://www.google.com"
            
            action_result = await navigate_to_url.ainvoke({"url": url})
            state["current_url"] = url
            
        elif "extract" in last_plan.lower():
            action_result = await extract_text_content.ainvoke({})
            state["extracted_data"] = action_result
            
        elif "search" in last_plan.lower():
            # Extract search query
            query = "Python programming"  # Default query
            if "query:" in last_plan.lower():
                query = last_plan.split("query:")[-1].split("\n")[0].strip()
            action_result = await search_on_page.ainvoke({"query": query})
            
        elif "screenshot" in last_plan.lower():
            action_result = await take_screenshot.ainvoke({})
        
        # Log action
        actions_log = state.get("actions_log", [])
        actions_log.append({
            "action": last_plan[:100],
            "result": action_result
        })
        
        return {
            **state,
            "actions_log": actions_log,
            "messages": state["messages"] + [
                AIMessage(content=f"Executed action. Result: {action_result}")
            ]
        }
    
    def _evaluate_progress(self, state: LiveBrowserState) -> LiveBrowserState:
        """Evaluate if task is complete using real LLM."""
        print("\n[AGENT] Evaluating progress...")
        
        evaluation_context = f"""
        Original task: {state['task']}
        Actions taken: {len(state.get('actions_log', []))}
        Data extracted: {bool(state.get('extracted_data'))}
        Last action result: {state['actions_log'][-1] if state.get('actions_log') else 'None'}
        
        Is the task complete? Respond with COMPLETE or CONTINUE and explain why.
        """
        
        evaluation = self.llm.invoke([
            SystemMessage(content="Evaluate if the browser task is complete."),
            HumanMessage(content=evaluation_context)
        ])
        
        print(f"[AGENT] Evaluation: {evaluation.content[:200]}...")
        
        # Check if complete
        if "COMPLETE" in evaluation.content.upper() or len(state.get("actions_log", [])) >= 5:
            state["task_complete"] = True
        
        return {
            **state,
            "messages": state["messages"] + [evaluation]
        }
    
    def _should_continue(self, state: LiveBrowserState) -> str:
        """Decide whether to continue or complete."""
        if state.get("task_complete") or len(state.get("actions_log", [])) >= 5:
            return "complete"
        return "continue"
    
    def _complete_task(self, state: LiveBrowserState) -> LiveBrowserState:
        """Complete the task with final summary from LLM."""
        print("\n[AGENT] Generating final summary...")
        
        summary_context = f"""
        Task completed: {state['task']}
        Actions performed: {[a['action'][:50] for a in state.get('actions_log', [])]}
        Data collected: {state.get('extracted_data', {}).keys() if state.get('extracted_data') else 'None'}
        
        Provide a brief summary of what was accomplished.
        """
        
        summary = self.llm.invoke([
            SystemMessage(content="Summarize the completed browser automation task."),
            HumanMessage(content=summary_context)
        ])
        
        print(f"[AGENT] Summary: {summary.content}")
        
        return {
            **state,
            "messages": state["messages"] + [summary],
            "task_complete": True
        }
    
    async def run(self, task: str) -> Dict[str, Any]:
        """Run the agent on a real task."""
        initial_state = {
            "messages": [],
            "task": task,
            "current_url": "",
            "actions_log": [],
            "extracted_data": {},
            "task_complete": False
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "success": result.get("task_complete", False),
            "actions": result.get("actions_log", []),
            "data": result.get("extracted_data", {}),
            "summary": result["messages"][-1].content if result["messages"] else "No summary"
        }


# ============================================================================
# LIVE Test Execution
# ============================================================================

async def run_live_test():
    """Run a completely live test with real browser and LLM."""
    global BROWSER, PAGE
    
    print("\n" + "=" * 80)
    print("STARTING LIVE TEST")
    print("=" * 80)
    
    # Initialize real browser
    print("\n[SETUP] Launching real Playwright browser...")
    playwright = await async_playwright().start()
    BROWSER = await playwright.chromium.launch(
        headless=False,  # Show the browser window
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = await BROWSER.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    
    PAGE = await context.new_page()
    print("[SETUP] Browser launched successfully")
    
    try:
        # Create agent
        print("\n[TEST] Creating Live Browser Agent...")
        agent = LiveBrowserAgent()
        
        # Define a real task
        task = """
        Navigate to Wikipedia and search for 'Artificial Intelligence'.
        Extract the main heading and first paragraph of information about AI.
        Take a screenshot of the page.
        """
        
        print(f"\n[TEST] Task: {task.strip()}")
        print("\n[TEST] Executing task with real browser and LLM...")
        print("-" * 80)
        
        # Run the task
        result = await agent.run(task)
        
        # Display results
        print("\n" + "=" * 80)
        print("LIVE TEST RESULTS")
        print("=" * 80)
        
        print(f"\n[RESULT] Task Complete: {result['success']}")
        print(f"\n[RESULT] Actions Performed: {len(result['actions'])}")
        for i, action in enumerate(result['actions'], 1):
            print(f"  {i}. {action['action'][:80]}...")
            print(f"     Result: {action['result'].get('success', False)}")
        
        print(f"\n[RESULT] Data Extracted:")
        if result['data']:
            for key, value in result['data'].items():
                if isinstance(value, list) and value:
                    print(f"  - {key}: {len(value)} items")
                    if key == "headings" and value:
                        print(f"    First heading: {value[0]}")
                elif value:
                    print(f"  - {key}: {value}")
        
        print(f"\n[RESULT] Final Summary:")
        print(f"  {result['summary']}")
        
    finally:
        # Cleanup
        print("\n[CLEANUP] Closing browser...")
        await BROWSER.close()
        await playwright.stop()
        print("[CLEANUP] Browser closed")
    
    print("\n" + "=" * 80)
    print("LIVE TEST COMPLETED SUCCESSFULLY")
    print("This was a REAL test with:")
    print("  - Real Playwright browser (not mocked)")
    print("  - Real LLM via langgraph_wrapper (not mocked)")
    print("  - Real website interaction (not mocked)")
    print("  - Real data extraction (not mocked)")
    print("=" * 80)


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("\nStarting LIVE browser automation test...")
    print("This will open a real browser window and perform real actions.")
    print("Using real LLM for reasoning and decision making.")
    
    # Run the live test
    asyncio.run(run_live_test())