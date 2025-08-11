"""
Prompt management system for UI Testing v2
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from ..core.logging import get_logger
from ..models.common import ElementData, TestCase, FrameworkType, LanguageType

logger = get_logger("prompt_manager")


class PromptType(str, Enum):
    """Types of prompts for different tasks"""
    ELEMENT_ANALYSIS = "element_analysis"
    TEST_GENERATION = "test_generation"
    CODE_GENERATION = "code_generation"
    TEST_OPTIMIZATION = "test_optimization"
    ELEMENT_EXTRACTION = "element_extraction"
    PAGE_ANALYSIS = "page_analysis"
    ACCESSIBILITY_CHECK = "accessibility_check"
    BUG_DETECTION = "bug_detection"


@dataclass
class PromptTemplate:
    """Template for AI prompts"""
    name: str
    type: PromptType
    template: str
    variables: List[str]
    description: str
    version: str = "1.0"
    created_at: str = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.tags is None:
            self.tags = []


class PromptManager:
    """Manages AI prompts and templates"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent / "prompts"
        self.templates_dir.mkdir(exist_ok=True)
        
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
        self._load_custom_templates()
        
        logger.info(f"Prompt manager initialized with {len(self._templates)} templates")
    
    def _load_default_templates(self):
        """Load default prompt templates"""
        
        # Element Analysis Template
        self.register_template(PromptTemplate(
            name="element_analysis",
            type=PromptType.ELEMENT_ANALYSIS,
            template="""
You are an expert UI/UX analyzer. Analyze the following web page elements and provide insights.

Elements to analyze:
{elements_json}

Page URL: {url}
Page Title: {page_title}

Please provide a comprehensive analysis including:

1. **Element Classification**: Categorize each element (button, input, navigation, content, etc.)
2. **User Interaction Patterns**: Identify common user workflows and interaction patterns
3. **Accessibility Assessment**: Check for accessibility compliance and potential issues
4. **Test Priority**: Rank elements by testing importance (critical, high, medium, low)
5. **Potential Issues**: Identify any UI/UX issues or inconsistencies

For each element, provide:
- Functional purpose and role in the application
- User interaction expectations
- Potential edge cases or error conditions
- Suggested test scenarios

Return your analysis in structured JSON format with clear categorization.
""",
            variables=["elements_json", "url", "page_title"],
            description="Analyzes UI elements for testing insights",
            tags=["element", "analysis", "ui", "accessibility"]
        ))
        
        # Test Generation Template
        self.register_template(PromptTemplate(
            name="comprehensive_test_generation",
            type=PromptType.TEST_GENERATION,
            template="""
You are an expert test automation engineer. Generate comprehensive test cases based on the provided elements and requirements.

**Context:**
- Page URL: {url}
- Application Type: {app_type}
- Test Requirements: {requirements}

**Elements Available:**
{elements_json}

**Generate test cases covering:**

1. **Functional Testing**:
   - Happy path scenarios
   - Edge cases and boundary conditions
   - Error handling and validation
   - User workflow completion

2. **UI Testing**:
   - Element visibility and responsiveness
   - Layout consistency across browsers
   - Interactive element behavior

3. **Accessibility Testing**:
   - Keyboard navigation
   - Screen reader compatibility
   - Color contrast and readability
   - ARIA attributes validation

4. **Performance Testing**:
   - Page load and element rendering
   - User interaction response times

**For each test case, provide:**
- Unique test ID and descriptive title
- Detailed step-by-step actions
- Expected results and assertions
- Priority level (critical/high/medium/low)
- Test data requirements
- Prerequisites and setup needs
- Estimated execution time

**Test Case Format:**
```json
{
  "id": "test_unique_id",
  "title": "Descriptive Test Title",
  "description": "What this test validates",
  "steps": [
    {
      "action": "click|type|select|wait|navigate|hover|scroll",
      "element": "element_selector_or_description",
      "value": "input_value_if_needed",
      "description": "Human readable step description"
    }
  ],
  "assertions": [
    {
      "type": "element_visible|element_text|url_contains|page_title",
      "target": "selector_or_value",
      "expected": "expected_value",
      "description": "What should be verified"
    }
  ],
  "priority": "critical|high|medium|low",
  "estimated_duration": 30,
  "tags": ["login", "functional", "critical"],
  "prerequisites": ["User account exists"],
  "test_data": {
    "username": "test_user",
    "password": "test_pass"
  }
}
```

Generate at least {min_test_cases} test cases, focusing on the most critical functionality first.
""",
            variables=["url", "app_type", "requirements", "elements_json", "min_test_cases"],
            description="Generates comprehensive test cases from UI elements",
            tags=["test", "generation", "comprehensive", "automation"]
        ))
        
        # Code Generation Template  
        self.register_template(PromptTemplate(
            name="code_generation",
            type=PromptType.CODE_GENERATION,
            template="""
You are an expert test automation engineer specializing in {framework} with {language}.

Generate production-ready test automation code for the following test cases:

**Framework**: {framework}
**Language**: {language}
**Test Cases**:
{test_cases_json}

**Requirements:**
1. **Best Practices**: Follow {framework} and {language} best practices
2. **Page Object Model**: Use page object pattern where appropriate
3. **Maintainability**: Write clean, readable, and maintainable code
4. **Error Handling**: Include proper error handling and logging
5. **Async/Await**: Use async patterns for modern frameworks
6. **Assertions**: Use appropriate assertion libraries
7. **Data Management**: Handle test data efficiently
8. **Browser Management**: Proper browser lifecycle management

**Code Structure:**
- Test class/module organization
- Setup and teardown methods
- Reusable utility functions
- Configuration management
- Reporting integration

**Include:**
- Main test file with all test methods
- Page object classes (if applicable)
- Configuration files (pytest.ini, package.json, etc.)
- Setup/installation instructions
- Dependencies list

**Quality Standards:**
- Code should be production-ready
- Include comments for complex logic
- Follow naming conventions
- Add proper typing/type hints
- Include docstrings for methods

Generate complete, executable code that can be run immediately after setup.
""",
            variables=["framework", "language", "test_cases_json"],
            description="Generates test automation code for specific frameworks",
            tags=["code", "generation", "automation", "framework"]
        ))
        
        # Element Extraction Template
        self.register_template(PromptTemplate(
            name="element_extraction_guidance",
            type=PromptType.ELEMENT_EXTRACTION,
            template="""
You are an expert web automation engineer. Analyze this webpage screenshot and provide guidance for element extraction.

**Context:**
- URL: {url}
- Screenshot: {screenshot_path}
- Page Title: {page_title}
- Viewport: {viewport_width}x{viewport_height}

**Analysis Tasks:**

1. **Element Identification**:
   - Identify all interactive elements (buttons, inputs, links, dropdowns)
   - Locate navigation elements and menus
   - Find content areas and containers
   - Detect modal dialogs or overlays

2. **Selector Strategy**:
   - Suggest the most reliable selector strategy for each element
   - Prioritize: ID > data-testid > class > xpath > css
   - Identify potentially unstable selectors
   - Recommend attribute additions for better testability

3. **Page Layout Analysis**:
   - Identify responsive design patterns
   - Detect dynamic content areas
   - Find loading states or spinners
   - Locate error message containers

4. **Automation Challenges**:
   - Identify elements that may be difficult to automate
   - Detect timing-sensitive interactions
   - Find elements that require special handling (file uploads, drag-drop)
   - Spot potential race conditions

5. **Recommendations**:
   - Suggest improvements for testability
   - Recommend data-testid additions
   - Identify missing ARIA labels
   - Propose page object model structure

**Output Format:**
Provide structured analysis in JSON format with element locations, recommended selectors, and automation strategies.
""",
            variables=["url", "screenshot_path", "page_title", "viewport_width", "viewport_height"],
            description="Guides element extraction strategy from screenshots",
            tags=["extraction", "guidance", "screenshot", "analysis"]
        ))
        
        # Accessibility Check Template
        self.register_template(PromptTemplate(
            name="accessibility_analysis",
            type=PromptType.ACCESSIBILITY_CHECK,
            template="""
You are an accessibility expert and WCAG compliance specialist. Analyze the provided elements for accessibility issues.

**Elements to Analyze:**
{elements_json}

**Page Context:**
- URL: {url}
- Page Type: {page_type}

**Accessibility Guidelines to Check:**

1. **WCAG 2.1 Level AA Compliance**:
   - Color contrast ratios (4.5:1 for normal text, 3:1 for large text)
   - Keyboard navigation support
   - Screen reader compatibility
   - Focus management

2. **Semantic HTML**:
   - Proper heading hierarchy (h1-h6)
   - Form label associations
   - Button vs link usage
   - ARIA roles and attributes

3. **Interactive Elements**:
   - Touch target sizes (minimum 44x44px)
   - Focus indicators
   - Tab order logic
   - Keyboard shortcuts

4. **Content Accessibility**:
   - Alternative text for images
   - Video captions and transcripts
   - Clear error messages
   - Consistent navigation

**Analysis Areas:**

1. **Critical Issues** (WCAG violations):
   - Missing alt text
   - Insufficient color contrast
   - Missing form labels
   - Inaccessible keyboard navigation

2. **Warning Issues** (Best practice violations):
   - Small touch targets
   - Poor focus indicators
   - Inconsistent navigation
   - Missing ARIA descriptions

3. **Recommendations**:
   - Specific ARIA attributes to add
   - Color contrast improvements
   - Keyboard navigation enhancements
   - Screen reader optimizations

**Output Format:**
```json
{
  "accessibility_score": 85,
  "wcag_level": "AA",
  "critical_issues": [...],
  "warnings": [...],
  "recommendations": [...],
  "element_analysis": {...}
}
```

Provide actionable recommendations for each issue found.
""",
            variables=["elements_json", "url", "page_type"],
            description="Analyzes elements for accessibility compliance",
            tags=["accessibility", "wcag", "compliance", "analysis"]
        ))
    
    def _load_custom_templates(self):
        """Load custom templates from files"""
        if not self.templates_dir.exists():
            return
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                template = PromptTemplate(**template_data)
                self._templates[template.name] = template
                logger.debug(f"Loaded custom template: {template.name}")
                
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")
    
    def register_template(self, template: PromptTemplate) -> None:
        """Register a new prompt template"""
        self._templates[template.name] = template
        logger.debug(f"Registered template: {template.name}")
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        return self._templates.get(name)
    
    def list_templates(self, type_filter: Optional[PromptType] = None) -> List[PromptTemplate]:
        """List available templates, optionally filtered by type"""
        templates = list(self._templates.values())
        
        if type_filter:
            templates = [t for t in templates if t.type == type_filter]
        
        return sorted(templates, key=lambda t: t.name)
    
    def render_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any],
        **kwargs: Any
    ) -> str:
        """Render a prompt template with variables"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Merge variables with kwargs
        all_variables = {**variables, **kwargs}
        
        # Check for missing variables
        missing_vars = set(template.variables) - set(all_variables.keys())
        if missing_vars:
            raise ValueError(f"Missing variables for template '{template_name}': {missing_vars}")
        
        # Render template
        try:
            rendered = template.template.format(**all_variables)
            logger.debug(f"Rendered prompt template: {template_name}")
            return rendered
            
        except KeyError as e:
            raise ValueError(f"Template variable error in '{template_name}': {e}")
    
    def save_template(self, template: PromptTemplate) -> None:
        """Save a template to file"""
        template_file = self.templates_dir / f"{template.name}.json"
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(template), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved template to {template_file}")
            
        except Exception as e:
            logger.error(f"Failed to save template {template.name}: {e}")
            raise
    
    def create_element_analysis_prompt(
        self,
        elements: List[ElementData],
        url: str,
        page_title: str = ""
    ) -> str:
        """Create prompt for element analysis"""
        elements_json = json.dumps([
            {
                "id": elem.id,
                "tag_name": elem.tag_name,
                "text": elem.text,
                "attributes": elem.attributes,
                "selectors": {k.value: v for k, v in elem.selectors.items()},
                "position": elem.position,
                "is_visible": elem.is_visible,
                "is_interactive": elem.is_interactive,
                "accessibility_info": elem.accessibility_info,
            }
            for elem in elements
        ], indent=2)
        
        return self.render_prompt(
            "element_analysis",
            {
                "elements_json": elements_json,
                "url": url,
                "page_title": page_title or "Unknown",
            }
        )
    
    def create_test_generation_prompt(
        self,
        elements: List[ElementData],
        url: str,
        requirements: str = "",
        app_type: str = "web application",
        min_test_cases: int = 5
    ) -> str:
        """Create prompt for test case generation"""
        elements_json = json.dumps([
            {
                "id": elem.id,
                "tag_name": elem.tag_name,
                "text": elem.text,
                "attributes": elem.attributes,
                "selectors": {k.value: v for k, v in elem.selectors.items()},
                "is_interactive": elem.is_interactive,
            }
            for elem in elements
        ], indent=2)
        
        return self.render_prompt(
            "comprehensive_test_generation",
            {
                "elements_json": elements_json,
                "url": url,
                "requirements": requirements or "Comprehensive testing of all functionality",
                "app_type": app_type,
                "min_test_cases": min_test_cases,
            }
        )
    
    def create_code_generation_prompt(
        self,
        test_cases: List[TestCase],
        framework: FrameworkType,
        language: LanguageType
    ) -> str:
        """Create prompt for code generation"""
        test_cases_json = json.dumps([
            {
                "id": tc.id,
                "title": tc.title,
                "description": tc.description,
                "steps": tc.steps,
                "assertions": tc.assertions,
                "priority": tc.priority.value,
                "tags": tc.tags,
                "test_data": getattr(tc, 'test_data', {}),
            }
            for tc in test_cases
        ], indent=2)
        
        return self.render_prompt(
            "code_generation",
            {
                "test_cases_json": test_cases_json,
                "framework": framework.value,
                "language": language.value,
            }
        )
    
    def create_accessibility_prompt(
        self,
        elements: List[ElementData],
        url: str,
        page_type: str = "web page"
    ) -> str:
        """Create prompt for accessibility analysis"""
        elements_json = json.dumps([
            {
                "id": elem.id,
                "tag_name": elem.tag_name,
                "text": elem.text,
                "attributes": elem.attributes,
                "position": elem.position,
                "accessibility_info": elem.accessibility_info,
            }
            for elem in elements
        ], indent=2)
        
        return self.render_prompt(
            "accessibility_analysis",
            {
                "elements_json": elements_json,
                "url": url,
                "page_type": page_type,
            }
        )


class ContextManager:
    """Manages conversation context and memory for AI interactions"""
    
    def __init__(self, max_context_length: int = 10000):
        self.max_context_length = max_context_length
        self.conversation_history: List[Dict[str, Any]] = []
        self.workflow_context: Dict[str, Any] = {}
        self.learning_insights: List[Dict[str, Any]] = []
        
        logger.info("Context manager initialized")
    
    def add_interaction(
        self,
        prompt: str,
        response: str,
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an AI interaction to conversation history"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "prompt": prompt[:1000],  # Truncate long prompts
            "response": response[:2000],  # Truncate long responses
            "metadata": metadata or {},
        }
        
        self.conversation_history.append(interaction)
        
        # Trim history if too long
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-40:]
        
        logger.debug(f"Added interaction: {interaction_type}")
    
    def update_workflow_context(self, key: str, value: Any) -> None:
        """Update workflow context"""
        self.workflow_context[key] = value
        logger.debug(f"Updated workflow context: {key}")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        return {
            "conversation_length": len(self.conversation_history),
            "workflow_context": self.workflow_context,
            "recent_interactions": self.conversation_history[-5:],
            "learning_insights_count": len(self.learning_insights),
        }
    
    def add_learning_insight(
        self,
        insight: str,
        category: str,
        confidence: float,
        source: str
    ) -> None:
        """Add a learning insight from AI interactions"""
        learning_item = {
            "timestamp": datetime.now().isoformat(),
            "insight": insight,
            "category": category,
            "confidence": confidence,
            "source": source,
        }
        
        self.learning_insights.append(learning_item)
        
        # Keep only recent insights
        if len(self.learning_insights) > 100:
            self.learning_insights = self.learning_insights[-80:]
        
        logger.info(f"Added learning insight: {category}")
    
    def get_relevant_context(self, current_task: str) -> str:
        """Get relevant context for current task"""
        # Simple context retrieval - could be enhanced with embeddings/similarity
        relevant_interactions = []
        
        for interaction in self.conversation_history[-10:]:
            if current_task.lower() in interaction["prompt"].lower():
                relevant_interactions.append(interaction)
        
        if not relevant_interactions:
            return ""
        
        context_parts = []
        for interaction in relevant_interactions:
            context_parts.append(f"Previous {interaction['type']}: {interaction['response'][:200]}...")
        
        return "\n".join(context_parts)


# Global prompt manager instance
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """Get global prompt manager instance"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
