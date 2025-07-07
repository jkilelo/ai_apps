"""
Self-Healing Test Generator
Generates resilient test cases that automatically adapt to UI changes
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class LocatorStrategy(Enum):
    """Locator strategies in order of preference"""
    ID = "id"
    DATA_TESTID = "data-testid"
    ARIA_LABEL = "aria-label"
    NAME = "name"
    PLACEHOLDER = "placeholder"
    ROLE_TEXT = "role+text"
    TEXT = "text"
    PARTIAL_TEXT = "partial_text"
    CSS = "css"
    XPATH = "xpath"
    NEARBY = "nearby"
    VISUAL = "visual"
    AI_DESCRIPTION = "ai_description"


@dataclass
class ResilientLocator:
    """Multi-strategy locator for self-healing"""
    primary: Dict[str, str]
    fallbacks: List[Dict[str, str]]
    confidence_scores: Dict[str, float]
    element_signature: str
    context: Dict[str, Any]


@dataclass
class TestStep:
    """Individual test step with self-healing capabilities"""
    action: str  # click, type, select, etc.
    locator: ResilientLocator
    data: Optional[Any] = None
    assertions: List[Dict[str, Any]] = None
    wait_condition: Optional[str] = None
    retry_count: int = 3
    timeout: int = 10000


@dataclass
class SelfHealingTest:
    """Complete self-healing test case"""
    test_id: str
    test_name: str
    description: str
    preconditions: List[str]
    steps: List[TestStep]
    expected_results: List[str]
    test_data: Dict[str, Any]
    tags: List[str]
    priority: str
    healing_history: List[Dict[str, Any]]


class SelfHealingTestGenerator:
    """Generates test cases with self-healing capabilities"""
    
    # Template for self-healing Playwright test
    PLAYWRIGHT_TEST_TEMPLATE = """
import asyncio
from playwright.async_api import Page, Locator
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


class SelfHealingPage:
    \"\"\"Page object with self-healing locator capabilities\"\"\"
    
    def __init__(self, page: Page):
        self.page = page
        self.healing_history = []
        
    async def locate_with_healing(self, locator_config: Dict[str, Any]) -> Optional[Locator]:
        \"\"\"Find element using primary and fallback strategies\"\"\"
        primary = locator_config['primary']
        fallbacks = locator_config['fallbacks']
        
        # Try primary locator
        element = await self._try_locator(primary)
        if element and await element.is_visible():
            return element
            
        # Try fallback locators
        for fallback in fallbacks:
            logger.info(f"Trying fallback locator: {fallback['strategy']}")
            element = await self._try_locator(fallback)
            if element and await element.is_visible():
                self._record_healing(primary, fallback)
                return element
                
        # Last resort: AI-based location
        if 'ai_description' in locator_config:
            element = await self._locate_by_ai(locator_config['ai_description'])
            if element:
                self._record_healing(primary, {'strategy': 'ai', 'description': locator_config['ai_description']})
                return element
                
        return None
        
    async def _try_locator(self, locator: Dict[str, str]) -> Optional[Locator]:
        \"\"\"Try a specific locator strategy\"\"\"
        try:
            strategy = locator['strategy']
            value = locator['value']
            
            if strategy == 'id':
                return self.page.locator(f'#{value}')
            elif strategy == 'data-testid':
                return self.page.locator(f'[data-testid="{value}"]')
            elif strategy == 'aria-label':
                return self.page.locator(f'[aria-label="{value}"]')
            elif strategy == 'role+text':
                role, text = value.split(':', 1)
                return self.page.get_by_role(role, name=text)
            elif strategy == 'text':
                return self.page.get_by_text(value, exact=True)
            elif strategy == 'partial_text':
                return self.page.get_by_text(value)
            elif strategy == 'css':
                return self.page.locator(value)
            elif strategy == 'xpath':
                return self.page.locator(f'xpath={value}')
            elif strategy == 'placeholder':
                return self.page.get_by_placeholder(value)
            else:
                return None
        except Exception as e:
            logger.debug(f"Locator failed: {e}")
            return None
            
    async def _locate_by_ai(self, description: str) -> Optional[Locator]:
        \"\"\"Use AI to find element based on description\"\"\"
        # This would integrate with an AI service
        # For now, return None
        logger.info(f"AI location not implemented for: {description}")
        return None
        
    def _record_healing(self, original: Dict[str, str], healed: Dict[str, str]):
        \"\"\"Record healing action for reporting\"\"\"
        self.healing_history.append({
            'timestamp': datetime.now().isoformat(),
            'original': original,
            'healed': healed
        })


async def test_{test_name}(page: Page):
    \"\"\"
    {test_description}
    
    Test ID: {test_id}
    Priority: {priority}
    Tags: {tags}
    \"\"\"
    healing_page = SelfHealingPage(page)
    
    # Test data
    test_data = {test_data}
    
    # Preconditions
    {preconditions}
    
    try:
        # Test steps
        {test_steps}
        
        # Assertions
        {assertions}
        
        logger.info("Test passed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        # Save healing history for analysis
        if healing_page.healing_history:
            with open(f'healing_history_{test_id}.json', 'w') as f:
                json.dump(healing_page.healing_history, f, indent=2)
        raise
    
    finally:
        # Cleanup
        pass
"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.healing_stats = {
            "total_healed": 0,
            "healing_by_strategy": {},
            "common_failures": []
        }
    
    def generate_resilient_locator(self, element: Dict[str, Any]) -> ResilientLocator:
        """Generate multi-strategy locator for an element"""
        
        locators = []
        confidence_scores = {}
        
        # ID - highest confidence
        if element.get("id"):
            locators.append({
                "strategy": LocatorStrategy.ID.value,
                "value": element["id"]
            })
            confidence_scores[LocatorStrategy.ID.value] = 0.95
        
        # Data-testid - very reliable
        if element.get("data-testid") or element.get("attributes", {}).get("data-testid"):
            testid = element.get("data-testid") or element["attributes"]["data-testid"]
            locators.append({
                "strategy": LocatorStrategy.DATA_TESTID.value,
                "value": testid
            })
            confidence_scores[LocatorStrategy.DATA_TESTID.value] = 0.90
        
        # ARIA label - good for accessibility
        if element.get("aria_label"):
            locators.append({
                "strategy": LocatorStrategy.ARIA_LABEL.value,
                "value": element["aria_label"]
            })
            confidence_scores[LocatorStrategy.ARIA_LABEL.value] = 0.85
        
        # Name attribute
        if element.get("name"):
            locators.append({
                "strategy": LocatorStrategy.NAME.value,
                "value": element["name"]
            })
            confidence_scores[LocatorStrategy.NAME.value] = 0.80
        
        # Placeholder
        if element.get("placeholder"):
            locators.append({
                "strategy": LocatorStrategy.PLACEHOLDER.value,
                "value": element["placeholder"]
            })
            confidence_scores[LocatorStrategy.PLACEHOLDER.value] = 0.75
        
        # Role + Text combination
        if element.get("role") and element.get("text"):
            locators.append({
                "strategy": LocatorStrategy.ROLE_TEXT.value,
                "value": f"{element['role']}:{element['text']}"
            })
            confidence_scores[LocatorStrategy.ROLE_TEXT.value] = 0.70
        
        # Text content
        if element.get("text") and len(element["text"]) > 3:
            locators.append({
                "strategy": LocatorStrategy.TEXT.value,
                "value": element["text"]
            })
            confidence_scores[LocatorStrategy.TEXT.value] = 0.65
            
            # Also add partial text
            if len(element["text"]) > 10:
                partial = element["text"][:20].strip()
                locators.append({
                    "strategy": LocatorStrategy.PARTIAL_TEXT.value,
                    "value": partial
                })
                confidence_scores[LocatorStrategy.PARTIAL_TEXT.value] = 0.60
        
        # CSS selector - less reliable but always available
        if element.get("css_selector"):
            locators.append({
                "strategy": LocatorStrategy.CSS.value,
                "value": element["css_selector"]
            })
            confidence_scores[LocatorStrategy.CSS.value] = 0.50
        
        # XPath - last resort for DOM
        if element.get("xpath"):
            locators.append({
                "strategy": LocatorStrategy.XPATH.value,
                "value": element["xpath"]
            })
            confidence_scores[LocatorStrategy.XPATH.value] = 0.40
        
        # Nearby element strategy
        if element.get("nearby_text"):
            locators.append({
                "strategy": LocatorStrategy.NEARBY.value,
                "value": json.dumps({
                    "near": element["nearby_text"],
                    "type": element.get("type", "element")
                })
            })
            confidence_scores[LocatorStrategy.NEARBY.value] = 0.55
        
        # Visual locator (if screenshot available)
        if element.get("visual_signature"):
            locators.append({
                "strategy": LocatorStrategy.VISUAL.value,
                "value": element["visual_signature"]
            })
            confidence_scores[LocatorStrategy.VISUAL.value] = 0.45
        
        # AI description fallback
        ai_description = self._generate_ai_description(element)
        locators.append({
            "strategy": LocatorStrategy.AI_DESCRIPTION.value,
            "value": ai_description
        })
        confidence_scores[LocatorStrategy.AI_DESCRIPTION.value] = 0.35
        
        # Select primary locator (highest confidence)
        locators.sort(key=lambda x: confidence_scores.get(x["strategy"], 0), reverse=True)
        primary = locators[0] if locators else {"strategy": "css", "value": "*"}
        fallbacks = locators[1:] if len(locators) > 1 else []
        
        # Generate element signature for tracking
        signature = self._generate_element_signature(element)
        
        return ResilientLocator(
            primary=primary,
            fallbacks=fallbacks,
            confidence_scores=confidence_scores,
            element_signature=signature,
            context={
                "page_url": element.get("page_url", ""),
                "parent_selector": element.get("parent_selector", ""),
                "siblings_count": element.get("siblings_count", 0)
            }
        )
    
    def generate_test_with_healing(
        self,
        test_scenario: Dict[str, Any],
        elements: List[Dict[str, Any]]
    ) -> SelfHealingTest:
        """Generate a complete self-healing test case"""
        
        # Create resilient locators for all elements
        element_locators = {}
        for element in elements:
            if element.get("id") or element.get("test_id"):
                elem_id = element.get("id") or element.get("test_id")
                element_locators[elem_id] = self.generate_resilient_locator(element)
        
        # Generate test steps
        test_steps = []
        for step_data in test_scenario.get("steps", []):
            element_id = step_data.get("element_id")
            if element_id and element_id in element_locators:
                locator = element_locators[element_id]
            else:
                # Create a basic locator
                locator = self._create_basic_locator(step_data)
            
            test_step = TestStep(
                action=step_data.get("action", "click"),
                locator=locator,
                data=step_data.get("data"),
                assertions=step_data.get("assertions", []),
                wait_condition=step_data.get("wait_condition"),
                retry_count=step_data.get("retry_count", 3),
                timeout=step_data.get("timeout", 10000)
            )
            test_steps.append(test_step)
        
        # Create test ID
        test_id = self._generate_test_id(test_scenario["name"])
        
        return SelfHealingTest(
            test_id=test_id,
            test_name=test_scenario["name"],
            description=test_scenario.get("description", ""),
            preconditions=test_scenario.get("preconditions", []),
            steps=test_steps,
            expected_results=test_scenario.get("expected_results", []),
            test_data=test_scenario.get("test_data", {}),
            tags=test_scenario.get("tags", []),
            priority=test_scenario.get("priority", "medium"),
            healing_history=[]
        )
    
    def generate_playwright_test(self, test: SelfHealingTest) -> str:
        """Generate Playwright test code with self-healing"""
        
        # Format test data
        test_data_str = json.dumps(test.test_data, indent=8)
        
        # Format preconditions
        preconditions_str = self._format_preconditions(test.preconditions)
        
        # Format test steps
        test_steps_str = self._format_test_steps(test.steps)
        
        # Format assertions
        assertions_str = self._format_assertions(test.expected_results)
        
        # Format tags
        tags_str = json.dumps(test.tags)
        
        # Generate test code
        return self.PLAYWRIGHT_TEST_TEMPLATE.format(
            test_name=test.test_name.replace(" ", "_").lower(),
            test_description=test.description,
            test_id=test.test_id,
            priority=test.priority,
            tags=tags_str,
            test_data=test_data_str,
            preconditions=preconditions_str,
            test_steps=test_steps_str,
            assertions=assertions_str
        )
    
    def _generate_ai_description(self, element: Dict[str, Any]) -> str:
        """Generate natural language description of element for AI-based location"""
        
        descriptions = []
        
        # Type and role
        if element.get("type"):
            descriptions.append(f"A {element['type']} element")
        elif element.get("role"):
            descriptions.append(f"An element with role {element['role']}")
        
        # Text content
        if element.get("text"):
            descriptions.append(f"containing text '{element['text'][:50]}'")
        
        # Visual characteristics
        if element.get("visual_description"):
            descriptions.append(element["visual_description"])
        
        # Position
        if element.get("position_description"):
            descriptions.append(element["position_description"])
        
        # Interaction hints
        if element.get("interaction_hints"):
            hints = ", ".join(element["interaction_hints"][:3])
            descriptions.append(f"that can be {hints}")
        
        return " ".join(descriptions)
    
    def _generate_element_signature(self, element: Dict[str, Any]) -> str:
        """Generate unique signature for element tracking"""
        
        # Combine stable attributes
        signature_parts = [
            element.get("type", "unknown"),
            element.get("role", ""),
            element.get("tag_name", ""),
            str(element.get("position_index", 0)),
            element.get("parent_selector", ""),
            str(len(element.get("text", "")))
        ]
        
        signature_string = "|".join(signature_parts)
        return hashlib.md5(signature_string.encode()).hexdigest()[:16]
    
    def _generate_test_id(self, test_name: str) -> str:
        """Generate unique test ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name_hash = hashlib.md5(test_name.encode()).hexdigest()[:8]
        return f"test_{name_hash}_{timestamp}"
    
    def _create_basic_locator(self, step_data: Dict[str, Any]) -> ResilientLocator:
        """Create a basic locator when element info is not available"""
        
        selector = step_data.get("selector", "")
        text = step_data.get("text", "")
        
        locators = []
        
        if selector:
            locators.append({
                "strategy": LocatorStrategy.CSS.value,
                "value": selector
            })
        
        if text:
            locators.append({
                "strategy": LocatorStrategy.TEXT.value,
                "value": text
            })
        
        return ResilientLocator(
            primary=locators[0] if locators else {"strategy": "css", "value": "*"},
            fallbacks=locators[1:] if len(locators) > 1 else [],
            confidence_scores={},
            element_signature="",
            context={}
        )
    
    def _format_preconditions(self, preconditions: List[str]) -> str:
        """Format preconditions as code comments"""
        if not preconditions:
            return "# No specific preconditions"
        
        lines = ["# Preconditions:"]
        for condition in preconditions:
            lines.append(f"    # - {condition}")
        
        return "\n".join(lines)
    
    def _format_test_steps(self, steps: List[TestStep]) -> str:
        """Format test steps as Playwright code"""
        
        code_lines = []
        
        for i, step in enumerate(steps, 1):
            code_lines.append(f"        # Step {i}: {step.action}")
            
            # Generate locator config
            locator_config = {
                "primary": step.locator.primary,
                "fallbacks": step.locator.fallbacks,
                "ai_description": step.locator.context.get("ai_description", "")
            }
            
            locator_json = json.dumps(locator_config, indent=12).replace('\n', '\n        ')
            
            code_lines.append(f"        locator_config = {locator_json}")
            code_lines.append(f"        element = await healing_page.locate_with_healing(locator_config)")
            code_lines.append("        assert element, f'Element not found: {locator_config}'")
            
            # Add wait condition if specified
            if step.wait_condition:
                code_lines.append(f"        await element.wait_for(state='{step.wait_condition}')")
            
            # Perform action
            if step.action == "click":
                code_lines.append("        await element.click()")
            elif step.action == "type":
                data = step.data or ""
                code_lines.append(f"        await element.fill('{data}')")
            elif step.action == "select":
                value = step.data or ""
                code_lines.append(f"        await element.select_option('{value}')")
            elif step.action == "check":
                code_lines.append("        await element.check()")
            elif step.action == "uncheck":
                code_lines.append("        await element.uncheck()")
            elif step.action == "hover":
                code_lines.append("        await element.hover()")
            elif step.action == "screenshot":
                code_lines.append(f"        await element.screenshot(path='step_{i}.png')")
            
            # Add assertions for this step
            if step.assertions:
                for assertion in step.assertions:
                    assertion_code = self._format_assertion(assertion)
                    code_lines.append(f"        {assertion_code}")
            
            code_lines.append("")  # Empty line between steps
        
        return "\n".join(code_lines)
    
    def _format_assertions(self, expected_results: List[str]) -> str:
        """Format expected results as assertions"""
        
        if not expected_results:
            return "# Verify expected results"
        
        lines = ["# Final assertions"]
        for result in expected_results:
            lines.append(f"        # TODO: Assert {result}")
        
        return "\n".join(lines)
    
    def _format_assertion(self, assertion: Dict[str, Any]) -> str:
        """Format a single assertion"""
        
        assert_type = assertion.get("type", "visible")
        
        if assert_type == "visible":
            return "assert await element.is_visible()"
        elif assert_type == "text":
            expected = assertion.get("expected", "")
            return f"assert await element.text_content() == '{expected}'"
        elif assert_type == "enabled":
            return "assert await element.is_enabled()"
        elif assert_type == "checked":
            return "assert await element.is_checked()"
        else:
            return f"# TODO: Custom assertion - {assertion}"
    
    async def analyze_healing_effectiveness(
        self,
        healing_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze how well self-healing is working"""
        
        analysis = {
            "total_healings": len(healing_history),
            "healing_by_strategy": {},
            "most_fragile_locators": [],
            "recommendations": []
        }
        
        # Count healings by strategy
        for record in healing_history:
            healed_strategy = record["healed"]["strategy"]
            analysis["healing_by_strategy"][healed_strategy] = \
                analysis["healing_by_strategy"].get(healed_strategy, 0) + 1
        
        # Identify fragile locators
        original_failures = {}
        for record in healing_history:
            original = json.dumps(record["original"])
            original_failures[original] = original_failures.get(original, 0) + 1
        
        # Sort by failure count
        fragile_locators = sorted(
            original_failures.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        analysis["most_fragile_locators"] = [
            {"locator": json.loads(loc), "failures": count}
            for loc, count in fragile_locators
        ]
        
        # Generate recommendations
        if analysis["healing_by_strategy"].get("ai_description", 0) > 5:
            analysis["recommendations"].append(
                "Consider adding more stable locators (IDs, data-testid) to reduce AI-based healing"
            )
        
        if analysis["total_healings"] > 50:
            analysis["recommendations"].append(
                "High healing rate detected. Review UI stability or update base locators."
            )
        
        return analysis