"""
Output formatters for different use cases
Transform raw extraction data into optimized formats for specific purposes
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from ..core.models import Element, ElementType
import json


class OutputFormatter(ABC):
    """Base class for output formatters"""
    
    @abstractmethod
    def format(self, elements: List[Element], metadata: Dict[str, Any]) -> Any:
        """Format elements for specific use case"""
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """Return formatter name"""
        pass


class LLMTestGenerationFormatter(OutputFormatter):
    """
    Format output optimized for LLM test case generation.
    Creates a concise, structured representation that helps LLMs understand
    the UI context and generate meaningful test cases.
    """
    
    def get_format_name(self) -> str:
        return "llm_test_generation"
    
    def format(self, elements: List[Element], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for LLM consumption with:
        - Grouped by interaction type
        - Natural language descriptions
        - Test-relevant context
        """
        
        # Group elements by their test relevance
        forms = []
        inputs = []
        buttons = []
        links = []
        other_interactive = []
        
        for elem in elements:
            if not elem.is_interactive:
                continue
                
            # Create LLM-friendly element description
            elem_desc = self._create_element_description(elem)
            
            if elem.element_type == ElementType.FORM:
                forms.append(elem_desc)
            elif elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
                inputs.append(elem_desc)
            elif elem.element_type == ElementType.BUTTON:
                buttons.append(elem_desc)
            elif elem.element_type == ElementType.LINK:
                links.append(elem_desc)
            else:
                other_interactive.append(elem_desc)
        
        # Create test scenarios context
        test_context = self._generate_test_context(forms, inputs, buttons, links)
        
        return {
            "page_context": {
                "url": metadata.get("url", ""),
                "page_type": self._infer_page_type(metadata.get("url", ""), elements),
                "total_interactive_elements": len([e for e in elements if e.is_interactive]),
                "high_priority_elements": len([e for e in elements if e.interaction_score > 0.8])
            },
            "testable_elements": {
                "forms": {
                    "count": len(forms),
                    "elements": forms,
                    "test_hints": [
                        "Test form submission with valid data",
                        "Test validation with invalid data",
                        "Test required field handling"
                    ] if forms else []
                },
                "inputs": {
                    "count": len(inputs),
                    "elements": inputs,
                    "test_hints": [
                        "Test input validation rules",
                        "Test character limits",
                        "Test special characters handling"
                    ] if inputs else []
                },
                "buttons": {
                    "count": len(buttons),
                    "elements": buttons,
                    "test_hints": [
                        "Test button click actions",
                        "Test disabled state behavior",
                        "Test loading states"
                    ] if buttons else []
                },
                "links": {
                    "count": len(links),
                    "elements": links,
                    "test_hints": [
                        "Test navigation targets",
                        "Test external link handling",
                        "Test anchor links"
                    ] if links else []
                }
            },
            "suggested_test_scenarios": test_context,
            "llm_prompt_context": self._create_llm_prompt_context(elements)
        }
    
    def _create_element_description(self, elem: Element) -> Dict[str, Any]:
        """Create natural language description for LLM understanding"""
        
        description = f"{elem.tag_name.upper()}"
        
        # Add meaningful identifiers
        if elem.attributes.get("aria-label"):
            description = f'{elem.attributes["aria-label"]} {elem.tag_name}'
        elif elem.attributes.get("name"):
            description = f'{elem.attributes["name"]} field'
        elif elem.text and len(elem.text) < 50:
            description = f'{elem.tag_name} "{elem.text[:50]}"'
        
        return {
            "description": description,
            "selector": elem.selector,
            "attributes": {
                k: v for k, v in elem.attributes.items() 
                if k in ["id", "name", "type", "role", "aria-label", "href"]
            },
            "interaction_score": elem.interaction_score,
            "position": f"x:{elem.bounding_box['x']}, y:{elem.bounding_box['y']}" if elem.bounding_box else None
        }
    
    def _infer_page_type(self, url: str, elements: List[Element]) -> str:
        """Infer the type of page for better test generation"""
        
        # Check URL patterns
        if "login" in url.lower() or "signin" in url.lower():
            return "authentication"
        elif "search" in url.lower():
            return "search"
        elif "checkout" in url.lower() or "cart" in url.lower():
            return "e-commerce"
        elif "form" in url.lower() or "contact" in url.lower():
            return "form"
        
        # Check element patterns
        has_search = any(
            "search" in str(e.attributes.get("aria-label", "")).lower() or
            "search" in str(e.attributes.get("name", "")).lower()
            for e in elements
        )
        
        if has_search:
            return "search"
        
        form_count = len([e for e in elements if e.element_type == ElementType.FORM])
        if form_count > 0:
            return "form-based"
        
        return "general"
    
    def _generate_test_context(self, forms, inputs, buttons, links) -> List[str]:
        """Generate high-level test scenarios based on elements"""
        
        scenarios = []
        
        if inputs and buttons:
            scenarios.append("User input and submission flow")
        
        if len(inputs) > 3:
            scenarios.append("Complex form validation")
        
        if any("password" in str(inp.get("attributes", {}).get("type", "")).lower() for inp in inputs):
            scenarios.append("Authentication and security")
        
        if any("email" in str(inp.get("attributes", {}).get("type", "")).lower() for inp in inputs):
            scenarios.append("Email validation")
        
        if links:
            scenarios.append("Navigation and routing")
        
        return scenarios
    
    def _create_llm_prompt_context(self, elements: List[Element]) -> str:
        """Create a concise context string for LLM prompts"""
        
        interactive = [e for e in elements if e.is_interactive]
        
        context = f"Page with {len(interactive)} interactive elements. "
        
        # Add key element types
        types = {}
        for elem in interactive:
            types[elem.element_type.value] = types.get(elem.element_type.value, 0) + 1
        
        type_summary = ", ".join([f"{count} {type}s" for type, count in types.items()])
        context += f"Elements: {type_summary}. "
        
        # Add accessibility info
        aria_elements = [e for e in interactive if e.attributes.get("aria-label")]
        if aria_elements:
            context += f"{len(aria_elements)} elements have accessibility labels. "
        
        return context


class AccessibilityTestFormatter(OutputFormatter):
    """Format output optimized for accessibility testing"""
    
    def get_format_name(self) -> str:
        return "accessibility_testing"
    
    def format(self, elements: List[Element], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for accessibility testing with:
        - ARIA attributes highlighted
        - Missing accessibility features
        - Tab order analysis
        """
        
        aria_elements = []
        missing_aria = []
        form_elements = []
        
        for elem in elements:
            if elem.is_interactive:
                aria_info = {
                    "selector": elem.selector,
                    "tag": elem.tag_name,
                    "role": elem.attributes.get("role"),
                    "aria-label": elem.attributes.get("aria-label"),
                    "aria-describedby": elem.attributes.get("aria-describedby"),
                    "tab_index": elem.attributes.get("tabindex"),
                    "name": elem.attributes.get("name"),
                    "id": elem.attributes.get("id")
                }
                
                if elem.attributes.get("aria-label") or elem.attributes.get("role"):
                    aria_elements.append(aria_info)
                else:
                    missing_aria.append(aria_info)
                
                if elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA, ElementType.SELECT]:
                    form_elements.append(aria_info)
        
        return {
            "accessibility_summary": {
                "total_interactive": len([e for e in elements if e.is_interactive]),
                "with_aria": len(aria_elements),
                "missing_aria": len(missing_aria),
                "form_elements": len(form_elements)
            },
            "elements_with_aria": aria_elements,
            "elements_missing_aria": missing_aria,
            "form_accessibility": form_elements,
            "recommendations": self._generate_recommendations(missing_aria, form_elements)
        }
    
    def _generate_recommendations(self, missing_aria, form_elements) -> List[str]:
        """Generate accessibility recommendations"""
        recs = []
        
        if missing_aria:
            recs.append(f"Add ARIA labels to {len(missing_aria)} interactive elements")
        
        form_without_labels = [f for f in form_elements if not f.get("aria-label") and not f.get("name")]
        if form_without_labels:
            recs.append(f"Add labels to {len(form_without_labels)} form elements")
        
        return recs


class VisualTestingFormatter(OutputFormatter):
    """Format output optimized for visual regression testing"""
    
    def get_format_name(self) -> str:
        return "visual_testing"
    
    def format(self, elements: List[Element], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for visual testing with:
        - Bounding box regions
        - Visual hierarchy
        - Screenshot regions
        """
        
        regions = []
        
        for elem in elements:
            if elem.bounding_box and elem.is_visible:
                region = {
                    "selector": elem.selector,
                    "type": elem.element_type.value,
                    "region": {
                        "x": elem.bounding_box["x"],
                        "y": elem.bounding_box["y"],
                        "width": elem.bounding_box["width"],
                        "height": elem.bounding_box["height"]
                    },
                    "area": elem.bounding_box["width"] * elem.bounding_box["height"],
                    "center": {
                        "x": elem.bounding_box["x"] + elem.bounding_box["width"] / 2,
                        "y": elem.bounding_box["y"] + elem.bounding_box["height"] / 2
                    }
                }
                regions.append(region)
        
        # Sort by area (largest first) for visual importance
        regions.sort(key=lambda r: r["area"], reverse=True)
        
        return {
            "visual_regions": regions[:20],  # Top 20 largest elements
            "viewport_coverage": self._calculate_coverage(regions),
            "visual_hierarchy": self._analyze_hierarchy(regions),
            "screenshot_regions": self._define_screenshot_regions(regions)
        }
    
    def _calculate_coverage(self, regions) -> Dict[str, Any]:
        """Calculate viewport coverage statistics"""
        if not regions:
            return {"total_area": 0, "coverage_percent": 0}
        
        total_area = sum(r["area"] for r in regions)
        viewport_area = 1920 * 1080  # Standard viewport
        
        return {
            "total_area": total_area,
            "viewport_area": viewport_area,
            "coverage_percent": (total_area / viewport_area) * 100
        }
    
    def _analyze_hierarchy(self, regions) -> List[str]:
        """Analyze visual hierarchy"""
        hierarchy = []
        
        if regions:
            hierarchy.append(f"Largest element: {regions[0]['selector']} ({regions[0]['area']}px²)")
            
            # Find top-most element
            top_element = min(regions, key=lambda r: r["region"]["y"])
            hierarchy.append(f"Top element: {top_element['selector']} at y={top_element['region']['y']}")
        
        return hierarchy
    
    def _define_screenshot_regions(self, regions) -> List[Dict]:
        """Define key regions for screenshot comparison"""
        screenshot_regions = []
        
        # Header region (top 200px)
        screenshot_regions.append({
            "name": "header",
            "region": {"x": 0, "y": 0, "width": 1920, "height": 200}
        })
        
        # Main content (middle section)
        screenshot_regions.append({
            "name": "main_content",
            "region": {"x": 0, "y": 200, "width": 1920, "height": 680}
        })
        
        # Footer region (bottom 200px)
        screenshot_regions.append({
            "name": "footer",
            "region": {"x": 0, "y": 880, "width": 1920, "height": 200}
        })
        
        return screenshot_regions


class APITestingFormatter(OutputFormatter):
    """Format output optimized for API testing"""
    
    def get_format_name(self) -> str:
        return "api_testing"
    
    def format(self, elements: List[Element], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for API testing with:
        - Form endpoints
        - Input field mappings
        - Validation rules inference
        """
        
        forms = []
        api_endpoints = []
        
        for elem in elements:
            if elem.element_type == ElementType.FORM:
                form_data = {
                    "selector": elem.selector,
                    "action": elem.attributes.get("action", ""),
                    "method": elem.attributes.get("method", "GET").upper(),
                    "fields": []
                }
                forms.append(form_data)
            
            # Extract potential API endpoints from links
            if elem.element_type == ElementType.LINK and elem.attributes.get("href"):
                href = elem.attributes["href"]
                if "/api/" in href or href.endswith(".json"):
                    api_endpoints.append({
                        "url": href,
                        "selector": elem.selector,
                        "text": elem.text[:50] if elem.text else None
                    })
        
        # Map form fields
        input_fields = []
        for elem in elements:
            if elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA, ElementType.SELECT]:
                field_info = {
                    "name": elem.attributes.get("name", ""),
                    "type": elem.attributes.get("type", "text"),
                    "required": elem.attributes.get("required", False),
                    "validation": self._infer_validation(elem)
                }
                input_fields.append(field_info)
        
        return {
            "forms": forms,
            "input_fields": input_fields,
            "potential_api_endpoints": api_endpoints,
            "test_data_requirements": self._generate_test_data_requirements(input_fields)
        }
    
    def _infer_validation(self, elem: Element) -> Dict[str, Any]:
        """Infer validation rules from element attributes"""
        validation = {}
        
        if elem.attributes.get("pattern"):
            validation["pattern"] = elem.attributes["pattern"]
        if elem.attributes.get("minlength"):
            validation["minlength"] = elem.attributes["minlength"]
        if elem.attributes.get("maxlength"):
            validation["maxlength"] = elem.attributes["maxlength"]
        if elem.attributes.get("type") == "email":
            validation["format"] = "email"
        if elem.attributes.get("type") == "number":
            validation["format"] = "number"
        
        return validation
    
    def _generate_test_data_requirements(self, fields) -> List[str]:
        """Generate test data requirements based on fields"""
        requirements = []
        
        for field in fields:
            if field["type"] == "email":
                requirements.append("Valid and invalid email addresses")
            elif field["type"] == "password":
                requirements.append("Strong and weak passwords")
            elif field["type"] == "number":
                requirements.append("Numeric ranges and boundaries")
            elif field.get("validation", {}).get("pattern"):
                requirements.append(f"Data matching pattern: {field['validation']['pattern']}")
        
        return list(set(requirements))


# Registry of available formatters
FORMATTERS = {
    "llm_test": LLMTestGenerationFormatter(),
    "accessibility": AccessibilityTestFormatter(),
    "visual": VisualTestingFormatter(),
    "api": APITestingFormatter()
}


def format_output(elements: List[Element], format_type: str, metadata: Optional[Dict] = None) -> Any:
    """
    Format extraction output for specific use case
    
    Args:
        elements: List of extracted elements
        format_type: Type of formatting ('llm_test', 'accessibility', 'visual', 'api')
        metadata: Additional metadata about the extraction
    
    Returns:
        Formatted output for the specific use case
    """
    
    if format_type not in FORMATTERS:
        raise ValueError(f"Unknown format type: {format_type}. Available: {list(FORMATTERS.keys())}")
    
    formatter = FORMATTERS[format_type]
    return formatter.format(elements, metadata or {})