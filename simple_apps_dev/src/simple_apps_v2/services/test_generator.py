"""
Test generation service.
"""

from typing import Dict, Any, List, Optional

from simple_apps_v2.core.logging import get_logger

logger = get_logger(__name__)


class TestGenerator:
    """Service for generating test scenarios."""
    
    def __init__(self, framework: str = "pytest"):
        """Initialize test generator."""
        self.framework = framework
    
    async def generate_tests(
        self,
        extraction_data: Dict[str, Any],
        categories: Optional[List[str]] = None,
        include_edge_cases: bool = True,
        max_per_category: int = 10
    ) -> Dict[str, Any]:
        """Generate test scenarios from extracted elements."""
        logger.info(f"Generating {self.framework} tests")
        
        # Extract elements
        elements = extraction_data.get("elements", [])
        elements_by_category = extraction_data.get("elements_by_category", {})
        
        # Generate test scenarios
        scenarios = []
        features = {}
        
        # Generate tests for each category
        for category, category_elements in elements_by_category.items():
            if categories and category not in categories:
                continue
            
            feature_name = f"{category.replace('_', ' ').title()} Tests"
            features[feature_name] = []
            
            # Generate scenarios for this category
            for idx, element in enumerate(category_elements[:max_per_category]):
                scenario = self._generate_scenario(element, category, idx)
                scenarios.append(scenario)
                features[feature_name].append(scenario["name"])
        
        # Add edge cases if requested
        if include_edge_cases:
            edge_scenarios = self._generate_edge_cases(extraction_data)
            scenarios.extend(edge_scenarios)
            features["Edge Cases"] = [s["name"] for s in edge_scenarios]
        
        return {
            "scenarios": scenarios,
            "features": features,
            "framework": self.framework,
            "url": extraction_data.get("url", ""),
        }
    
    def _generate_scenario(
        self, 
        element: Dict[str, Any], 
        category: str, 
        index: int
    ) -> Dict[str, Any]:
        """Generate a single test scenario."""
        scenario = {
            "name": f"Test {category} element {index + 1}",
            "category": category,
            "element": element,
            "steps": [],
            "expected": [],
        }
        
        # Generate steps based on element type
        if category == "button":
            scenario["steps"] = [
                f"Navigate to page",
                f"Find button with text '{element.get('text', 'Button')}'",
                f"Click the button",
            ]
            scenario["expected"] = [
                "Button is visible",
                "Button is clickable",
                "Action is performed",
            ]
        elif category == "form_input":
            scenario["steps"] = [
                f"Navigate to page",
                f"Find input field '{element.get('name', 'input')}'",
                f"Enter test data",
                f"Verify input accepted",
            ]
            scenario["expected"] = [
                "Input field is visible",
                "Can enter text",
                "Value is retained",
            ]
        elif category == "link":
            scenario["steps"] = [
                f"Navigate to page",
                f"Find link with text '{element.get('text', 'Link')}'",
                f"Click the link",
            ]
            scenario["expected"] = [
                "Link is visible",
                "Link has valid href",
                "Navigation occurs",
            ]
        else:
            scenario["steps"] = [
                f"Navigate to page",
                f"Find {category} element",
                f"Verify element properties",
            ]
            scenario["expected"] = [
                "Element is present",
                "Element has correct attributes",
            ]
        
        return scenario
    
    def _generate_edge_cases(self, extraction_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge case test scenarios."""
        edge_cases = []
        
        # Page load edge case
        edge_cases.append({
            "name": "Test page loads within timeout",
            "category": "edge_case",
            "steps": [
                "Navigate to page with timeout",
                "Wait for page to load",
                "Verify page loaded",
            ],
            "expected": [
                "Page loads within 30 seconds",
                "No timeout errors",
            ]
        })
        
        # Responsive design edge case
        edge_cases.append({
            "name": "Test responsive design",
            "category": "edge_case",
            "steps": [
                "Navigate to page",
                "Resize viewport to mobile",
                "Verify layout adapts",
                "Resize viewport to tablet",
                "Verify layout adapts",
            ],
            "expected": [
                "Layout is responsive",
                "Elements remain accessible",
            ]
        })
        
        # Error handling edge case
        edge_cases.append({
            "name": "Test error handling",
            "category": "edge_case",
            "steps": [
                "Navigate to page",
                "Submit form with invalid data",
                "Verify error messages",
            ],
            "expected": [
                "Appropriate error messages shown",
                "Form does not submit invalid data",
            ]
        })
        
        return edge_cases