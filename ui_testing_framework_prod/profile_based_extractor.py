#!/usr/bin/env python3
"""
Profile-Based Element Extractor
Main interface for extraction with profile support

INPUTS:
- URL or file path to extract from
- Profile name (qa, accessibility, performance, general)
- Optional configuration overrides

OUTPUTS:
- Extraction results saved to: extraction_results/{profile_name}/{timestamp}_{url_hash}.json
- Latest results always available at: extraction_results/{profile_name}/latest.json
- Full state persistence - no execution data is ever lost

Architecture:
- Wraps elements_extractor_no_llm.py with profile capabilities
- Uses Registry + Strategy patterns for extensibility
- Maintains backward compatibility
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse

from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractionConfig,
    ExtractionResult,
    ExtractedElement
)
from extraction_profiles import (
    ProfileRegistry,
    ExtractionProfile,
    ProfileConfig,
    get_profile,
    list_available_profiles
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfileBasedExtractor:
    """
    Main extractor class with profile support
    Coordinates between the base extractor and profile system
    """
    
    def __init__(self, profile_name: str = "general", 
                 config_overrides: Optional[Dict[str, Any]] = None,
                 module_name: str = "elements_extractor_no_llm"):
        """
        Initialize extractor with specified profile
        
        Args:
            profile_name: Name of the extraction profile to use
            config_overrides: Optional config overrides for the profile
            module_name: Name of the module (for organizing results)
        """
        # Get the profile with module name
        self.module_name = module_name
        self.profile = get_profile(profile_name, module_name)
        logger.info(f"Initialized with profile: {profile_name} for module: {module_name}")
        
        # Apply config overrides if provided
        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(self.profile.config, key):
                    setattr(self.profile.config, key, value)
        
        # Create base extractor config from profile
        self.extractor_config = self._create_extractor_config()
        self.extractor = ElementsExtractorNoLLM(self.extractor_config)
        
        # Setup results directory
        self._setup_results_directory()
    
    def _create_extractor_config(self) -> ExtractionConfig:
        """Create base extractor config from profile settings"""
        profile_config = self.profile.config
        
        # Map profile config to extractor config
        config = ExtractionConfig(
            element_limit=profile_config.element_limit,
            timeout=profile_config.timeout,
            filter_invisible=profile_config.filter_invisible,
            filter_duplicates=profile_config.filter_duplicates,
            min_element_size=profile_config.min_element_size,
            capture_screenshots=profile_config.save_screenshots,
            capture_html=profile_config.save_html
        )
        
        # Apply QA-specific settings if this is QA profile
        if self.profile._name == "qa":
            config.qa_mode = True
            config.qa_min_interaction_score = profile_config.custom_settings.get("min_interaction_score", 0.7)
            config.qa_include_disabled = profile_config.custom_settings.get("include_disabled", True)
        
        return config
    
    def _setup_results_directory(self):
        """Ensure results directory exists relative to script location"""
        # Get the directory where this script is located
        script_dir = Path(__file__).parent.resolve()
        base_dir = script_dir / "extraction_results" / self.module_name
        base_dir.mkdir(parents=True, exist_ok=True)
        
        profile_dir = base_dir / self.profile._name
        profile_dir.mkdir(exist_ok=True)
        
        # Create metadata file for the profile
        metadata_file = profile_dir / "profile_metadata.json"
        metadata = {
            "profile_name": self.profile._name,
            "profile_description": self.profile._description,
            "profile_version": self.profile.config.version,
            "created_at": datetime.now().isoformat(),
            "config": self.profile.config.model_dump()
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    async def extract(self, 
                     source: str,
                     source_type: str = "url") -> Dict[str, Any]:
        """
        Main extraction method
        
        Args:
            source: URL or file path to extract from
            source_type: Either "url" or "file"
        
        Returns:
            Dictionary containing extraction results and metadata
        """
        logger.info(f"Starting extraction from {source_type}: {source}")
        logger.info(f"Using profile: {self.profile._name}")
        
        try:
            # Perform extraction based on source type
            if source_type == "url":
                result = await self.extractor.extract_from_url(source)
            elif source_type == "file":
                with open(source, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                result = await self.extractor.extract_from_html(html_content, source)
            else:
                raise ValueError(f"Invalid source_type: {source_type}")
            
            # Convert ExtractedElement objects to dictionaries
            elements_data = self._convert_elements_to_dict(result.elements)
            
            # Apply profile filtering
            filtered_elements = self.profile.filter_elements(elements_data)
            logger.info(f"Filtered from {len(elements_data)} to {len(filtered_elements)} elements")
            
            # Categorize elements
            categories = self.profile.categorize_elements(filtered_elements)
            
            # Generate insights
            insights = self.profile.generate_insights(filtered_elements)
            
            # Prepare full results
            extraction_results = {
                "success": result.success,
                "source": source,
                "source_type": source_type,
                "profile": self.profile._name,
                "timestamp": datetime.now().isoformat(),
                "extraction_time": result.extraction_time,
                "statistics": {
                    "total_extracted": len(elements_data),
                    "after_filtering": len(filtered_elements),
                    "categories": {cat: len(elems) for cat, elems in categories.items()}
                },
                "insights": insights,
                "elements": {
                    "all": elements_data,
                    "filtered": filtered_elements,
                    "categorized": categories
                },
                "metadata": {
                    "page_url": result.url,
                    "extraction_config": self.extractor_config.model_dump() if hasattr(self.extractor_config, 'model_dump') else {},
                    "result_metadata": result.metadata if hasattr(result, 'metadata') else {}
                },
                "errors": result.errors if hasattr(result, 'errors') else []
            }
            
            # Save results with full state persistence
            saved_path = self.profile.save_results(
                url=source,
                elements=filtered_elements,
                metadata=extraction_results
            )
            
            logger.info(f"Results saved to: {saved_path}")
            
            # Also save a comprehensive report
            self._save_comprehensive_report(extraction_results)
            
            return extraction_results
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            
            # Even on failure, save what we have
            error_results = {
                "success": False,
                "source": source,
                "source_type": source_type,
                "profile": self.profile._name,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "elements": []
            }
            
            # Save error state
            self.profile.save_results(
                url=source,
                elements=[],
                metadata=error_results
            )
            
            raise
        
        finally:
            # Always close the browser
            if hasattr(self.extractor, 'browser') and self.extractor.browser:
                await self.extractor.browser.close()
    
    def _convert_elements_to_dict(self, elements: List[ExtractedElement]) -> List[Dict[str, Any]]:
        """Convert ExtractedElement objects to dictionaries"""
        elements_data = []
        
        for element in elements:
            # Convert element to dict
            elem_dict = {
                "tag_name": element.tag_name,
                "element_type": element.element_type.value if hasattr(element.element_type, 'value') else str(element.element_type),
                "selector": element.selector,
                "xpath": element.xpath,
                "text": element.text,
                "attributes": element.attributes if element.attributes else {},
                "is_clickable": element.is_clickable if hasattr(element, 'is_clickable') else False,
                "is_editable": element.is_editable if hasattr(element, 'is_editable') else False,
                "confidence": element.confidence if hasattr(element, 'confidence') else 0.0
            }
            
            # Add computed style if available
            if hasattr(element, 'computed_style') and element.computed_style:
                elem_dict['computed_style'] = element.computed_style.model_dump() if hasattr(element.computed_style, 'model_dump') else {}
            
            # Add bounding box if available
            if hasattr(element, 'bounding_box') and element.bounding_box:
                elem_dict['bounding_box'] = element.bounding_box.model_dump() if hasattr(element.bounding_box, 'model_dump') else {}
            
            # Add interaction types if available
            if hasattr(element, 'interaction_types') and element.interaction_types:
                elem_dict['interaction_types'] = [i.value if hasattr(i, 'value') else str(i) for i in element.interaction_types]
            
            elements_data.append(elem_dict)
        
        return elements_data
    
    def _save_comprehensive_report(self, results: Dict[str, Any]):
        """Save a human-readable comprehensive report"""
        # Get the directory where this script is located
        script_dir = Path(__file__).parent.resolve()
        report_dir = script_dir / "extraction_results" / self.module_name / self.profile._name / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"report_{timestamp}.md"
        
        # Generate markdown report
        report = f"""# Extraction Report - {self.profile._name.upper()} Profile

## Summary
- **Source**: {results['source']}
- **Timestamp**: {results['timestamp']}
- **Profile**: {self.profile._name} - {self.profile._description}
- **Success**: {results['success']}
- **Extraction Time**: {results.get('extraction_time', 0):.2f} seconds

## Statistics
- **Total Elements Extracted**: {results['statistics']['total_extracted']}
- **After Profile Filtering**: {results['statistics']['after_filtering']}

## Element Categories
"""
        
        for category, count in results['statistics']['categories'].items():
            report += f"- **{category}**: {count} elements\n"
        
        report += "\n## Insights\n"
        report += f"```json\n{json.dumps(results['insights'], indent=2)}\n```\n"
        
        report += "\n## Sample Elements\n"
        filtered = results['elements']['filtered'][:5]
        for i, elem in enumerate(filtered, 1):
            report += f"\n### Element {i}\n"
            report += f"- **Tag**: {elem.get('tag_name', 'N/A')}\n"
            report += f"- **Type**: {elem.get('element_type', 'N/A')}\n"
            if elem.get('text'):
                report += f"- **Text**: {elem['text'][:100]}...\n"
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Report saved to: {report_file}")
    
    async def close(self):
        """Clean up resources"""
        if hasattr(self.extractor, 'browser') and self.extractor.browser:
            await self.extractor.browser.close()
    
    def get_results_history(self) -> List[Dict[str, Any]]:
        """Get history of all extraction results for current profile"""
        return self.profile.get_results_history()
    
    def get_latest_results(self) -> Dict[str, Any]:
        """Get the latest extraction results"""
        return self.profile.load_results()


# ==================== CONVENIENCE FUNCTIONS ====================

async def extract_with_profile(
    source: str,
    profile_name: str = "general",
    source_type: str = "url",
    config_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for one-shot extraction
    
    Args:
        source: URL or file path
        profile_name: Name of profile to use
        source_type: "url" or "file"
        config_overrides: Optional config overrides
    
    Returns:
        Extraction results dictionary
    """
    extractor = ProfileBasedExtractor(profile_name, config_overrides)
    try:
        return await extractor.extract(source, source_type)
    finally:
        await extractor.close()


def show_available_profiles():
    """Display all available extraction profiles"""
    print("\n" + "="*60)
    print("AVAILABLE EXTRACTION PROFILES")
    print("="*60)
    
    profiles = list_available_profiles()
    for name, description in profiles.items():
        print(f"\n[{name.upper()}]")
        print(f"  {description}")
        
        # Show profile config
        profile = get_profile(name)
        config = profile.config
        print(f"  - Element limit: {config.element_limit}")
        print(f"  - Timeout: {config.timeout}s")
        print(f"  - Filter invisible: {config.filter_invisible}")
        
        if config.custom_settings:
            print(f"  - Custom settings: {list(config.custom_settings.keys())}")


# ==================== COMMAND LINE INTERFACE ====================

async def main():
    """Command line interface for profile-based extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Profile-Based Web Element Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract with QA profile
  python profile_based_extractor.py --url https://example.com --profile qa
  
  # Extract from file with accessibility profile
  python profile_based_extractor.py --file page.html --profile accessibility
  
  # List available profiles
  python profile_based_extractor.py --list-profiles
  
  # View extraction history
  python profile_based_extractor.py --history --profile qa
        """
    )
    
    parser.add_argument("--url", help="URL to extract from")
    parser.add_argument("--file", help="HTML file to extract from")
    parser.add_argument("--profile", default="general", help="Extraction profile to use")
    parser.add_argument("--list-profiles", action="store_true", help="List available profiles")
    parser.add_argument("--history", action="store_true", help="Show extraction history for profile")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle list profiles
    if args.list_profiles:
        show_available_profiles()
        return
    
    # Handle history
    if args.history:
        extractor = ProfileBasedExtractor(args.profile)
        history = extractor.get_results_history()
        
        print(f"\n{'='*60}")
        print(f"EXTRACTION HISTORY - {args.profile.upper()} PROFILE")
        print('='*60)
        
        if not history:
            print("No extraction history found")
        else:
            for entry in history[-10:]:  # Show last 10
                print(f"\n{entry['timestamp']}")
                print(f"  URL: {entry['url']}")
                print(f"  Elements: {entry['element_count']}")
                print(f"  File: {entry['filepath']}")
        
        return
    
    # Perform extraction
    if args.url:
        source = args.url
        source_type = "url"
    elif args.file:
        source = args.file
        source_type = "file"
    else:
        parser.error("Either --url or --file must be specified")
    
    print(f"\n{'='*60}")
    print(f"PROFILE-BASED EXTRACTION")
    print(f"{'='*60}")
    print(f"Source: {source}")
    print(f"Profile: {args.profile}")
    print(f"Starting extraction...")
    
    try:
        results = await extract_with_profile(
            source=source,
            profile_name=args.profile,
            source_type=source_type
        )
        
        print(f"\n{'='*60}")
        print("EXTRACTION COMPLETE")
        print('='*60)
        print(f"Success: {results['success']}")
        print(f"Total elements: {results['statistics']['total_extracted']}")
        print(f"After filtering: {results['statistics']['after_filtering']}")
        print(f"Extraction time: {results.get('extraction_time', 0):.2f}s")
        
        print("\nElement Categories:")
        for cat, count in results['statistics']['categories'].items():
            print(f"  - {cat}: {count}")
        
        print("\nResults saved to:")
        script_dir = Path(__file__).parent.resolve()
        results_path = script_dir / "extraction_results" / "elements_extractor_no_llm" / args.profile / "latest.json"
        print(f"  {results_path}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Run the CLI
    import sys
    sys.exit(asyncio.run(main()))