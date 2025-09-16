"""Prompt engineering and building for browser agents"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from perception.models import WebPageState, InteractiveElement
from cognition.actions import AgentAction


class BrowserPrompts:
    """Collection of prompts for browser automation"""
    
    SYSTEM_PROMPT = """You are an AI browser automation agent. Your role is to navigate web pages and complete tasks by interacting with page elements.

You perceive the web page through:
1. A simplified text representation of the page content
2. An annotated screenshot showing numbered interactive elements
3. A list of interactive elements with their IDs and properties

You can perform actions like clicking, typing, scrolling, and navigating. Always think step-by-step about what you need to do to achieve the goal."""
    
    REACT_TEMPLATE = """## Current Task
{task}

## Page Information
**URL:** {url}
**Title:** {title}

## Simplified Page Content
{content}

## Interactive Elements
You can see an annotated screenshot with numbered elements. Here are the available interactive elements:
{elements}

## Previous Actions
{history}

## Current Situation Analysis
Think step-by-step:
1. What is my goal?
2. What is the current state of the page?
3. What progress have I made so far?
4. What is the logical next action?

Based on this analysis, determine the single next action to take. Respond with exactly ONE action in the structured format.

Remember:
- Use element IDs from the annotated screenshot
- Be specific in your justification
- If the task is complete, use the 'finished' action
- If you cannot proceed, use the 'failed' action"""
    
    PLANNER_TEMPLATE = """You are a task planning agent. Your role is to break down complex user requests into simple, concrete sub-tasks that can be executed on web pages.

## User Request
{user_request}

## Guidelines for Task Decomposition
1. Each sub-task should be:
   - Self-contained and achievable on a single page/site
   - Specific and unambiguous
   - Ordered logically
   - Actionable (can be completed through browser interactions)

2. Consider common patterns like:
   - Navigation to the right page first
   - Authentication if needed
   - Form filling in order
   - Verification of results

3. Break down complex actions into steps

## Example Decomposition
User: "Book a flight from NYC to LA for next Friday"
Sub-tasks:
1. Navigate to flight booking website
2. Enter "New York" as departure city
3. Enter "Los Angeles" as destination city
4. Select next Friday as travel date
5. Search for available flights
6. Select the most suitable flight
7. Proceed to booking

Now decompose the user's request into sub-tasks:"""
    
    CORRECTION_TEMPLATE = """## Attention: Previous Action Failed

**Error Details:**
- Action attempted: {action_type}
- Element/Target: {target}
- Error type: {error_type}
- Error message: {error_message}

**Wait**, my previous action failed. Let me reconsider the situation.

Looking at the page again, I need to find an alternative approach. The error suggests that {error_analysis}.

Let me try a different strategy:"""
    
    VISION_ANALYSIS_TEMPLATE = """Analyze this annotated screenshot of a web page.

## Task
{task}

## What to identify:
1. The numbered red labels mark interactive elements
2. Identify which element would help achieve the task
3. Consider the visual layout and element positions
4. Look for relevant text, buttons, links, or input fields

## Current Context
{context}

Based on the visual analysis, which numbered element should be interacted with next, and what action should be taken?"""
    
    DATA_EXTRACTION_TEMPLATE = """Extract structured data from this web page.

## Extraction Goal
{extraction_goal}

## Page Content
{content}

## Extraction Schema
{schema}

Extract the requested information and structure it according to the schema. Return only the extracted data in the specified format."""

    NAVIGATION_STRATEGY_TEMPLATE = """Determine the navigation strategy to reach the target page.

## Current Location
URL: {current_url}
Page Type: {page_type}

## Target
{target_description}

## Available Navigation Elements
{navigation_elements}

## Strategy Considerations
1. Is the target on the same domain?
2. Can we use direct URL navigation?
3. Should we use site navigation menus?
4. Do we need to use search functionality?

Recommend the best navigation approach."""


class PromptBuilder:
    """Builds prompts for various agent scenarios"""
    
    def __init__(self):
        self.prompts = BrowserPrompts()
    
    def build_react_prompt(self, task: str, state: WebPageState,
                          history: List[Dict[str, Any]],
                          max_content_length: int = 3000,
                          max_elements: int = 30) -> str:
        """Build ReAct prompt for browser agent"""
        
        # Truncate content if needed
        content = state.dom_structure.distilled_content
        if len(content) > max_content_length:
            content = content[:max_content_length] + "... [truncated]"
        
        # Format interactive elements
        elements_text = self._format_elements(
            state.interactive_elements[:max_elements]
        )
        
        if len(state.interactive_elements) > max_elements:
            elements_text += f"\n... and {len(state.interactive_elements) - max_elements} more elements"
        
        # Format history
        history_text = self._format_history(history[-5:] if history else [])
        
        return self.prompts.REACT_TEMPLATE.format(
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            content=content,
            elements=elements_text,
            history=history_text
        )
    
    def build_planner_prompt(self, user_request: str) -> str:
        """Build prompt for task planning"""
        return self.prompts.PLANNER_TEMPLATE.format(
            user_request=user_request
        )
    
    def build_correction_prompt(self, base_prompt: str, error_info: Dict[str, Any]) -> str:
        """Build prompt for error correction"""
        
        # Analyze error
        error_analysis = self._analyze_error(error_info)
        
        correction = self.prompts.CORRECTION_TEMPLATE.format(
            action_type=error_info.get('action_type', 'unknown'),
            target=error_info.get('target', 'unknown'),
            error_type=error_info.get('error_type', 'unknown'),
            error_message=error_info.get('error_message', 'No details available'),
            error_analysis=error_analysis
        )
        
        return base_prompt + "\n\n" + correction
    
    def build_vision_prompt(self, task: str, context: str = "") -> str:
        """Build prompt for visual analysis"""
        return self.prompts.VISION_ANALYSIS_TEMPLATE.format(
            task=task,
            context=context or "Starting fresh on this page."
        )
    
    def build_extraction_prompt(self, goal: str, content: str,
                               schema: Dict[str, Any]) -> str:
        """Build prompt for data extraction"""
        import json
        
        schema_str = json.dumps(schema, indent=2)
        
        return self.prompts.DATA_EXTRACTION_TEMPLATE.format(
            extraction_goal=goal,
            content=content,
            schema=schema_str
        )
    
    def build_navigation_prompt(self, current_url: str, target: str,
                              nav_elements: List[InteractiveElement]) -> str:
        """Build prompt for navigation strategy"""
        
        # Determine page type
        page_type = self._identify_page_type(current_url)
        
        # Format navigation elements
        nav_text = self._format_navigation_elements(nav_elements)
        
        return self.prompts.NAVIGATION_STRATEGY_TEMPLATE.format(
            current_url=current_url,
            page_type=page_type,
            target_description=target,
            navigation_elements=nav_text
        )
    
    def _format_elements(self, elements: List[InteractiveElement]) -> str:
        """Format interactive elements for prompt"""
        lines = []
        
        for elem in elements:
            # Build element description
            desc_parts = [f"[{elem.id}]"]
            
            # Add type
            desc_parts.append(f"{elem.type}:")
            
            # Add text or key attributes
            if elem.text:
                desc_parts.append(f'"{elem.text[:50]}"')
            elif elem.aria_label:
                desc_parts.append(f'aria-label="{elem.aria_label}"')
            elif elem.placeholder:
                desc_parts.append(f'placeholder="{elem.placeholder}"')
            elif elem.value:
                desc_parts.append(f'value="{elem.value[:30]}"')
            else:
                desc_parts.append(f"<{elem.tag_name}>")
            
            # Add state info
            states = []
            if not elem.is_visible:
                states.append("hidden")
            if not elem.is_enabled:
                states.append("disabled")
            if elem.is_checked:
                states.append("checked")
            
            if states:
                desc_parts.append(f"({', '.join(states)})")
            
            lines.append(" ".join(desc_parts))
        
        return "\n".join(lines)
    
    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format action history for prompt"""
        if not history:
            return "No previous actions taken yet."
        
        lines = []
        for i, entry in enumerate(history, 1):
            action = entry.get('action', {})
            result = entry.get('result', {})
            
            # Format action
            action_type = action.get('action', action.get('type', 'unknown'))
            action_desc = f"{i}. {action_type}"
            
            # Add action details
            if action_type == "click":
                action_desc += f" on element {action.get('element_id', '?')}"
            elif action_type == "type" or action_type == "fill":
                text = action.get('text_to_type', action.get('text', ''))
                action_desc += f' "{text[:30]}"' if text else ""
            elif action_type == "navigate":
                action_desc += f" to {action.get('url', '?')}"
            
            # Add result
            if result.get('success'):
                action_desc += " ✓"
            else:
                action_desc += f" ✗ ({result.get('error', 'failed')})"
            
            lines.append(action_desc)
        
        return "\n".join(lines)
    
    def _analyze_error(self, error_info: Dict[str, Any]) -> str:
        """Analyze error and provide insight"""
        error_type = error_info.get('error_type', '').lower()
        error_msg = error_info.get('error_message', '').lower()
        
        if 'not found' in error_msg or 'element' in error_msg:
            return "the element might not exist, be hidden, or have a different ID"
        elif 'timeout' in error_msg:
            return "the page might still be loading or the element is not becoming available"
        elif 'not clickable' in error_msg or 'intercepted' in error_msg:
            return "another element might be covering it, or it might need to be scrolled into view"
        elif 'navigation' in error_msg:
            return "the URL might be invalid or the page failed to load"
        else:
            return "there might be an unexpected page state or the action parameters are incorrect"
    
    def _identify_page_type(self, url: str) -> str:
        """Identify the type of page from URL"""
        url_lower = url.lower()
        
        if 'login' in url_lower or 'signin' in url_lower:
            return "Login page"
        elif 'search' in url_lower:
            return "Search page"
        elif 'checkout' in url_lower or 'cart' in url_lower:
            return "Shopping cart/checkout"
        elif 'product' in url_lower or 'item' in url_lower:
            return "Product page"
        elif url_lower.endswith('/') or 'index' in url_lower or 'home' in url_lower:
            return "Homepage"
        else:
            return "Content page"
    
    def _format_navigation_elements(self, elements: List[InteractiveElement]) -> str:
        """Format navigation-specific elements"""
        nav_elements = [
            elem for elem in elements
            if elem.type in ['link', 'button'] or 
            'nav' in elem.tag_name.lower() or
            'menu' in str(elem.attributes.get('class', '')).lower()
        ]
        
        return self._format_elements(nav_elements[:15])  # Limit to 15 nav elements
    
    def build_reasoning_prompt(
        self,
        task: str,
        current_state: WebPageState,
        conversation_history: List[Dict[str, Any]],
        reasoning_steps: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for ReAct reasoning step"""
        
        reasoning_template = """## ReAct Reasoning Step

### Current Task
{task}

### Current Page State
**URL:** {url}
**Title:** {title}

### Simplified Page Content
{content}

### Interactive Elements Available
{elements}

### Recent Conversation History
{history}

### Previous Reasoning Steps
{steps}

### Your Task: Generate Reasoning
Think step by step about the current situation:

1. **Current State Analysis**: What is happening on this page right now?
2. **Progress Assessment**: What progress have I made toward the goal?
3. **Next Steps Planning**: What should be the logical next action?
4. **Potential Issues**: What could go wrong or needs special attention?

Provide your reasoning in a clear, logical manner:"""

        # Format content (truncated)
        content = current_state.dom_structure.distilled_content
        if len(content) > 2000:
            content = content[:2000] + "... [truncated]"
        
        # Format elements
        elements_text = self._format_elements(current_state.interactive_elements[:20])
        
        # Format history
        history_text = self._format_conversation_history(conversation_history)
        
        # Format reasoning steps
        steps_text = self._format_reasoning_steps(reasoning_steps)
        
        return reasoning_template.format(
            task=task,
            url=current_state.metadata.url,
            title=current_state.metadata.title,
            content=content,
            elements=elements_text,
            history=history_text,
            steps=steps_text
        )
    
    def build_action_prompt(
        self,
        task: str,
        reasoning: str,
        state: WebPageState,
        history: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for action generation based on reasoning"""
        
        action_template = """## Action Generation

### Task
{task}

### Current Reasoning
{reasoning}

### Current Page State
**URL:** {url}
**Title:** {title}

### Available Interactive Elements
{elements}

### Recent Action History
{history}

### Your Task: Generate Action
Based on your reasoning above, determine the single best next action.

Consider:
1. Which element (if any) should be interacted with?
2. What type of action is most appropriate?
3. What parameters are needed for the action?
4. How confident are you in this action choice?

Respond with exactly ONE action in the structured format."""

        # Format elements
        elements_text = self._format_elements(state.interactive_elements[:25])
        
        # Format action history
        history_text = self._format_reasoning_history(history)
        
        return action_template.format(
            task=task,
            reasoning=reasoning,
            url=state.metadata.url,
            title=state.metadata.title,
            elements=elements_text,
            history=history_text
        )
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for reasoning prompts"""
        if not history:
            return "No recent conversation history."
        
        lines = []
        for i, entry in enumerate(history, 1):
            task = entry.get("task", "Unknown task")
            success = entry.get("success", False)
            duration = entry.get("duration", 0)
            
            status = "✓ Success" if success else "✗ Failed"
            lines.append(f"{i}. {task[:60]}... [{status}, {duration:.1f}s]")
        
        return "\n".join(lines)
    
    def _format_reasoning_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Format previous reasoning steps"""
        if not steps:
            return "No previous reasoning steps in this session."
        
        lines = []
        for step in steps:
            step_num = step.get("step_number", "?")
            thought = step.get("thought", "No thought recorded")
            action = step.get("action", {})
            observation = step.get("observation", "No observation")
            
            lines.append(f"Step {step_num}:")
            lines.append(f"  Thought: {thought[:100]}...")
            if action:
                action_type = action.get("action", "unknown")
                lines.append(f"  Action: {action_type}")
            lines.append(f"  Observation: {observation[:100]}...")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_reasoning_history(self, history: List[Dict[str, Any]]) -> str:
        """Format reasoning step history for action prompts"""
        if not history:
            return "No previous actions in this reasoning session."
        
        lines = []
        for step in history[-3:]:  # Last 3 steps
            step_num = step.get("step_number", "?")
            action = step.get("action")
            observation = step.get("observation", "No observation")
            
            if action:
                action_type = action.get("action", "unknown")
                lines.append(f"Step {step_num}: {action_type} -> {observation[:80]}...")
            else:
                lines.append(f"Step {step_num}: No action -> {observation[:80]}...")
        
        return "\n".join(lines)