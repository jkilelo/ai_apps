"""
Result Converter Module
Converts crawler results to standardized format
"""

from typing import Dict, Any, List
from datetime import datetime


class ResultConverter:
    """Converts raw crawler results to standardized format"""
    
    def __init__(self, profile_config: Any):
        self.profile_config = profile_config
    
    def convert(self, raw_results: Any) -> Dict[str, Any]:
        """
        Convert raw crawler results to standardized format
        
        Args:
            raw_results: Raw results from crawler
            
        Returns:
            Standardized dictionary format
        """
        # Check if raw_results is a CrawlResult object
        if hasattr(raw_results, 'url') and hasattr(raw_results, 'elements'):
            # Handle single CrawlResult object
            converted = {
                "metadata": {
                    "crawl_time": datetime.now().isoformat(),
                    "profile_used": self.profile_config.profile_name if hasattr(self.profile_config, 'profile_name') else "unknown",
                    "total_pages": 1,
                    "total_elements": len(raw_results.elements) if hasattr(raw_results, 'elements') else 0
                },
                "results": {
                    raw_results.url: {
                        "title": raw_results.title if hasattr(raw_results, 'title') else "",
                        "elements": self._convert_elements(raw_results.elements if hasattr(raw_results, 'elements') else []),
                        "metrics": raw_results.metadata if hasattr(raw_results, 'metadata') else {},
                        "screenshots": {}
                    }
                }
            }
        else:
            # Handle dictionary format
            converted = {
                "metadata": {
                    "crawl_time": datetime.now().isoformat(),
                    "profile_used": self.profile_config.profile_name if hasattr(self.profile_config, 'profile_name') else "unknown",
                    "total_pages": len(raw_results.get("pages", [])),
                    "total_elements": sum(len(page.get("elements", [])) for page in raw_results.get("pages", []))
                },
                "results": {}
            }
            
            # Convert pages
            for page in raw_results.get("pages", []):
                page_url = page.get("url", "unknown")
                converted["results"][page_url] = {
                    "title": page.get("title", ""),
                    "elements": self._convert_elements(page.get("elements", [])),
                    "metrics": page.get("metrics", {}),
                    "screenshots": page.get("screenshots", {})
                }
        
        return converted
    
    def _convert_elements(self, elements: List[Any]) -> List[Dict[str, Any]]:
        """Convert element data to standardized format"""
        converted_elements = []
        
        for elem in elements:
            # Handle ElementData objects or dictionaries
            if hasattr(elem, 'element_type'):
                # It's an ElementData object - use the correct attributes
                converted_elem = {
                    "type": elem.element_type.value if hasattr(elem.element_type, 'value') else str(elem.element_type),
                    "tag": elem.tag_name,
                    "text": elem.text_content,
                    "href": elem.attributes.get('href') if elem.attributes else None,
                    "selector": elem.locators[0].value if elem.locators else "",
                    "xpath": next((loc.value for loc in elem.locators if loc.strategy.value == "xpath"), ""),
                    "attributes": elem.attributes,
                    "is_visible": elem.visual_properties.get('is_visible', True) if elem.visual_properties else True,
                    "is_interactive": elem.element_type.value in ['button', 'link', 'input', 'select', 'checkbox', 'radio', 'toggle'],
                    "bounds": elem.visual_properties.get('bounding_box', {}) if elem.visual_properties else {},
                    "screenshot": None
                }
            else:
                # It's a dictionary
                converted_elem = {
                    "type": elem.get("type", "unknown"),
                    "tag": elem.get("tag", ""),
                    "text": elem.get("text", ""),
                    "href": elem.get("href"),
                    "selector": elem.get("selector", ""),
                    "xpath": elem.get("xpath", ""),
                    "attributes": elem.get("attributes", {}),
                    "is_visible": elem.get("is_visible", True),
                    "is_interactive": elem.get("is_interactive", False),
                    "bounds": elem.get("bounds", {}),
                    "screenshot": elem.get("screenshot")
                }
            converted_elements.append(converted_elem)
        
        return converted_elements
    
    def convert_for_profile(self, raw_results: Dict[str, Any], profile_type: str) -> Dict[str, Any]:
        """Convert results for a specific profile type"""
        # First do the standard conversion
        converted = self.convert(raw_results)
        
        # Add profile-specific metadata
        converted["metadata"]["profile_type"] = profile_type
        
        return converted
    
    def save_to_file(self, data: Dict[str, Any], filename: str, format: str = "json"):
        """Save results to a file"""
        import json
        
        if format == "json":
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")