"""
Context-aware reasoning engine for UI Testing v2
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..core.logging import get_logger
from ..models.common import ElementData, TestCase, BrowserType, FrameworkType, LanguageType
from .prompt_manager import PromptManager, ContextManager, PromptType

logger = get_logger("reasoning_engine")


class ReasoningType(str, Enum):
    """Types of reasoning tasks"""
    ELEMENT_CLASSIFICATION = "element_classification"
    TEST_STRATEGY = "test_strategy"
    CODE_OPTIMIZATION = "code_optimization"
    WORKFLOW_ANALYSIS = "workflow_analysis"
    ERROR_DIAGNOSIS = "error_diagnosis"
    PERFORMANCE_ANALYSIS = "performance_analysis"


@dataclass
class ReasoningResult:
    """Result of reasoning analysis"""
    task_type: ReasoningType
    confidence: float
    insights: List[str]
    recommendations: List[str]
    data: Dict[str, Any]
    reasoning_path: List[str]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ElementReasoner:
    """Reasons about UI elements and their relationships"""
    
    def __init__(self, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.logger = get_logger("element_reasoner")
    
    async def classify_elements(
        self,
        elements: List[ElementData],
        page_context: Dict[str, Any]
    ) -> ReasoningResult:
        """Classify elements and determine their functional roles"""
        
        reasoning_path = [
            "Analyzing element attributes and positioning",
            "Identifying interactive patterns",
            "Classifying by functional purpose",
            "Determining testing priority"
        ]
        
        classifications = {}
        insights = []
        recommendations = []
        
        # Group elements by type and position
        form_elements = []
        navigation_elements = []
        content_elements = []
        action_elements = []
        
        for element in elements:
            # Classify by tag name and attributes
            if element.tag_name in ['input', 'select', 'textarea']:
                form_elements.append(element)
            elif element.tag_name in ['nav', 'header'] or 'nav' in element.attributes.get('class', ''):
                navigation_elements.append(element)
            elif element.tag_name in ['button', 'a'] and element.is_interactive:
                action_elements.append(element)
            else:
                content_elements.append(element)
        
        # Analyze form patterns
        if form_elements:
            insights.append(f"Found {len(form_elements)} form elements - likely a form workflow")
            
            # Check for form validation patterns
            validation_elements = [e for e in form_elements if 'required' in e.attributes]
            if validation_elements:
                insights.append(f"Form has {len(validation_elements)} required fields - validation testing needed")
                recommendations.append("Generate validation test cases for required fields")
        
        # Analyze navigation patterns
        if navigation_elements:
            insights.append(f"Found {len(navigation_elements)} navigation elements")
            recommendations.append("Test navigation consistency and accessibility")
        
        # Analyze action elements
        if action_elements:
            primary_actions = [e for e in action_elements if 'primary' in e.attributes.get('class', '')]
            if primary_actions:
                insights.append(f"Found {len(primary_actions)} primary action buttons")
                recommendations.append("Prioritize testing of primary action flows")
        
        # Determine testing priorities
        priority_mapping = {}
        for element in elements:
            priority = self._calculate_testing_priority(element, page_context)
            priority_mapping[element.id] = priority
            classifications[element.id] = {
                "functional_role": self._determine_functional_role(element),
                "testing_priority": priority,
                "interaction_type": self._determine_interaction_type(element),
                "accessibility_concerns": self._identify_accessibility_concerns(element),
            }
        
        # Generate insights based on analysis
        critical_elements = [e for e in elements if priority_mapping[e.id] == "critical"]
        if critical_elements:
            insights.append(f"Identified {len(critical_elements)} critical elements requiring priority testing")
        
        return ReasoningResult(
            task_type=ReasoningType.ELEMENT_CLASSIFICATION,
            confidence=0.85,
            insights=insights,
            recommendations=recommendations,
            data={
                "classifications": classifications,
                "element_groups": {
                    "form_elements": [e.id for e in form_elements],
                    "navigation_elements": [e.id for e in navigation_elements],
                    "action_elements": [e.id for e in action_elements],
                    "content_elements": [e.id for e in content_elements],
                },
                "priority_summary": {
                    "critical": len([e for e in elements if priority_mapping[e.id] == "critical"]),
                    "high": len([e for e in elements if priority_mapping[e.id] == "high"]),
                    "medium": len([e for e in elements if priority_mapping[e.id] == "medium"]),
                    "low": len([e for e in elements if priority_mapping[e.id] == "low"]),
                }
            },
            reasoning_path=reasoning_path
        )
    
    def _calculate_testing_priority(self, element: ElementData, page_context: Dict[str, Any]) -> str:
        """Calculate testing priority for an element"""
        priority_score = 0
        
        # Interactive elements get higher priority
        if element.is_interactive:
            priority_score += 30
        
        # Form elements are usually critical
        if element.tag_name in ['input', 'select', 'textarea', 'button']:
            priority_score += 25
        
        # Elements with specific roles
        if 'submit' in element.attributes.get('type', ''):
            priority_score += 40
        if 'required' in element.attributes:
            priority_score += 20
        
        # Navigation elements
        if element.tag_name == 'a' or 'nav' in element.attributes.get('class', ''):
            priority_score += 15
        
        # Primary actions
        if 'primary' in element.attributes.get('class', '') or 'btn-primary' in element.attributes.get('class', ''):
            priority_score += 35
        
        # Size and visibility
        if element.position and element.position.get('width', 0) * element.position.get('height', 0) > 5000:
            priority_score += 10
        
        # Determine priority level
        if priority_score >= 60:
            return "critical"
        elif priority_score >= 40:
            return "high"
        elif priority_score >= 20:
            return "medium"
        else:
            return "low"
    
    def _determine_functional_role(self, element: ElementData) -> str:
        """Determine the functional role of an element"""
        # Login/auth patterns
        if any(keyword in element.text.lower() for keyword in ['login', 'sign in', 'authenticate']):
            return "authentication"
        if any(keyword in element.attributes.get('name', '').lower() for keyword in ['username', 'email', 'password']):
            return "authentication"
        
        # Form submission
        if element.attributes.get('type') == 'submit' or 'submit' in element.text.lower():
            return "form_submission"
        
        # Navigation
        if element.tag_name == 'a' or 'nav' in element.attributes.get('class', ''):
            return "navigation"
        
        # Search functionality
        if any(keyword in element.text.lower() for keyword in ['search', 'find']):
            return "search"
        if element.attributes.get('type') == 'search':
            return "search"
        
        # Data input
        if element.tag_name in ['input', 'textarea', 'select']:
            return "data_input"
        
        # Content display
        if element.tag_name in ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return "content_display"
        
        return "unknown"
    
    def _determine_interaction_type(self, element: ElementData) -> str:
        """Determine the type of interaction expected"""
        if not element.is_interactive:
            return "none"
        
        if element.tag_name == 'button' or element.attributes.get('type') == 'button':
            return "click"
        
        if element.tag_name == 'input':
            input_type = element.attributes.get('type', 'text')
            if input_type in ['text', 'email', 'password', 'tel', 'url']:
                return "type"
            elif input_type in ['checkbox', 'radio']:
                return "select"
            elif input_type == 'file':
                return "file_upload"
            else:
                return "click"
        
        if element.tag_name == 'select':
            return "select"
        
        if element.tag_name == 'textarea':
            return "type"
        
        if element.tag_name == 'a':
            return "navigate"
        
        return "click"
    
    def _identify_accessibility_concerns(self, element: ElementData) -> List[str]:
        """Identify potential accessibility concerns"""
        concerns = []
        
        # Missing labels
        if element.tag_name in ['input', 'select', 'textarea']:
            if not element.attributes.get('aria-label') and not element.attributes.get('aria-labelledby'):
                concerns.append("missing_label")
        
        # Small touch targets
        if element.position:
            width = element.position.get('width', 0)
            height = element.position.get('height', 0)
            if element.is_interactive and (width < 44 or height < 44):
                concerns.append("small_touch_target")
        
        # Missing alt text for images
        if element.tag_name == 'img' and not element.attributes.get('alt'):
            concerns.append("missing_alt_text")
        
        # Form validation
        if element.attributes.get('required') and not element.attributes.get('aria-describedby'):
            concerns.append("missing_error_description")
        
        return concerns


class TestStrategyReasoner:
    """Reasons about test strategies and optimization"""
    
    def __init__(self, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.logger = get_logger("test_strategy_reasoner")
    
    async def analyze_test_strategy(
        self,
        elements: List[ElementData],
        test_cases: List[TestCase],
        requirements: str,
        constraints: Dict[str, Any]
    ) -> ReasoningResult:
        """Analyze and optimize test strategy"""
        
        reasoning_path = [
            "Analyzing element coverage",
            "Evaluating test case effectiveness",
            "Identifying gaps in test coverage",
            "Optimizing test execution strategy"
        ]
        
        insights = []
        recommendations = []
        
        # Analyze element coverage
        covered_elements = set()
        for test_case in test_cases:
            for step in test_case.steps:
                if 'element' in step and hasattr(step['element'], 'id'):
                    covered_elements.add(step['element'].id)
        
        uncovered_elements = [e for e in elements if e.id not in covered_elements and e.is_interactive]
        
        if uncovered_elements:
            insights.append(f"Found {len(uncovered_elements)} interactive elements without test coverage")
            recommendations.append("Add test cases for uncovered interactive elements")
        
        # Analyze test case distribution
        priority_distribution = {}
        for test_case in test_cases:
            priority = test_case.priority.value
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        if priority_distribution.get('critical', 0) < 2:
            insights.append("Low number of critical test cases - may miss essential functionality")
            recommendations.append("Increase critical test case coverage for core workflows")
        
        # Analyze test execution efficiency
        total_duration = sum(getattr(tc, 'estimated_duration', 30) for tc in test_cases)
        if total_duration > constraints.get('max_execution_time', 300):
            insights.append(f"Estimated execution time ({total_duration}s) exceeds constraints")
            recommendations.append("Consider parallel execution or test case prioritization")
        
        # Check for test dependencies
        navigation_tests = [tc for tc in test_cases if any('navigate' in str(step) for step in tc.steps)]
        if len(navigation_tests) > len(test_cases) * 0.3:
            insights.append("High number of navigation-dependent tests detected")
            recommendations.append("Consider optimizing test data setup to reduce navigation overhead")
        
        return ReasoningResult(
            task_type=ReasoningType.TEST_STRATEGY,
            confidence=0.8,
            insights=insights,
            recommendations=recommendations,
            data={
                "coverage_analysis": {
                    "total_elements": len(elements),
                    "interactive_elements": len([e for e in elements if e.is_interactive]),
                    "covered_elements": len(covered_elements),
                    "uncovered_elements": len(uncovered_elements),
                    "coverage_percentage": len(covered_elements) / max(len([e for e in elements if e.is_interactive]), 1) * 100
                },
                "priority_distribution": priority_distribution,
                "execution_analysis": {
                    "total_test_cases": len(test_cases),
                    "estimated_duration": total_duration,
                    "parallel_potential": len([tc for tc in test_cases if not any('navigate' in str(step) for step in tc.steps)])
                }
            },
            reasoning_path=reasoning_path
        )


class WorkflowAnalyzer:
    """Analyzes user workflows and interaction patterns"""
    
    def __init__(self, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.logger = get_logger("workflow_analyzer")
    
    async def analyze_user_workflows(
        self,
        elements: List[ElementData],
        page_context: Dict[str, Any]
    ) -> ReasoningResult:
        """Analyze potential user workflows on the page"""
        
        reasoning_path = [
            "Identifying form workflows",
            "Mapping navigation patterns",
            "Analyzing interaction sequences",
            "Detecting critical user journeys"
        ]
        
        insights = []
        recommendations = []
        workflows = []
        
        # Identify form workflows
        form_workflows = await self._identify_form_workflows(elements)
        workflows.extend(form_workflows)
        
        if form_workflows:
            insights.append(f"Identified {len(form_workflows)} form-based workflows")
            recommendations.append("Create end-to-end tests for each form workflow")
        
        # Identify navigation workflows
        nav_workflows = await self._identify_navigation_workflows(elements)
        workflows.extend(nav_workflows)
        
        if nav_workflows:
            insights.append(f"Identified {len(nav_workflows)} navigation workflows")
            recommendations.append("Test navigation consistency and back-button behavior")
        
        # Identify search workflows
        search_workflows = await self._identify_search_workflows(elements)
        workflows.extend(search_workflows)
        
        if search_workflows:
            insights.append(f"Identified {len(search_workflows)} search workflows")
            recommendations.append("Test search functionality with various query types")
        
        # Analyze workflow complexity
        complex_workflows = [w for w in workflows if len(w.get('steps', [])) > 5]
        if complex_workflows:
            insights.append(f"Found {len(complex_workflows)} complex workflows requiring careful testing")
            recommendations.append("Break down complex workflows into smaller test scenarios")
        
        return ReasoningResult(
            task_type=ReasoningType.WORKFLOW_ANALYSIS,
            confidence=0.75,
            insights=insights,
            recommendations=recommendations,
            data={
                "workflows": workflows,
                "workflow_types": {
                    "form_workflows": len(form_workflows),
                    "navigation_workflows": len(nav_workflows),
                    "search_workflows": len(search_workflows)
                },
                "complexity_analysis": {
                    "simple_workflows": len([w for w in workflows if len(w.get('steps', [])) <= 3]),
                    "medium_workflows": len([w for w in workflows if 3 < len(w.get('steps', [])) <= 5]),
                    "complex_workflows": len(complex_workflows)
                }
            },
            reasoning_path=reasoning_path
        )
    
    async def _identify_form_workflows(self, elements: List[ElementData]) -> List[Dict[str, Any]]:
        """Identify form-based workflows"""
        workflows = []
        
        # Group form elements
        form_elements = [e for e in elements if e.tag_name in ['input', 'select', 'textarea']]
        submit_buttons = [e for e in elements if e.tag_name == 'button' and 'submit' in e.attributes.get('type', '')]
        
        if form_elements and submit_buttons:
            for submit_button in submit_buttons:
                workflow = {
                    "type": "form_submission",
                    "name": f"Submit form via {submit_button.text or submit_button.id}",
                    "steps": [],
                    "complexity": "medium"
                }
                
                # Add form filling steps
                for element in form_elements:
                    workflow["steps"].append({
                        "action": "fill",
                        "element": element.id,
                        "description": f"Fill {element.attributes.get('name', element.id)}"
                    })
                
                # Add submission step
                workflow["steps"].append({
                    "action": "click",
                    "element": submit_button.id,
                    "description": f"Submit form"
                })
                
                workflows.append(workflow)
        
        return workflows
    
    async def _identify_navigation_workflows(self, elements: List[ElementData]) -> List[Dict[str, Any]]:
        """Identify navigation workflows"""
        workflows = []
        
        nav_elements = [e for e in elements if e.tag_name == 'a' or 'nav' in e.attributes.get('class', '')]
        
        for nav_element in nav_elements:
            if nav_element.text and nav_element.is_interactive:
                workflow = {
                    "type": "navigation",
                    "name": f"Navigate to {nav_element.text}",
                    "steps": [
                        {
                            "action": "click",
                            "element": nav_element.id,
                            "description": f"Click {nav_element.text} link"
                        }
                    ],
                    "complexity": "simple"
                }
                workflows.append(workflow)
        
        return workflows
    
    async def _identify_search_workflows(self, elements: List[ElementData]) -> List[Dict[str, Any]]:
        """Identify search workflows"""
        workflows = []
        
        search_inputs = [e for e in elements if 
                        e.tag_name == 'input' and 
                        ('search' in e.attributes.get('type', '') or 
                         'search' in e.attributes.get('name', '').lower() or
                         'search' in e.text.lower())]
        
        search_buttons = [e for e in elements if 
                         e.tag_name == 'button' and 
                         'search' in e.text.lower()]
        
        if search_inputs:
            for search_input in search_inputs:
                # Find associated search button
                search_button = None
                if search_buttons:
                    search_button = search_buttons[0]  # Assume first search button
                
                workflow = {
                    "type": "search",
                    "name": "Perform search",
                    "steps": [
                        {
                            "action": "fill",
                            "element": search_input.id,
                            "description": "Enter search query"
                        }
                    ],
                    "complexity": "simple"
                }
                
                if search_button:
                    workflow["steps"].append({
                        "action": "click",
                        "element": search_button.id,
                        "description": "Click search button"
                    })
                else:
                    workflow["steps"].append({
                        "action": "press_key",
                        "element": search_input.id,
                        "key": "Enter",
                        "description": "Press Enter to search"
                    })
                
                workflows.append(workflow)
        
        return workflows


class ReasoningEngine:
    """Main reasoning engine that coordinates different reasoning components"""
    
    def __init__(self, prompt_manager: Optional[PromptManager] = None):
        self.prompt_manager = prompt_manager or PromptManager()
        self.context_manager = ContextManager()
        
        # Initialize reasoners
        self.element_reasoner = ElementReasoner(self.prompt_manager)
        self.test_strategy_reasoner = TestStrategyReasoner(self.prompt_manager)
        self.workflow_analyzer = WorkflowAnalyzer(self.prompt_manager)
        
        self.logger = get_logger("reasoning_engine")
        self.logger.info("Reasoning engine initialized")
    
    async def analyze_elements(
        self,
        elements: List[ElementData],
        page_context: Dict[str, Any]
    ) -> ReasoningResult:
        """Perform comprehensive element analysis"""
        result = await self.element_reasoner.classify_elements(elements, page_context)
        
        # Add to context for future reasoning
        self.context_manager.update_workflow_context("last_element_analysis", result.data)
        
        return result
    
    async def analyze_test_strategy(
        self,
        elements: List[ElementData],
        test_cases: List[TestCase],
        requirements: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> ReasoningResult:
        """Analyze and optimize test strategy"""
        constraints = constraints or {}
        result = await self.test_strategy_reasoner.analyze_test_strategy(
            elements, test_cases, requirements, constraints
        )
        
        # Add to context
        self.context_manager.update_workflow_context("last_test_strategy", result.data)
        
        return result
    
    async def analyze_workflows(
        self,
        elements: List[ElementData],
        page_context: Dict[str, Any]
    ) -> ReasoningResult:
        """Analyze user workflows"""
        result = await self.workflow_analyzer.analyze_user_workflows(elements, page_context)
        
        # Add to context
        self.context_manager.update_workflow_context("last_workflow_analysis", result.data)
        
        return result
    
    async def comprehensive_analysis(
        self,
        elements: List[ElementData],
        page_context: Dict[str, Any],
        test_cases: Optional[List[TestCase]] = None,
        requirements: str = ""
    ) -> Dict[str, ReasoningResult]:
        """Perform comprehensive analysis combining all reasoning types"""
        
        self.logger.info("Starting comprehensive analysis")
        
        results = {}
        
        # Element analysis
        results["elements"] = await self.analyze_elements(elements, page_context)
        
        # Workflow analysis
        results["workflows"] = await self.analyze_workflows(elements, page_context)
        
        # Test strategy analysis (if test cases provided)
        if test_cases:
            results["test_strategy"] = await self.analyze_test_strategy(
                elements, test_cases, requirements
            )
        
        # Generate meta-insights combining all analyses
        meta_insights = self._generate_meta_insights(results)
        
        results["meta_analysis"] = ReasoningResult(
            task_type=ReasoningType.WORKFLOW_ANALYSIS,
            confidence=0.9,
            insights=meta_insights["insights"],
            recommendations=meta_insights["recommendations"],
            data=meta_insights["data"],
            reasoning_path=["Combining element, workflow, and test strategy analyses"]
        )
        
        self.logger.info("Comprehensive analysis completed")
        
        return results
    
    def _generate_meta_insights(self, results: Dict[str, ReasoningResult]) -> Dict[str, Any]:
        """Generate insights combining multiple analyses"""
        insights = []
        recommendations = []
        
        # Cross-reference element and workflow analysis
        if "elements" in results and "workflows" in results:
            element_data = results["elements"].data
            workflow_data = results["workflows"].data
            
            critical_elements = element_data.get("priority_summary", {}).get("critical", 0)
            complex_workflows = workflow_data.get("complexity_analysis", {}).get("complex_workflows", 0)
            
            if critical_elements > 0 and complex_workflows > 0:
                insights.append(f"Page has {critical_elements} critical elements and {complex_workflows} complex workflows - requires thorough testing")
                recommendations.append("Focus on end-to-end testing of complex workflows involving critical elements")
        
        # Test coverage insights
        if "test_strategy" in results:
            test_data = results["test_strategy"].data
            coverage = test_data.get("coverage_analysis", {}).get("coverage_percentage", 0)
            
            if coverage < 80:
                insights.append(f"Test coverage is {coverage:.1f}% - below recommended threshold")
                recommendations.append("Increase test coverage to at least 80% of interactive elements")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "data": {
                "analysis_types": list(results.keys()),
                "combined_confidence": sum(r.confidence for r in results.values()) / len(results),
                "total_insights": sum(len(r.insights) for r in results.values()),
                "total_recommendations": sum(len(r.recommendations) for r in results.values())
            }
        }
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get reasoning engine context summary"""
        return {
            "context_manager": self.context_manager.get_context_summary(),
            "available_reasoners": ["element", "test_strategy", "workflow"],
            "prompt_templates": len(self.prompt_manager.list_templates()),
        }
