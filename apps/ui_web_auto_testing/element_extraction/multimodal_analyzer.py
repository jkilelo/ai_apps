"""
Multimodal Element Analyzer using Vision LLMs
Combines visual analysis with DOM parsing for comprehensive element detection
"""

import base64
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from io import BytesIO
from PIL import Image
import asyncio

logger = logging.getLogger(__name__)


class VisualElementType(Enum):
    """Types of visual elements detected"""
    BUTTON = "button"
    INPUT_FIELD = "input_field"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    LINK = "link"
    IMAGE = "image"
    VIDEO = "video"
    MODAL = "modal"
    NAVIGATION = "navigation"
    FORM = "form"
    TABLE = "table"
    CHART = "chart"
    LOADING = "loading_indicator"
    ADVERTISEMENT = "advertisement"
    POPUP = "popup"
    TOOLTIP = "tooltip"
    ERROR_MESSAGE = "error_message"
    SUCCESS_MESSAGE = "success_message"
    WARNING_MESSAGE = "warning_message"


@dataclass
class VisualElement:
    """Represents an element detected through visual analysis"""
    element_type: VisualElementType
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    text_content: Optional[str]
    visual_description: str
    interaction_hints: List[str]
    accessibility_concerns: List[str]
    test_suggestions: List[str]


@dataclass
class PageVisualAnalysis:
    """Complete visual analysis of a page"""
    layout_type: str  # e.g., "e-commerce", "dashboard", "form", "article"
    visual_hierarchy: List[str]
    color_scheme: Dict[str, str]
    accessibility_score: float
    ui_patterns: List[str]
    dynamic_regions: List[Dict[str, Any]]
    visual_elements: List[VisualElement]


class MultimodalElementAnalyzer:
    """Analyzes web pages using multimodal LLMs for enhanced element detection"""
    
    # Prompt templates for different analysis tasks
    ELEMENT_DETECTION_PROMPT = """
Analyze this web page screenshot and identify all interactive UI elements.

For each element found, provide:
1. Element type (button, input, dropdown, etc.)
2. Bounding box coordinates [x, y, width, height]
3. Text content or label
4. Visual description
5. Possible interactions (click, type, select, etc.)
6. Accessibility concerns if any
7. Test case suggestions

Also identify:
- Dynamic regions that might update (live data, animations, etc.)
- Hidden or partially visible elements
- Elements that might appear on interaction (dropdowns, tooltips, modals)

Format the response as JSON with the following structure:
{
    "elements": [...],
    "dynamic_regions": [...],
    "layout_analysis": {...}
}
"""

    ELEMENT_STATE_ANALYSIS_PROMPT = """
Compare these two screenshots taken before and after user interaction.

Identify:
1. What changed between the screenshots
2. New elements that appeared
3. Elements that disappeared
4. State changes (enabled/disabled, selected/unselected, etc.)
5. Visual feedback (color changes, animations, loading states)
6. Error or success messages

This helps understand dynamic behavior for test generation.
"""

    TEST_GENERATION_PROMPT = """
Based on this UI screenshot and the identified elements, generate comprehensive test scenarios.

Consider:
1. Happy path flows
2. Edge cases and error conditions
3. Accessibility requirements
4. Performance considerations
5. Cross-browser compatibility
6. Mobile responsiveness
7. Security implications

For each test scenario, provide:
- Test name
- Preconditions
- Test steps
- Expected results
- Test data requirements
- Priority (critical, high, medium, low)
"""

    def __init__(self, vision_model: str = "gpt-4-vision-preview"):
        self.vision_model = vision_model
        self.llm_client = None  # Initialize based on model choice
        self._initialize_llm_client()
        
    def _initialize_llm_client(self):
        """Initialize the appropriate LLM client based on model choice"""
        if "gpt" in self.vision_model:
            from openai import AsyncOpenAI
            self.llm_client = AsyncOpenAI()
            self.model_type = "openai"
        elif "claude" in self.vision_model:
            import anthropic
            self.llm_client = anthropic.AsyncAnthropic()
            self.model_type = "anthropic"
        else:
            # Default to OpenAI-compatible endpoint
            from openai import AsyncOpenAI
            self.llm_client = AsyncOpenAI()
            self.model_type = "openai"
    
    async def analyze_screenshot(
        self, 
        screenshot: bytes, 
        page_context: Dict[str, Any],
        include_test_suggestions: bool = True
    ) -> PageVisualAnalysis:
        """Analyze a page screenshot using vision LLM"""
        logger.info("Starting multimodal analysis of screenshot")
        
        # Convert screenshot to base64
        base64_image = base64.b64encode(screenshot).decode('utf-8')
        
        # Prepare messages for vision model
        messages = [
            {
                "role": "system",
                "content": "You are an expert UI/UX analyst and test automation engineer."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.ELEMENT_DETECTION_PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        try:
            # Call vision model
            response = await self._call_vision_model(messages)
            
            # Parse response
            analysis_data = self._parse_vision_response(response)
            
            # Convert to structured format
            visual_elements = [
                VisualElement(
                    element_type=VisualElementType(elem.get("type", "button")),
                    bounding_box=tuple(elem.get("bounding_box", [0, 0, 0, 0])),
                    confidence=elem.get("confidence", 0.5),
                    text_content=elem.get("text_content"),
                    visual_description=elem.get("description", ""),
                    interaction_hints=elem.get("interactions", []),
                    accessibility_concerns=elem.get("accessibility_concerns", []),
                    test_suggestions=elem.get("test_suggestions", []) if include_test_suggestions else []
                )
                for elem in analysis_data.get("elements", [])
            ]
            
            # Create page analysis
            page_analysis = PageVisualAnalysis(
                layout_type=analysis_data.get("layout_analysis", {}).get("type", "unknown"),
                visual_hierarchy=analysis_data.get("layout_analysis", {}).get("hierarchy", []),
                color_scheme=analysis_data.get("layout_analysis", {}).get("colors", {}),
                accessibility_score=analysis_data.get("layout_analysis", {}).get("accessibility_score", 0.0),
                ui_patterns=analysis_data.get("layout_analysis", {}).get("patterns", []),
                dynamic_regions=analysis_data.get("dynamic_regions", []),
                visual_elements=visual_elements
            )
            
            logger.info(f"Visual analysis complete: Found {len(visual_elements)} elements")
            
            # Generate test suggestions if requested
            if include_test_suggestions:
                test_suggestions = await self.generate_test_suggestions(
                    screenshot, 
                    visual_elements,
                    page_context
                )
                # Merge test suggestions into elements
                for elem, suggestions in zip(visual_elements, test_suggestions):
                    elem.test_suggestions.extend(suggestions)
            
            return page_analysis
            
        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            # Return empty analysis on error
            return PageVisualAnalysis(
                layout_type="unknown",
                visual_hierarchy=[],
                color_scheme={},
                accessibility_score=0.0,
                ui_patterns=[],
                dynamic_regions=[],
                visual_elements=[]
            )
    
    async def compare_screenshots(
        self,
        before_screenshot: bytes,
        after_screenshot: bytes,
        action_performed: str
    ) -> Dict[str, Any]:
        """Compare screenshots to detect UI changes after an action"""
        logger.info(f"Comparing screenshots after action: {action_performed}")
        
        # Convert screenshots to base64
        before_base64 = base64.b64encode(before_screenshot).decode('utf-8')
        after_base64 = base64.b64encode(after_screenshot).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{self.ELEMENT_STATE_ANALYSIS_PROMPT}\n\nAction performed: {action_performed}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{before_base64}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{after_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        try:
            response = await self._call_vision_model(messages)
            changes = self._parse_vision_response(response)
            
            return {
                "action": action_performed,
                "changes_detected": changes.get("changes", []),
                "new_elements": changes.get("new_elements", []),
                "removed_elements": changes.get("removed_elements", []),
                "state_changes": changes.get("state_changes", []),
                "visual_feedback": changes.get("visual_feedback", []),
                "messages": changes.get("messages", [])
            }
            
        except Exception as e:
            logger.error(f"Screenshot comparison failed: {e}")
            return {"error": str(e)}
    
    async def generate_test_suggestions(
        self,
        screenshot: bytes,
        detected_elements: List[VisualElement],
        page_context: Dict[str, Any]
    ) -> List[List[str]]:
        """Generate test suggestions for detected elements"""
        logger.info("Generating test suggestions based on visual analysis")
        
        # Prepare element summary for prompt
        element_summary = self._create_element_summary(detected_elements)
        
        base64_image = base64.b64encode(screenshot).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{self.TEST_GENERATION_PROMPT}\n\nDetected elements:\n{element_summary}\n\nPage context:\n{page_context}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        try:
            response = await self._call_vision_model(messages)
            test_data = self._parse_vision_response(response)
            
            # Map test suggestions to elements
            test_suggestions = []
            for element in detected_elements:
                element_tests = []
                for test in test_data.get("test_scenarios", []):
                    if self._test_applies_to_element(test, element):
                        element_tests.append(test.get("description", ""))
                test_suggestions.append(element_tests[:3])  # Limit to 3 tests per element
            
            return test_suggestions
            
        except Exception as e:
            logger.error(f"Test suggestion generation failed: {e}")
            return [[] for _ in detected_elements]
    
    async def detect_accessibility_issues(
        self,
        screenshot: bytes,
        dom_elements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect accessibility issues using visual analysis"""
        logger.info("Performing visual accessibility analysis")
        
        accessibility_prompt = """
Analyze this screenshot for accessibility issues:

1. Color contrast problems
2. Text readability
3. Touch target sizes (mobile)
4. Visual hierarchy issues
5. Missing visual indicators (focus states, etc.)
6. Confusing layouts
7. Hidden or obscured content

Consider WCAG 2.1 guidelines. Provide specific recommendations.
"""
        
        base64_image = base64.b64encode(screenshot).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": accessibility_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ]
        
        try:
            response = await self._call_vision_model(messages)
            accessibility_data = self._parse_vision_response(response)
            
            return {
                "issues": accessibility_data.get("issues", []),
                "recommendations": accessibility_data.get("recommendations", []),
                "wcag_violations": accessibility_data.get("wcag_violations", []),
                "severity_scores": accessibility_data.get("severity_scores", {})
            }
            
        except Exception as e:
            logger.error(f"Accessibility analysis failed: {e}")
            return {"error": str(e)}
    
    async def _call_vision_model(self, messages: List[Dict[str, Any]]) -> str:
        """Call the vision model with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if self.model_type == "openai":
                    response = await self.llm_client.chat.completions.create(
                        model=self.vision_model,
                        messages=messages,
                        max_tokens=4096,
                        temperature=0.2
                    )
                    return response.choices[0].message.content
                    
                elif self.model_type == "anthropic":
                    response = await self.llm_client.messages.create(
                        model=self.vision_model,
                        messages=messages,
                        max_tokens=4096,
                        temperature=0.2
                    )
                    return response.content[0].text
                    
                else:
                    # Generic OpenAI-compatible API
                    response = await self.llm_client.chat.completions.create(
                        model=self.vision_model,
                        messages=messages,
                        max_tokens=4096
                    )
                    return response.choices[0].message.content
                    
            except Exception as e:
                logger.error(f"Vision model call failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def _parse_vision_response(self, response: str) -> Dict[str, Any]:
        """Parse the vision model response"""
        import json
        
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find JSON object in response
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Failed to parse vision response: {e}")
            # Return a basic structure
            return {
                "elements": [],
                "dynamic_regions": [],
                "layout_analysis": {}
            }
    
    def _create_element_summary(self, elements: List[VisualElement]) -> str:
        """Create a text summary of detected elements"""
        summary_lines = []
        
        for i, elem in enumerate(elements):
            summary_lines.append(
                f"{i+1}. {elem.element_type.value}: "
                f"{elem.text_content or 'No text'} "
                f"at ({elem.bounding_box[0]}, {elem.bounding_box[1]})"
            )
        
        return "\n".join(summary_lines)
    
    def _test_applies_to_element(self, test: Dict[str, Any], element: VisualElement) -> bool:
        """Check if a test scenario applies to a specific element"""
        test_keywords = test.get("keywords", [])
        element_keywords = [
            element.element_type.value,
            element.text_content or "",
            element.visual_description
        ]
        
        # Simple keyword matching
        for test_kw in test_keywords:
            for elem_kw in element_keywords:
                if test_kw.lower() in elem_kw.lower():
                    return True
        
        return False
    
    def merge_with_dom_elements(
        self,
        visual_elements: List[VisualElement],
        dom_elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge visual analysis with DOM elements for comprehensive data"""
        merged_elements = []
        
        # Create spatial index for efficient matching
        visual_by_region = {}
        for v_elem in visual_elements:
            key = (
                v_elem.bounding_box[0] // 50,  # Grid-based spatial hashing
                v_elem.bounding_box[1] // 50
            )
            if key not in visual_by_region:
                visual_by_region[key] = []
            visual_by_region[key].append(v_elem)
        
        # Match DOM elements with visual elements
        for dom_elem in dom_elements:
            bbox = dom_elem.get("bounding_box", {})
            if not bbox:
                continue
            
            # Find nearby visual elements
            grid_x = int(bbox.get("x", 0)) // 50
            grid_y = int(bbox.get("y", 0)) // 50
            
            matched_visual = None
            min_distance = float('inf')
            
            # Check neighboring grid cells
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    key = (grid_x + dx, grid_y + dy)
                    if key in visual_by_region:
                        for v_elem in visual_by_region[key]:
                            distance = self._calculate_bbox_distance(
                                (bbox["x"], bbox["y"], bbox["width"], bbox["height"]),
                                v_elem.bounding_box
                            )
                            if distance < min_distance:
                                min_distance = distance
                                matched_visual = v_elem
            
            # Merge data
            merged = dom_elem.copy()
            if matched_visual and min_distance < 50:  # Within 50 pixels
                merged["visual_analysis"] = {
                    "description": matched_visual.visual_description,
                    "interaction_hints": matched_visual.interaction_hints,
                    "accessibility_concerns": matched_visual.accessibility_concerns,
                    "test_suggestions": matched_visual.test_suggestions,
                    "confidence": matched_visual.confidence
                }
            
            merged_elements.append(merged)
        
        # Add visual-only elements (not found in DOM)
        for v_elem in visual_elements:
            if not any(self._is_visual_elem_matched(v_elem, merged_elements)):
                merged_elements.append({
                    "type": v_elem.element_type.value,
                    "bounding_box": {
                        "x": v_elem.bounding_box[0],
                        "y": v_elem.bounding_box[1],
                        "width": v_elem.bounding_box[2],
                        "height": v_elem.bounding_box[3]
                    },
                    "text": v_elem.text_content,
                    "detection_method": "visual_only",
                    "visual_analysis": {
                        "description": v_elem.visual_description,
                        "interaction_hints": v_elem.interaction_hints,
                        "accessibility_concerns": v_elem.accessibility_concerns,
                        "test_suggestions": v_elem.test_suggestions,
                        "confidence": v_elem.confidence
                    }
                })
        
        return merged_elements
    
    def _calculate_bbox_distance(self, bbox1: Tuple, bbox2: Tuple) -> float:
        """Calculate distance between two bounding boxes"""
        # Center points
        c1_x = bbox1[0] + bbox1[2] / 2
        c1_y = bbox1[1] + bbox1[3] / 2
        c2_x = bbox2[0] + bbox2[2] / 2
        c2_y = bbox2[1] + bbox2[3] / 2
        
        # Euclidean distance
        return ((c1_x - c2_x) ** 2 + (c1_y - c2_y) ** 2) ** 0.5
    
    def _is_visual_elem_matched(self, v_elem: VisualElement, merged_elements: List[Dict]) -> bool:
        """Check if a visual element has been matched with DOM elements"""
        for elem in merged_elements:
            if "visual_analysis" in elem:
                va = elem["visual_analysis"]
                if (va.get("description") == v_elem.visual_description and
                    va.get("confidence") == v_elem.confidence):
                    return True
        return False