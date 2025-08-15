"""
LIVE Production UI Testing System with Real Browser Automation
==============================================================
This system uses REAL browser automation to extract elements from LIVE websites.
No mocks, no fake data - everything is extracted from actual web pages.

Pipeline:
1. Real browser navigation using UltimateStealthBrowserLLMEnhanced
2. Live element extraction with LLM optimization
3. Test case generation based on actual page structure
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import LLM functionality
from llm import query_llm

# Import browser automation
from browser.main import UltimateStealthBrowserLLMEnhanced
from browser.base import StealthConfig, StealthLevel
from browser.element_structure import PageStructure, LLMOptimizedElement, ElementCategory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class LiveProductionConfig:
    """Configuration for live production testing."""
    
    # Browser Settings
    headless: bool = False  # Set to False to see browser in action
    stealth_level: StealthLevel = StealthLevel.MAXIMUM
    timeout: int = 30000  # 30 seconds
    wait_for_load: bool = True
    
    # LLM Settings
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash-lite" #"gemini-2.5-pro"
    llm_temperature: float = 0.3
    llm_max_retries: int = 3
    
    # Advanced Prompt Strategies
    enable_chain_of_thought: bool = True
    enable_tree_of_thoughts: bool = True
    enable_self_consistency: bool = True
    enable_meta_prompting: bool = True
    enable_react: bool = True  # ReAct: Reasoning + Acting
    enable_constitutional_ai: bool = True  # Constitutional AI for safety
    enable_debate: bool = True  # Multi-agent debate
    enable_reflexion: bool = True  # Self-reflection and improvement
    enable_scratchpad: bool = True  # Scratchpad reasoning
    enable_few_shot: bool = True  # Few-shot examples
    enable_opro_optimization: bool = True  # OPRO iterative optimization
    enable_dspy_refinement: bool = True  # DSPy-style self-refinement
    self_consistency_samples: int = 3
    opro_iterations: int = 2  # Number of OPRO optimization iterations
    
    # Extraction Settings
    max_elements_per_page: int = 50
    extract_timeout: int = 60
    
    # Test Generation Settings
    test_strategies: List[str] = field(default_factory=lambda: [
        "critical_path",
        "validation",
        "error_handling",
        "security",
        "metamorphic",
        "visual_regression",
        "property_based",
        "contract_testing",
        "chaos_engineering"
    ])
    scenarios_per_strategy: int = 3
    
    # Advanced Testing Features
    enable_metamorphic_testing: bool = True
    enable_visual_testing: bool = True
    enable_property_based: bool = True
    enable_context_aware_generation: bool = True
    
    # 2025 Cutting-Edge Features
    enable_gherkin_format: bool = True
    enable_self_healing: bool = True
    enable_risk_based_prioritization: bool = True
    enable_test_impact_analysis: bool = True
    enable_performance_budgets: bool = True
    enable_ai_test_optimization: bool = True
    
    # Storage Settings
    results_dir: str = "live_test_results"
    save_screenshots: bool = True
    save_intermediate: bool = True


# ============================================================================
# LIVE BROWSER EXTRACTOR
# ============================================================================

class LiveBrowserExtractor:
    """Extract elements from live websites using real browser automation."""
    
    def __init__(self, config: LiveProductionConfig):
        self.config = config
        self.browser = None
        self.extraction_count = 0
    
    async def initialize(self):
        """Initialize the browser with stealth configuration."""
        browser_config = StealthConfig(
            level=self.config.stealth_level,
            headless=self.config.headless,
            detect_frameworks=True,
            detect_captcha=True
        )
        
        self.browser = UltimateStealthBrowserLLMEnhanced(browser_config)
        await self.browser.initialize()
        logger.info("Browser initialized with stealth capabilities")
    
    async def extract_from_url(self, url: str) -> PageStructure:
        """Extract elements from a live URL."""
        if not self.browser:
            await self.initialize()
        
        try:
            logger.info(f"Navigating to {url}...")
            
            # Extract elements using LLM-optimized method
            page_structure = await self.browser.extract_elements_for_llm(url)
            
            self.extraction_count += 1
            
            # Count total elements
            total_elements = sum(
                len(elements) for elements in page_structure.elements_by_category.values()
            )
            
            logger.info(f"Extracted {total_elements} elements from {url}")
            logger.info(f"Categories found: {list(page_structure.elements_by_category.keys())}")
            
            # Take screenshot if enabled
            if self.config.save_screenshots:
                screenshot_path = await self._take_screenshot(url)
                logger.info(f"Screenshot saved: {screenshot_path}")
            
            return page_structure
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}")
            raise
    
    async def _take_screenshot(self, url: str) -> str:
        """Take a screenshot of the current page."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_name = url.split('/')[2].replace('.', '_')
        
        results_dir = Path(self.config.results_dir)
        results_dir.mkdir(exist_ok=True)
        
        screenshot_path = results_dir / f"{timestamp}_{site_name}_screenshot.png"
        
        if self.browser and self.browser.page:
            await self.browser.page.screenshot(path=str(screenshot_path))
        
        return str(screenshot_path)
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.cleanup()
            logger.info("Browser cleanup completed")


# ============================================================================
# LLM TEST GENERATOR
# ============================================================================

class LiveTestGenerator:
    """Generate test cases from live extracted elements using LLM with advanced prompt strategies."""
    
    def __init__(self, config: LiveProductionConfig):
        self.config = config
        self.llm_calls = 0
        self.risk_scores = {}  # Store risk scores for prioritization
        self.test_impact_map = {}  # Map tests to impacted areas
    
    def _apply_chain_of_thought(self, prompt: str) -> str:
        """Apply Chain of Thought reasoning to enhance prompt."""
        if not self.config.enable_chain_of_thought:
            return prompt
            
        cot_addition = """

Think step-by-step:
1. First, identify the most critical functionality based on the actual elements
2. Then, determine what could go wrong with each interaction
3. Consider edge cases specific to the element types found
4. Think about real-world user mistakes and malicious inputs
5. Prioritize test cases by risk and user impact

Show your reasoning before generating the test cases."""
        return prompt + cot_addition
    
    def _apply_tree_of_thoughts(self, prompt: str, strategy: str) -> str:
        """Apply Tree of Thoughts for comprehensive exploration."""
        if not self.config.enable_tree_of_thoughts:
            return prompt
            
        tot_addition = f"""

Explore multiple testing perspectives for {strategy}:

Branch 1: User Experience Testing
- What would frustrate real users?
- What mistakes would beginners make?
- What shortcuts would power users attempt?
- How would users with disabilities interact?

Branch 2: Technical Testing
- What are the boundary conditions for each field?
- What data combinations could break the system?
- What race conditions could occur?
- What caching or state issues might arise?

Branch 3: Security & Compliance Testing
- What injection attacks are possible?
- How could authentication be bypassed?
- What sensitive data could be exposed?
- What compliance requirements must be met?

Synthesize insights from ALL branches into comprehensive test cases."""
        return prompt + tot_addition
    
    def _apply_meta_prompting(self, prompt: str) -> str:
        """Apply meta-prompting for self-improvement."""
        if not self.config.enable_meta_prompting:
            return prompt
            
        meta_addition = """

Before generating test cases, consider:
- What test cases would a senior QA engineer with 10+ years experience create?
- What critical scenarios are often missed in automated test generation?
- How can these tests provide maximum coverage with minimum redundancy?
- What would make these tests maintainable and reusable?

Ensure your test cases reflect this expertise level."""
        return prompt + meta_addition
    
    def _apply_react(self, prompt: str, page_structure: PageStructure) -> str:
        """Apply ReAct (Reasoning + Acting) strategy."""
        if not self.config.enable_react:
            return prompt
            
        # Get all elements from categories
        all_elements = []
        for elements in page_structure.elements_by_category.values():
            all_elements.extend(elements)
        
        react_enhancement = f"""

Use ReAct (Reasoning + Acting) approach:

Thought 1: Analyze the page structure
- Page has {len(all_elements)} elements
- Critical elements: {len([e for e in all_elements if hasattr(e, 'test_priority') and e.test_priority and e.test_priority.value == 'critical'])}
- Forms detected: {len(page_structure.elements_by_category.get(ElementCategory.FORM_INPUT, []))}

Action 1: Identify test scenarios based on element types
Observation 1: Generate tests for each critical interaction path

Thought 2: Consider edge cases and error conditions
Action 2: Create negative test scenarios
Observation 2: Ensure comprehensive error handling coverage

Thought 3: Evaluate security and performance implications
Action 3: Add security and performance test cases
Observation 3: Complete test suite with all dimensions covered

Reasoning: Each action should be justified by clear reasoning.
Actions: Generate concrete, executable test steps.
"""
        return prompt + react_enhancement
    
    def _apply_constitutional_ai(self, prompt: str) -> str:
        """Apply Constitutional AI principles for safe and ethical testing."""
        if not self.config.enable_constitutional_ai:
            return prompt
            
        constitutional_enhancement = """

Apply Constitutional AI principles:

Constitutional Rules:
1. SAFETY: Never generate tests that could harm users or systems
2. PRIVACY: Do not include real personal data in test cases
3. ETHICS: Avoid tests that exploit vulnerabilities maliciously
4. COMPLIANCE: Ensure tests follow GDPR, CCPA, and accessibility standards
5. TRANSPARENCY: Make test intentions clear and documented

Self-Critique:
- Are these tests safe to run in production?
- Do they respect user privacy?
- Are they ethically sound?
- Do they comply with regulations?

Revise any test cases that violate these principles.
"""
        return prompt + constitutional_enhancement
    
    def _apply_debate(self, prompt: str, strategy: str) -> str:
        """Apply multi-agent debate for test case validation."""
        if not self.config.enable_debate:
            return prompt
            
        debate_enhancement = f"""

Multi-Agent Debate for {strategy} testing:

Agent 1 (Advocate): Generate comprehensive test cases
- Argument: Maximum coverage is essential
- Proposal: Test every possible scenario

Agent 2 (Critic): Challenge test efficiency
- Counter: Too many tests slow development
- Proposal: Focus on high-risk areas only

Agent 3 (Synthesizer): Find optimal balance
- Resolution: Prioritize by risk and business value
- Final: Generate balanced test suite

Debate Outcome: Create tests that balance coverage with efficiency.
"""
        return prompt + debate_enhancement
    
    def _apply_reflexion(self, prompt: str) -> str:
        """Apply Reflexion for iterative improvement."""
        if not self.config.enable_reflexion:
            return prompt
            
        reflexion_enhancement = """

Apply Reflexion (self-improvement through reflection):

Initial Attempt: Generate test cases
Reflection Questions:
- What did I miss in my initial test design?
- Which edge cases were overlooked?
- How can I improve test maintainability?
- What would break these tests?

Refined Approach:
- Add missing edge cases
- Improve selector strategies
- Enhance assertions
- Add better error messages

Final Iteration: Generate improved test cases based on reflection.
"""
        return prompt + reflexion_enhancement
    
    def _apply_scratchpad(self, prompt: str, page_structure: PageStructure) -> str:
        """Apply Scratchpad reasoning for complex test generation."""
        if not self.config.enable_scratchpad:
            return prompt
            
        # Get all elements from categories
        all_elements = []
        for elements in page_structure.elements_by_category.values():
            all_elements.extend(elements)
            
        scratchpad_enhancement = f"""

=== SCRATCHPAD REASONING ===

Working Memory:
- Total elements: {len(all_elements)}
- Page type: {page_structure.page_type}
- Critical paths: {len(page_structure.critical_paths) if page_structure.critical_paths else 0}

Calculations:
- Test complexity score: {self._calculate_complexity_score(page_structure)}
- Risk assessment: {self._assess_page_risk(page_structure)}
- Coverage target: 80% of critical paths, 60% of all paths

Test Design Notes:
1. Start with happy path
2. Add validation for each required field
3. Include boundary value tests
4. Add security tests for input fields
5. Include accessibility checks

=== END SCRATCHPAD ===

Based on scratchpad analysis, generate comprehensive tests.
"""
        return prompt + scratchpad_enhancement
    
    def _apply_few_shot(self, prompt: str, strategy: str) -> str:
        """Apply Few-Shot learning with examples."""
        if not self.config.enable_few_shot:
            return prompt
            
        few_shot_examples = {
            "critical_path": """

Example test case for reference:
```json
{
  "title": "Successful user login flow",
  "description": "Given user is on login page, When entering valid credentials, Then user is redirected to dashboard",
  "priority": "critical",
  "steps": [
    {"action": "navigate", "url": "/login"},
    {"action": "type", "selector": "#username", "value": "testuser"},
    {"action": "type", "selector": "#password", "value": "password123"},
    {"action": "click", "selector": "#submit"},
    {"action": "wait", "condition": "url_contains('/dashboard')"},
    {"action": "assert", "selector": ".welcome-message", "exists": true}
  ]
}
```

Generate similar high-quality test cases.
""",
            "security": """

Example security test case:
```json
{
  "title": "SQL Injection prevention test",
  "description": "Verify system prevents SQL injection attacks",
  "priority": "critical",
  "steps": [
    {"action": "type", "selector": "#search", "value": "'; DROP TABLE users; --"},
    {"action": "click", "selector": "#search-btn"},
    {"action": "assert", "response_code": 400},
    {"action": "assert", "error_message": "Invalid input"}
  ]
}
```
"""
        }
        
        example = few_shot_examples.get(strategy, "")
        if example:
            return prompt + example
        return prompt
    
    def _generate_gherkin_format(self, test_case: Dict) -> str:
        """Convert test case to Gherkin format for BDD."""
        if not self.config.enable_gherkin_format:
            return ""
        
        gherkin = f"""Feature: {test_case.get('title', 'Test Feature')}
  {test_case.get('description', 'Test description')}

  @{test_case.get('priority', 'medium')}
  @{test_case.get('strategy', 'general')}
  Scenario: {test_case.get('title', 'Test Scenario')}"""
        
        # Add prerequisites as Background if present
        if test_case.get('prerequisites'):
            gherkin += "\n    Background:"
            for prereq in test_case['prerequisites']:
                gherkin += f"\n      * {prereq}"
        
        # Convert steps to Given/When/Then format
        steps = test_case.get('steps', [])
        for i, step in enumerate(steps):
            action = step.get('action', '')
            data = step.get('data', '')
            expected = step.get('expected', '')
            
            # Determine step type based on position and action
            if i == 0 or 'navigate' in action.lower() or 'open' in action.lower():
                keyword = "Given"
            elif 'click' in action.lower() or 'type' in action.lower() or 'select' in action.lower():
                keyword = "When"
            else:
                keyword = "Then"
            
            # Format the step
            if data:
                gherkin += f'\n    {keyword} I {action} "{data}" in "{step.get("selector", "element")}"'
            else:
                gherkin += f'\n    {keyword} {action}'
            
            if expected and keyword != "Then":
                gherkin += f'\n    Then {expected}'
        
        # Add assertions as Then statements
        for assertion in test_case.get('assertions', []):
            gherkin += f"\n    Then {assertion}"
        
        # Add examples table for data-driven tests
        if test_case.get('test_data'):
            gherkin += "\n\n    Examples:"
            headers = list(test_case['test_data'].keys())
            gherkin += f"\n      | {' | '.join(headers)} |"
            values = [str(v) for v in test_case['test_data'].values()]
            gherkin += f"\n      | {' | '.join(values)} |"
        
        return gherkin
    
    def _add_self_healing_capabilities(self, test_case: Dict) -> Dict:
        """Add self-healing metadata to test cases."""
        if not self.config.enable_self_healing:
            return test_case
        
        # Add alternative selectors for self-healing
        for step in test_case.get('steps', []):
            selector = step.get('selector', '')
            if selector:
                # Generate alternative selectors
                step['alternative_selectors'] = {
                    'primary': selector,
                    'fallback_text': f"text={step.get('data', '')}",
                    'fallback_partial': selector.replace('#', '[id*=').replace(']', ']') if '#' in selector else selector,
                    'fallback_contains': f"*[class*='{selector.split('.')[-1]}']" if '.' in selector else selector,
                    'ai_hint': f"Element that {step.get('action', 'interacts')} with {step.get('expected', 'system')}"
                }
                
                # Add healing strategy
                step['healing_strategy'] = {
                    'retry_count': 3,
                    'wait_before_retry': 1000,
                    'use_ai_recognition': True,
                    'visual_matching': True,
                    'context_aware': True
                }
        
        # Add test-level healing metadata
        test_case['self_healing'] = {
            'enabled': True,
            'max_healing_attempts': 5,
            'healing_confidence_threshold': 0.8,
            'report_healed_elements': True,
            'update_selectors_after_healing': True
        }
        
        return test_case
    
    def _calculate_risk_score(self, test_case: Dict, page_structure: PageStructure) -> float:
        """Calculate risk score for test prioritization."""
        if not self.config.enable_risk_based_prioritization:
            return 0.5
        
        risk_score = 0.0
        
        # Priority-based scoring
        priority_scores = {'critical': 1.0, 'high': 0.75, 'medium': 0.5, 'low': 0.25}
        risk_score += priority_scores.get(test_case.get('priority', 'medium'), 0.5)
        
        # Page type risk scoring
        high_risk_pages = ['login', 'checkout', 'payment', 'authentication']
        if page_structure.page_type in high_risk_pages:
            risk_score += 0.3
        
        # Security test bonus
        if test_case.get('strategy') == 'security':
            risk_score += 0.2
        
        # Critical path bonus
        if test_case.get('strategy') == 'critical_path':
            risk_score += 0.15
        
        # Complexity scoring based on steps
        step_count = len(test_case.get('steps', []))
        if step_count > 10:
            risk_score += 0.1
        
        # Normalize to 0-1 range
        return min(risk_score / 2.0, 1.0)
    
    def _calculate_complexity_score(self, page_structure: PageStructure) -> float:
        """Calculate complexity score for test generation."""
        score = 0.0
        
        # Get all elements
        all_elements = []
        for elements in page_structure.elements_by_category.values():
            all_elements.extend(elements)
        
        # Factor in number of elements
        element_count = len(all_elements)
        score += min(element_count / 100, 0.3)  # Max 0.3 for element count
        
        # Factor in form complexity
        form_elements = len(page_structure.elements_by_category.get(ElementCategory.FORM_INPUT, []))
        score += min(form_elements / 20, 0.2)  # Max 0.2 for forms
        
        # Factor in critical paths
        if page_structure.critical_paths:
            score += min(len(page_structure.critical_paths) / 10, 0.2)  # Max 0.2 for paths
        
        # Factor in validation rules
        if page_structure.page_validations:
            score += min(len(page_structure.page_validations) / 15, 0.15)  # Max 0.15
        
        # Factor in security elements
        if page_structure.security_considerations:
            score += 0.15  # Flat 0.15 for security
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _assess_page_risk(self, page_structure: PageStructure) -> str:
        """Assess risk level of the page for testing."""
        risk_score = 0
        
        # Check for authentication elements
        if page_structure.page_type in ['login', 'registration', 'authentication']:
            risk_score += 3
        
        # Check for payment/financial elements
        if any(keyword in str(page_structure.business_purpose).lower() 
               for keyword in ['payment', 'checkout', 'billing', 'credit']):
            risk_score += 3
        
        # Check for data input forms
        form_count = len(page_structure.elements_by_category.get(ElementCategory.FORM_INPUT, []))
        if form_count > 5:
            risk_score += 2
        elif form_count > 0:
            risk_score += 1
        
        # Check for security considerations
        if page_structure.security_considerations:
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 6:
            return "CRITICAL"
        elif risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _perform_test_impact_analysis(self, test_case: Dict, element_context: Dict) -> Dict:
        """Analyze test impact based on element changes and dependencies."""
        if not self.config.enable_test_impact_analysis:
            return {}
        
        impact_analysis = {
            'affected_components': [],
            'dependency_chain': [],
            'estimated_execution_time': 0,
            'flakiness_risk': 'low',
            'maintenance_complexity': 'low'
        }
        
        # Identify affected components
        for step in test_case.get('steps', []):
            selector = step.get('selector', '')
            if selector:
                # Map selector to component
                if 'login' in selector.lower() or 'auth' in selector.lower():
                    impact_analysis['affected_components'].append('authentication')
                if 'nav' in selector.lower() or 'menu' in selector.lower():
                    impact_analysis['affected_components'].append('navigation')
                if 'form' in selector.lower() or 'input' in selector.lower():
                    impact_analysis['affected_components'].append('forms')
        
        # Estimate execution time
        step_count = len(test_case.get('steps', []))
        impact_analysis['estimated_execution_time'] = step_count * 2  # 2 seconds per step average
        
        # Assess flakiness risk
        if element_context.get('performance_risks'):
            impact_analysis['flakiness_risk'] = 'high'
        elif step_count > 15:
            impact_analysis['flakiness_risk'] = 'medium'
        
        # Assess maintenance complexity
        if test_case.get('strategy') in ['metamorphic', 'property_based']:
            impact_analysis['maintenance_complexity'] = 'high'
        elif step_count > 10:
            impact_analysis['maintenance_complexity'] = 'medium'
        
        return impact_analysis
    
    async def generate_tests(
        self, 
        page_structure: PageStructure,
        strategy: str
    ) -> List[Dict[str, Any]]:
        """Generate test cases for a specific strategy based on live data."""
        
        # Prepare element summary from live extraction
        element_summary = self._create_element_summary(page_structure)
        
        # Analyze element context for smarter test generation
        element_context = self._analyze_element_context(page_structure) if self.config.enable_context_aware_generation else {}
        
        # Enhanced strategy prompts with comprehensive testing patterns
        strategy_prompts = {
            "contract_testing": f"""Generate CONTRACT TESTING test cases for API and component contracts. Include:

1. API CONTRACT VALIDATION:
   - Request/response schema validation
   - Required fields presence
   - Data type consistency
   - Response time SLAs
   - Error response formats

2. COMPONENT CONTRACTS:
   - Interface agreements between UI components
   - Event emission contracts
   - State management contracts
   - Props/attributes contracts

3. BACKWARD COMPATIBILITY:
   - Version compatibility checks
   - Deprecation handling
   - Migration path validation

4. CONSUMER-DRIVEN CONTRACTS:
   - Consumer expectations validation
   - Provider capability verification

For {page_structure.page_type} page, focus on:
{json.dumps(element_context.get('api_contracts', []), indent=2)}""",

            "chaos_engineering": f"""Generate CHAOS ENGINEERING test cases to test system resilience. Include:

1. NETWORK CHAOS:
   - Simulated network latency (add 3-5 second delays)
   - Packet loss simulation (drop 10-30% requests)
   - Bandwidth throttling
   - Connection timeouts
   - DNS failures

2. BROWSER CHAOS:
   - Memory pressure simulation
   - CPU throttling (6x slowdown)
   - Storage quota exceeded
   - JavaScript execution errors
   - Third-party script failures

3. USER BEHAVIOR CHAOS:
   - Rapid clicking/double clicking
   - Browser back/forward during operations
   - Tab switching mid-operation
   - Copy-paste of malformed data
   - Rage clicking when slow

4. DATA CHAOS:
   - Corrupt localStorage/sessionStorage
   - Invalid cookies
   - Stale cache data
   - Timezone changes mid-session

System resilience points for {page_structure.page_type}:
{json.dumps(element_context.get('resilience_points', []), indent=2)}""",

            "metamorphic": f"""Generate METAMORPHIC test cases using invariant properties. Include:

1. INVARIANT RELATIONS (output unchanged):
   - Synonym substitution in text fields
   - Reordering optional fields
   - Adding/removing whitespace
   - Case transformation where applicable
   - Session persistence across refreshes

2. INCREASING RELATIONS (output increases):
   - Adding more items to cart increases total
   - More search keywords return more results
   - Longer input increases processing time

3. DECREASING RELATIONS (output decreases):
   - More restrictive filters reduce results
   - Earlier date ranges show fewer recent items

4. TRANSFORMATION RELATIONS:
   - Input permutations yield consistent results
   - Inverse operations cancel each other

Context-specific relations for {page_structure.page_type}:
{json.dumps(element_context.get('metamorphic_hints', []), indent=2)}""",
            
            "visual_regression": f"""Generate VISUAL REGRESSION test cases. Include:

1. LAYOUT CONSISTENCY:
   - Element alignment verification
   - Responsive breakpoints (320px, 768px, 1024px, 1920px)
   - Text overflow handling
   - Image loading and fallbacks
   - Dynamic content rendering

2. INTERACTION STATES:
   - Hover effects on interactive elements
   - Focus states for accessibility
   - Active/pressed states
   - Disabled state appearance
   - Loading/skeleton states

3. CROSS-BROWSER RENDERING:
   - Chrome vs Firefox vs Safari differences
   - Font rendering consistency
   - CSS grid/flexbox behavior
   - Animation smoothness

4. VISUAL ACCESSIBILITY:
   - Color contrast ratios (WCAG AA/AAA)
   - Focus indicators visibility
   - Text readability at zoom levels
   - High contrast mode compatibility

Visual elements detected: {len([e for cat, elems in page_structure.elements_by_category.items() for e in elems if cat.value in ['action', 'navigation']])}""",
            
            "property_based": f"""Generate PROPERTY-BASED test cases. Test invariants that should ALWAYS hold:

1. MATHEMATICAL PROPERTIES:
   - Commutativity: order doesn't matter for certain operations
   - Associativity: grouping doesn't affect results
   - Idempotence: repeated operations yield same result
   - Inverse: undo operations restore original state

2. BUSINESS RULE PROPERTIES:
   - Price calculations always non-negative
   - Dates follow chronological order
   - Unique IDs remain unique
   - Totals equal sum of parts

3. CONSISTENCY PROPERTIES:
   - Database state matches UI state
   - Client-side validation matches server-side
   - URL state matches application state
   - Cache coherence maintained

4. GENERATIVE PROPERTIES for {page_structure.page_type}:
   - Generate random valid inputs and verify invariants
   - Shrink failing cases to minimal reproducible example
   - Test with extreme values within valid ranges

Detected constraints: {json.dumps(page_structure.page_validations[:3], indent=2)}""",
            
            "critical_path": """Generate COMPREHENSIVE test cases for critical user journeys. Include:

1. HAPPY PATH scenarios:
   - Complete end-to-end workflows
   - All mandatory fields with valid data
   - Expected navigation flows
   - Success confirmations

2. ALTERNATE PATHS:
   - Optional field combinations
   - Different navigation routes to same goal
   - Browser back/forward button usage
   - Session timeout and recovery

3. INTEGRATION POINTS:
   - API calls triggered by user actions
   - Third-party service integrations
   - Cross-browser compatibility
   - Mobile responsiveness

4. PERFORMANCE CONSIDERATIONS:
   - Response time expectations
   - Concurrent user scenarios
   - Large data handling""",
            
            "validation": """Generate THOROUGH validation test cases. Include:

1. FIELD-LEVEL VALIDATION:
   - Required field enforcement
   - Min/max length boundaries
   - Format validation (email, phone, date)
   - Special character handling
   - Unicode and emoji support
   - Copy-paste behavior
   - Auto-fill compatibility

2. BOUNDARY TESTING:
   - Minimum valid values (n-1, n, n+1)
   - Maximum valid values (n-1, n, n+1)
   - Empty strings vs null values
   - Leading/trailing spaces
   - Case sensitivity

3. CROSS-FIELD VALIDATION:
   - Dependent field validation
   - Date range validation (start < end)
   - Conditional required fields
   - Business rule validation

4. ERROR MESSAGE TESTING:
   - Clear, actionable error messages
   - Error message localization
   - Multiple error display
   - Error recovery flows""",
            
            "error_handling": """Generate ROBUST error handling test cases. Include:

1. USER ERROR SCENARIOS:
   - Accidental form resubmission
   - Double-clicking submit buttons
   - Browser refresh during submission
   - Network interruption handling
   - Session expiration during input

2. SYSTEM ERROR SCENARIOS:
   - Server timeout responses
   - 500/503 error handling
   - Database connection failures
   - Third-party service failures
   - Rate limiting responses

3. EDGE CASES:
   - Concurrent modifications
   - Race conditions
   - Memory/storage limits
   - Recursive operations
   - Infinite loops prevention

4. RECOVERY TESTING:
   - Data persistence after errors
   - Graceful degradation
   - Retry mechanisms
   - Fallback options
   - Error logging verification""",
            
            "security": """Generate COMPREHENSIVE security test cases. Include:

1. INJECTION ATTACKS:
   - SQL injection ('; DROP TABLE; --, OR 1=1)
   - XSS attacks (<script>alert('XSS')</script>)
   - Command injection (; ls -la)
   - LDAP injection
   - XML/XXE injection
   - Header injection

2. AUTHENTICATION ATTACKS:
   - Brute force prevention
   - Password complexity bypass
   - Session hijacking
   - Token manipulation
   - Cookie tampering
   - CSRF token validation

3. AUTHORIZATION TESTING:
   - Privilege escalation
   - Direct object reference
   - Path traversal (../../etc/passwd)
   - Forced browsing
   - API endpoint access control

4. DATA SECURITY:
   - Sensitive data in URLs
   - Password visibility toggle security
   - Autocomplete on sensitive fields
   - Data leakage in error messages
   - Encryption verification
   - PII handling compliance"""
        }
        
        base_prompt = f"""{strategy_prompts.get(strategy, strategy_prompts['critical_path'])}

PAGE INFORMATION:
URL: {page_structure.url}
Type: {page_structure.page_type}
Purpose: {page_structure.business_purpose}

ACTUAL ELEMENTS EXTRACTED:
{element_summary}

CRITICAL PATHS IDENTIFIED:
{json.dumps(page_structure.critical_paths[:3], indent=2) if page_structure.critical_paths else "None identified"}

USER JOURNEYS:
{json.dumps(page_structure.user_journeys[:3], indent=2) if page_structure.user_journeys else "None identified"}

VALIDATIONS REQUIRED:
{json.dumps(page_structure.page_validations[:5], indent=2) if page_structure.page_validations else "None identified"}

Generate exactly {self.config.scenarios_per_strategy} DETAILED test cases. Each test case must include:
- Specific test data values (not placeholders)
- Exact selectors from the extracted elements
- Clear pass/fail criteria
- Prerequisites and cleanup steps if needed

Return as JSON:
{{
  "test_cases": [
    {{
      "title": "Specific, descriptive test case title",
      "description": "Detailed description of what this tests and why it's important",
      "priority": "critical|high|medium|low",
      "prerequisites": ["Any setup needed before test"],
      "steps": [
        {{
          "action": "Exact action to perform",
          "selector": "Actual selector from page",
          "data": "Specific test data",
          "expected": "Detailed expected result"
        }}
      ],
      "assertions": ["Specific measurable assertions"],
      "test_data": {{"field": "exact test value"}},
      "cleanup": ["Any cleanup steps needed after test"]
    }}
  ]
}}"""

        # Apply ALL advanced prompt strategies
        enhanced_prompt = base_prompt
        enhanced_prompt = self._apply_chain_of_thought(enhanced_prompt)
        enhanced_prompt = self._apply_tree_of_thoughts(enhanced_prompt, strategy)
        enhanced_prompt = self._apply_meta_prompting(enhanced_prompt)
        
        # Apply new strategies
        if self.config.enable_react:
            enhanced_prompt = self._apply_react(enhanced_prompt, page_structure)
        if self.config.enable_constitutional_ai:
            enhanced_prompt = self._apply_constitutional_ai(enhanced_prompt)
        if self.config.enable_debate:
            enhanced_prompt = self._apply_debate(enhanced_prompt, strategy)
        if self.config.enable_reflexion:
            enhanced_prompt = self._apply_reflexion(enhanced_prompt)
        if self.config.enable_scratchpad:
            enhanced_prompt = self._apply_scratchpad(enhanced_prompt, page_structure)
        if self.config.enable_few_shot:
            enhanced_prompt = self._apply_few_shot(enhanced_prompt, strategy)

        try:
            # Use self-consistency if enabled
            if self.config.enable_self_consistency and strategy in ["critical_path", "security"]:
                responses = []
                for i in range(self.config.self_consistency_samples):
                    response = await self._call_llm(enhanced_prompt, temperature=0.3 + (i * 0.1))
                    if response and 'test_cases' in response:
                        responses.append(response['test_cases'])
                    self.llm_calls += 1
                
                # Merge and deduplicate responses
                if responses:
                    return self._merge_test_cases(responses)
            else:
                response = await self._call_llm(enhanced_prompt)
                self.llm_calls += 1
                
                if response and 'test_cases' in response:
                    test_cases = response['test_cases']
                    
                    # Apply 2025 enhancements to each test case
                    enhanced_cases = []
                    for test_case in test_cases:
                        # Add self-healing capabilities
                        test_case = self._add_self_healing_capabilities(test_case)
                        
                        # Calculate risk score for prioritization
                        risk_score = self._calculate_risk_score(test_case, page_structure)
                        test_case['risk_score'] = risk_score
                        self.risk_scores[test_case.get('id', test_case.get('title', ''))] = risk_score
                        
                        # Perform test impact analysis
                        impact = self._perform_test_impact_analysis(test_case, element_context)
                        test_case['impact_analysis'] = impact
                        self.test_impact_map[test_case.get('id', test_case.get('title', ''))] = impact
                        
                        # Generate Gherkin format
                        test_case['gherkin'] = self._generate_gherkin_format(test_case)
                        
                        # Add performance budgets if enabled
                        if self.config.enable_performance_budgets:
                            test_case['performance_budgets'] = {
                                'max_execution_time': impact.get('estimated_execution_time', 10) * 1.5,
                                'max_memory_usage': '100MB',
                                'max_cpu_usage': '50%',
                                'max_network_latency': '200ms'
                            }
                        
                        enhanced_cases.append(test_case)
                    
                    # Sort by risk score if prioritization is enabled
                    if self.config.enable_risk_based_prioritization:
                        enhanced_cases.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
                    
                    return enhanced_cases
            
            logger.warning(f"No test cases generated for {strategy}")
            return []
                
        except Exception as e:
            logger.error(f"Error generating tests: {e}")
            return []
    
    def _merge_test_cases(self, responses: List[List[Dict]]) -> List[Dict]:
        """Merge multiple test case responses, prioritizing diversity and quality."""
        all_tests = []
        seen_titles = set()
        
        for test_list in responses:
            for test in test_list:
                # Deduplicate by title
                if test.get('title') not in seen_titles:
                    all_tests.append(test)
                    seen_titles.add(test.get('title'))
        
        # Sort by priority and return top cases
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_tests.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
        
        return all_tests[:self.config.scenarios_per_strategy]
    
    def _analyze_element_context(self, page_structure: PageStructure) -> Dict[str, Any]:
        """Deeply analyze element context for intelligent test generation."""
        context = {
            "technology_stack": [],
            "framework_patterns": [],
            "metamorphic_hints": [],
            "visual_characteristics": {},
            "security_vectors": [],
            "accessibility_issues": [],
            "performance_risks": []
        }
        
        # Analyze technology stack from element patterns
        for category, elements in page_structure.elements_by_category.items():
            for elem in elements[:5]:  # Sample first 5 of each category
                # Detect React/Vue/Angular patterns from selectors
                if hasattr(elem, 'selectors') and elem.selectors:
                    for selector_type, selector_value in elem.selectors.items():
                        if selector_value:
                            if 'react' in selector_value.lower():
                                context["technology_stack"].append("React")
                            if 'ng-' in selector_value or 'data-ng-' in selector_value:
                                context["technology_stack"].append("Angular")
                            if 'v-' in selector_value and 'nav' not in selector_value:
                                context["technology_stack"].append("Vue")
                
                # Detect framework-specific patterns
                if hasattr(elem, 'selectors') and elem.selectors:
                    css_selector = elem.selectors.get('css', '') if isinstance(elem.selectors, dict) else ''
                    if css_selector:
                        if 'mui-' in css_selector or 'MuiButton' in css_selector:
                            context["framework_patterns"].append("Material-UI")
                        if 'ant-' in css_selector:
                            context["framework_patterns"].append("Ant Design")
                        if 'btn-primary' in css_selector or 'btn-secondary' in css_selector:
                            context["framework_patterns"].append("Bootstrap")
                
                # Generate metamorphic hints based on element type
                if elem.interaction and elem.interaction.primary_interaction:
                    interaction_type = elem.interaction.primary_interaction.value
                    
                    if interaction_type == "type_text":
                        context["metamorphic_hints"].append({
                            "element": elem.element_id,
                            "relation": "Case insensitive search should return same results",
                            "property": "invariant"
                        })
                        context["metamorphic_hints"].append({
                            "element": elem.element_id,
                            "relation": "Trimmed input should match untrimmed for non-password fields",
                            "property": "equivalence"
                        })
                    
                    elif interaction_type == "click":
                        context["metamorphic_hints"].append({
                            "element": elem.element_id,
                            "relation": "Double-click prevention - multiple rapid clicks should equal single click",
                            "property": "idempotence"
                        })
                
                # Identify security vectors from element characteristics
                if hasattr(elem, 'validation') and elem.validation:
                    # Check validation rules for security implications
                    if elem.validation.rules:
                        has_sanitization = any(
                            rule.value in ['html_escape', 'xss_prevention', 'sql_escape'] 
                            for rule in elem.validation.rules
                        )
                        if not has_sanitization and elem.interaction:
                            context["security_vectors"].append({
                                "element": elem.element_id,
                                "vector": "Potential injection vulnerability - no explicit sanitization rules",
                                "severity": "medium"
                            })
                
                # Check accessibility
                if hasattr(elem, 'accessibility') and elem.accessibility:
                    if hasattr(elem.accessibility, 'aria_label'):
                        if not elem.accessibility.aria_label and elem.interaction:
                            context["accessibility_issues"].append({
                                "element": elem.element_id,
                                "issue": "Interactive element missing ARIA label",
                                "wcag": "4.1.2"
                            })
                    
                    if hasattr(elem.accessibility, 'contrast_ratio'):
                        if elem.accessibility.contrast_ratio and elem.accessibility.contrast_ratio < 4.5:
                            context["accessibility_issues"].append({
                                "element": elem.element_id,
                                "issue": f"Low contrast ratio: {elem.accessibility.contrast_ratio}",
                                "wcag": "1.4.3"
                            })
        
        # Deduplicate lists
        context["technology_stack"] = list(set(context["technology_stack"]))
        context["framework_patterns"] = list(set(context["framework_patterns"]))
        
        # Add page-specific metamorphic relations
        if page_structure.page_type == "login":
            context["metamorphic_hints"].extend([
                {"relation": "Username field should be case-insensitive for email addresses", "property": "invariant"},
                {"relation": "Login with spaces around username should be trimmed", "property": "normalization"},
                {"relation": "Login attempt order should not affect lockout counter", "property": "commutativity"}
            ])
        elif page_structure.page_type == "search":
            context["metamorphic_hints"].extend([
                {"relation": "Search with synonyms should return overlapping results", "property": "similarity"},
                {"relation": "Paginated results concatenated should equal unpaginated", "property": "completeness"},
                {"relation": "Filters should be commutative - order doesn't matter", "property": "commutativity"}
            ])
        elif page_structure.page_type == "checkout":
            context["metamorphic_hints"].extend([
                {"relation": "Total = sum of items + tax + shipping", "property": "mathematical"},
                {"relation": "Removing and re-adding items should yield same total", "property": "idempotence"},
                {"relation": "Currency conversion should be reversible within tolerance", "property": "inverse"}
            ])
        
        # Visual characteristics based on element distribution
        action_elements = len(page_structure.elements_by_category.get(ElementCategory.ACTION, []))
        form_elements = len(page_structure.elements_by_category.get(ElementCategory.FORM_INPUT, []))
        
        context["visual_characteristics"] = {
            "is_form_heavy": form_elements > 5,
            "is_action_heavy": action_elements > 10,
            "requires_responsive_testing": True,  # Always test responsive
            "critical_viewports": [320, 768, 1024, 1920],
            "estimated_complexity": "high" if (action_elements + form_elements) > 20 else "medium"
        }
        
        # Performance risks based on element count and type
        total_elements = sum(len(elems) for elems in page_structure.elements_by_category.values())
        if total_elements > 100:
            context["performance_risks"].append("High DOM element count may impact rendering performance")
        
        if len(page_structure.elements_by_category.get(ElementCategory.DATA_DISPLAY, [])) > 50:
            context["performance_risks"].append("Large data tables may need virtualization")
        
        return context
    
    def _create_element_summary(self, page_structure: PageStructure) -> str:
        """Create a concise summary of live extracted elements."""
        summary = []
        
        for category, elements in page_structure.elements_by_category.items():
            if elements:
                summary.append(f"\n{category.value.upper()} ({len(elements)} elements):")
                
                for elem in elements[:3]:  # Show first 3 of each category
                    elem_info = {
                        'id': elem.element_id,
                        'tag': elem.tag_name,
                        'type': elem.element_category.value,
                        'selectors': elem.selectors,
                        'purpose': elem.semantic.primary_purpose if elem.semantic else None,
                        'priority': elem.test_priority.value if elem.test_priority else None
                    }
                    
                    # Add interaction info
                    if elem.interaction:
                        elem_info['interaction'] = elem.interaction.primary_interaction.value
                    
                    # Add validation info
                    if elem.validation and elem.validation.rules:
                        elem_info['validation_rules'] = [r.value for r in elem.validation.rules]
                    
                    summary.append(f"  - {json.dumps(elem_info, indent=4)}")
        
        return '\n'.join(summary)
    
    async def _call_llm(self, prompt: str, temperature: float = None) -> Dict:
        """Call LLM with retry logic."""
        if temperature is None:
            temperature = self.config.llm_temperature
            
        for attempt in range(self.config.llm_max_retries):
            try:
                # Enhanced system prompt for 2025 standards with Gemini-2.5-pro
                system_prompt = """You are a principal QA architect with 15+ years of experience at FAANG companies, specializing in AI-powered testing for 2025.
                
Your cutting-edge expertise includes:
- BDD/Gherkin: Writing collaborative, living documentation in Cucumber format
- Self-healing tests: Creating resilient tests that adapt to UI changes automatically
- Risk-based prioritization: Using AI to identify high-impact test scenarios
- Contract testing: Consumer-driven contracts, API schemas, backward compatibility
- Chaos engineering: Netflix-style resilience testing, failure injection
- Test oracle generation: AI-powered prediction of expected behaviors
- Metamorphic testing: Identifying invariant properties that always hold
- Property-based testing: Generative testing with automatic shrinking
- Visual AI: Detecting pixel-level UI regressions using computer vision
- Performance budgets: Setting and validating performance thresholds
- Shift-left testing: Early testing integration with development
- Mutation testing: Validating test effectiveness with code mutations

Generate test cases following 2025 best practices:
1. Write in Gherkin format when possible (Given/When/Then)
2. Include self-healing selectors (multiple fallback strategies)
3. Prioritize by risk score (critical > high > medium > low)
4. Add performance budgets and SLAs
5. Include chaos scenarios for resilience testing
6. Generate contract tests for API integrations
7. Create property-based tests for mathematical invariants
8. Add visual regression checkpoints
9. Include accessibility testing (WCAG 2.2 Level AA)
10. Generate mutation-resistant test assertions

For each test, provide:
- Business-readable Gherkin scenarios
- Multiple selector strategies for self-healing
- Risk assessment and prioritization score
- Performance expectations and budgets
- Expected behavior predictions using AI patterns
- Flakiness mitigation strategies
- Test impact analysis for maintenance

Remember: In 2025, tests must be:
- Self-maintaining through AI
- Business-readable for collaboration
- Risk-prioritized for efficiency
- Resilient to system changes
- Performance-aware with budgets
- Accessible and inclusive"""
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                
                response = query_llm(
                    provider=self.config.llm_provider,
                    model=self.config.llm_model,
                    messages=messages
                )
                
                content = response.choices[0].message.content
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                return {}
                
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt < self.config.llm_max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise


# ============================================================================
# RESULT MANAGER
# ============================================================================

class LiveResultManager:
    """Manage results from live testing."""
    
    def __init__(self, config: LiveProductionConfig):
        self.config = config
        self.results_dir = Path(config.results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_extraction(self, url: str, page_structure: PageStructure) -> Path:
        """Save live extraction results."""
        site_name = url.split('/')[2].replace('.', '_')
        file_path = self.results_dir / f"{self.session_id}_{site_name}_extraction.json"
        
        # Convert to serializable format
        data = {
            "url": page_structure.url,
            "timestamp": datetime.now().isoformat(),
            "page_type": page_structure.page_type,
            "business_purpose": page_structure.business_purpose,
            "total_elements": sum(len(elems) for elems in page_structure.elements_by_category.values()),
            "categories": {
                category.value: len(elements) 
                for category, elements in page_structure.elements_by_category.items()
            },
            "user_journeys": page_structure.user_journeys,
            "critical_paths": page_structure.critical_paths,
            "page_validations": page_structure.page_validations,
            "security_considerations": page_structure.security_considerations
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved extraction to {file_path}")
        return file_path
    
    def save_test_cases(self, url: str, test_cases: Dict[str, List]) -> Path:
        """Save generated test cases."""
        site_name = url.split('/')[2].replace('.', '_')
        file_path = self.results_dir / f"{self.session_id}_{site_name}_tests.json"
        
        data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "total_cases": sum(len(cases) for cases in test_cases.values()),
            "test_cases": test_cases
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved test cases to {file_path}")
        return file_path
    
    def save_summary(self, results: List[Dict]) -> Path:
        """Save overall summary."""
        file_path = self.results_dir / f"{self.session_id}_summary.json"
        
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Saved summary to {file_path}")
        return file_path


# ============================================================================
# MAIN LIVE PRODUCTION SYSTEM
# ============================================================================

class LiveProductionUITestSystem:
    """Production system using REAL browser automation on LIVE sites."""
    
    def __init__(self, config: Optional[LiveProductionConfig] = None):
        self.config = config or LiveProductionConfig()
        self.extractor = LiveBrowserExtractor(self.config)
        self.generator = LiveTestGenerator(self.config)
        self.result_manager = LiveResultManager(self.config)
        self.stats = {
            "start_time": datetime.now(),
            "sites_processed": 0,
            "elements_extracted": 0,
            "test_cases_generated": 0,
            "llm_calls": 0
        }
    
    async def process_site(self, url: str) -> Dict[str, Any]:
        """Process a live site with real browser automation."""
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing LIVE site: {url}")
        logger.info('='*60)
        
        result = {
            "url": url,
            "success": False,
            "extraction": None,
            "test_cases": None,
            "errors": []
        }
        
        try:
            # Step 1: Extract elements from LIVE site
            logger.info("Step 1: Extracting elements from LIVE page...")
            page_structure = await self.extractor.extract_from_url(url)
            
            # Save extraction results
            extraction_file = self.result_manager.save_extraction(url, page_structure)
            
            total_elements = sum(
                len(elements) for elements in page_structure.elements_by_category.values()
            )
            
            result["extraction"] = {
                "total_elements": total_elements,
                "categories": list(page_structure.elements_by_category.keys()),
                "page_type": page_structure.page_type,
                "file": str(extraction_file)
            }
            
            self.stats["elements_extracted"] += total_elements
            
            # Display extraction summary
            print(f"\n[LIVE EXTRACTION COMPLETE]")
            print(f"  URL: {url}")
            print(f"  Page Type: {page_structure.page_type}")
            print(f"  Total Elements: {total_elements}")
            print(f"  Categories: {', '.join(cat.value for cat in page_structure.elements_by_category.keys())}")
            
            if page_structure.user_journeys:
                print(f"\n  User Journeys Detected:")
                for journey in page_structure.user_journeys[:3]:
                    print(f"    - {journey.get('name', 'Unknown')}")
            
            if page_structure.critical_paths:
                print(f"\n  Critical Paths:")
                for path in page_structure.critical_paths[:3]:
                    print(f"    - {path.get('element', 'Unknown')}: {path.get('action', 'Unknown')}")
            
            # Step 2: Generate test cases based on LIVE data
            logger.info("Step 2: Generating test cases from LIVE elements...")
            test_cases = {}
            
            for strategy in self.config.test_strategies:
                logger.info(f"  Generating {strategy} tests...")
                cases = await self.generator.generate_tests(page_structure, strategy)
                test_cases[strategy] = cases
                self.stats["test_cases_generated"] += len(cases)
                
                # Rate limiting
                await asyncio.sleep(1)
            
            # Save test cases
            test_file = self.result_manager.save_test_cases(url, test_cases)
            
            result["test_cases"] = {
                "total": sum(len(cases) for cases in test_cases.values()),
                "by_strategy": {s: len(c) for s, c in test_cases.items()},
                "file": str(test_file)
            }
            
            self.stats["llm_calls"] = self.generator.llm_calls
            
            # Display test summary
            print(f"\n[TEST GENERATION COMPLETE]")
            print(f"  Total Test Cases: {result['test_cases']['total']}")
            for strategy, count in result['test_cases']['by_strategy'].items():
                print(f"    {strategy}: {count} cases")
            
            # Show sample test case
            for strategy, cases in test_cases.items():
                if cases and len(cases) > 0:
                    print(f"\n  Sample {strategy} test:")
                    case = cases[0]
                    print(f"    Title: {case.get('title', 'N/A')}")
                    print(f"    Priority: {case.get('priority', 'N/A')}")
                    if case.get('steps'):
                        print(f"    First Step: {case['steps'][0].get('action', 'N/A')}")
                    break
            
            result["success"] = True
            self.stats["sites_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            result["errors"].append(str(e))
            import traceback
            traceback.print_exc()
        
        return result
    
    async def run_tests(self, urls: List[str]) -> List[Dict]:
        """Run tests on multiple live sites."""
        results = []
        
        try:
            # Initialize browser once
            await self.extractor.initialize()
            
            for url in urls:
                result = await self.process_site(url)
                results.append(result)
                
                # Save intermediate results
                self.result_manager.save_summary(results)
                
                # Rate limiting between sites
                await asyncio.sleep(2)
            
        finally:
            # Always cleanup browser
            await self.extractor.cleanup()
        
        return results
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        runtime = (datetime.now() - self.stats["start_time"]).total_seconds()
        return {
            "runtime_seconds": runtime,
            "sites_processed": self.stats["sites_processed"],
            "elements_extracted": self.stats["elements_extracted"],
            "test_cases_generated": self.stats["test_cases_generated"],
            "llm_calls": self.stats["llm_calls"],
            "avg_elements_per_site": self.stats["elements_extracted"] / max(self.stats["sites_processed"], 1),
            "avg_cases_per_site": self.stats["test_cases_generated"] / max(self.stats["sites_processed"], 1)
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def run_live_production_tests():
    """Run production tests on LIVE websites."""
    
    # Configuration
    config = LiveProductionConfig(
        headless=False,  # Set to False to see browser in action
        stealth_level=StealthLevel.MAXIMUM,
        test_strategies=["critical_path", "validation", "security"],
        scenarios_per_strategy=2,
        save_screenshots=True
    )
    
    # Test sites
    test_sites = [
        "https://example.com",
        "https://quotes.toscrape.com",
        "https://github.com/login"
    ]
    
    print("\n" + "="*60)
    print("LIVE PRODUCTION UI TESTING SYSTEM")
    print("="*60)
    print("Testing REAL websites with LIVE browser automation")
    print(f"Sites to test: {', '.join(test_sites)}")
    print(f"Browser mode: {'Headless' if config.headless else 'Visible'}")
    print(f"Strategies: {', '.join(config.test_strategies)}")
    print(f"Results directory: {config.results_dir}/")
    print("="*60)
    
    # Initialize system
    system = LiveProductionUITestSystem(config)
    
    # Run tests on live sites
    results = await system.run_tests(test_sites)
    
    # Final summary
    print("\n" + "="*60)
    print("LIVE TESTING SUMMARY")
    print("="*60)
    
    stats = system.get_stats()
    print(f"Runtime: {stats['runtime_seconds']:.1f} seconds")
    print(f"Sites processed: {stats['sites_processed']}")
    print(f"Elements extracted (LIVE): {stats['elements_extracted']}")
    print(f"Test cases generated: {stats['test_cases_generated']}")
    print(f"LLM calls: {stats['llm_calls']}")
    print(f"Avg elements/site: {stats['avg_elements_per_site']:.1f}")
    print(f"Avg test cases/site: {stats['avg_cases_per_site']:.1f}")
    
    # Success/failure summary
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    print(f"\nSuccess rate: {successful}/{len(results)} sites")
    
    if failed > 0:
        print(f"Failed sites:")
        for r in results:
            if not r['success']:
                print(f"  - {r['url']}: {r['errors']}")
    
    # Save final summary
    summary_path = system.result_manager.save_summary({
        "stats": stats,
        "results": results,
        "config": {
            "headless": config.headless,
            "stealth_level": config.stealth_level.value,
            "strategies": config.test_strategies
        }
    })
    
    print(f"\nAll results saved to: {summary_path.parent}/")
    
    return results


if __name__ == "__main__":
    print("Starting LIVE Production UI Testing System")
    print("This will use REAL browser automation on LIVE websites")
    print("")
    
    try:
        # Check for required packages
        try:
            import playwright
            print("[OK] Playwright is installed")
        except ImportError:
            print("[WARNING] Playwright not installed. Installing...")
            os.system("pip install playwright")
            os.system("playwright install chromium")
        
        # Run the live tests
        results = asyncio.run(run_live_production_tests())
        print("\n[SUCCESS] Live testing completed!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()