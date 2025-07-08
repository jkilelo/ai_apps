"""
Profile-based Web Crawler Entry Point

This module provides the main entry point for running the web crawler
with different user profiles and returning standardized dictionary results.
"""

import asyncio
import argparse
import json
from typing import Dict, Any, Optional, List
# from pathlib import Path  # Removed unused import
from playwright.async_api import async_playwright

from .crawler import AdvancedWebCrawler
from .profiles import ProfileManager, ProfileType, convert_profile_to_crawler_config
from .result_converter import ResultConverter


class ProfileCrawler:
    """Main profile-based crawler interface"""
    
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.result_converter = None
    
    async def crawl_with_profile(
        self,
        url: str,
        profile_type: str,
        max_depth: Optional[int] = None,
        max_pages: Optional[int] = None,
        save_results: bool = False,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crawl a website using a specific profile
        
        Args:
            url: URL to crawl
            profile_type: Profile type to use
            max_depth: Override max depth from profile
            max_pages: Override max pages from profile  
            save_results: Whether to save results to file
            output_file: Optional output file path
            
        Returns:
            Dictionary containing crawl results
        """
        
        # Get profile configuration
        profile_config = self.profile_manager.get_profile(profile_type)
        if not profile_config:
            raise ValueError(f"Profile '{profile_type}' not found. Available profiles: {self.profile_manager.list_profiles()}")
        
        # Override profile settings if provided
        if max_depth is not None:
            profile_config.max_depth = max_depth
        if max_pages is not None:
            profile_config.max_pages = max_pages
        
        # Convert profile to crawler configuration
        crawler_config = convert_profile_to_crawler_config(profile_config)
        
        # Initialize result converter with profile config
        self.result_converter = ResultConverter(profile_config)
        
        # Run the crawler
        async with async_playwright() as playwright:
            crawler = AdvancedWebCrawler(crawler_config)
            await crawler.initialize(playwright)
            
            try:
                # Perform the crawl
                crawl_result = await crawler.crawl_website(
                    url=url,
                    max_depth=profile_config.max_depth,
                    max_pages=profile_config.max_pages
                )
                
                # Convert to standardized dictionary format
                result_dict = self.result_converter.convert_for_profile(
                    crawl_result, 
                    profile_type
                )
                
                # Save results if requested
                if save_results:
                    if not output_file:
                        timestamp = crawl_result.metadata.get("crawl_timestamp", "").replace(":", "-")
                        output_file = f"{profile_type}_{timestamp}_results.json"
                    
                    self.result_converter.save_to_file(result_dict, output_file, "json")
                    result_dict["output_file"] = output_file
                
                return result_dict
                
            finally:
                await crawler.cleanup()
    
    def list_available_profiles(self) -> Dict[str, str]:
        """List all available profiles with descriptions"""
        profiles = {}
        for profile_type in self.profile_manager.list_profiles():
            profiles[profile_type] = self.profile_manager.get_profile_description(profile_type)
        return profiles
    
    def get_profile_info(self, profile_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific profile"""
        return self.profile_manager.get_profile_config_dict(profile_type)
    
    async def quick_scan(self, url: str, profile_type: str = "qa_manual_tester") -> Dict[str, Any]:
        """Quick scan with minimal depth for fast results"""
        return await self.crawl_with_profile(
            url=url,
            profile_type=profile_type,
            max_depth=1,
            max_pages=1
        )
    
    async def deep_analysis(self, url: str, profile_type: str) -> Dict[str, Any]:
        """Deep analysis with maximum depth for comprehensive results"""
        profile_config = self.profile_manager.get_profile(profile_type)
        if not profile_config:
            raise ValueError(f"Profile '{profile_type}' not found")
        
        return await self.crawl_with_profile(
            url=url,
            profile_type=profile_type,
            max_depth=min(profile_config.max_depth + 1, 5),  # Increase depth but cap at 5
            max_pages=min(profile_config.max_pages + 10, 50)  # Increase pages but cap at 50
        )
    
    async def compare_profiles(self, url: str, profile_types: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare results across multiple profiles"""
        results = {}
        
        for profile_type in profile_types:
            try:
                result = await self.quick_scan(url, profile_type)
                results[profile_type] = result
            except Exception as e:
                results[profile_type] = {"error": str(e)}
        
        return results
    
    def create_custom_profile(
        self,
        profile_name: str,
        base_profile: str,
        customizations: Dict[str, Any]
    ) -> str:
        """Create a custom profile based on an existing profile"""
        base_config = self.profile_manager.get_profile(base_profile)
        if not base_config:
            raise ValueError(f"Base profile '{base_profile}' not found")
        
        # Apply customizations
        for key, value in customizations.items():
            if hasattr(base_config, key):
                setattr(base_config, key, value)
        
        base_config.profile_name = profile_name
        custom_profile_id = self.profile_manager.create_custom_profile(base_config)
        
        return custom_profile_id


# CLI Interface
async def main():
    """Command line interface for profile crawler"""
    parser = argparse.ArgumentParser(description="Profile-based Web Crawler")
    parser.add_argument("url", nargs='?', help="URL to crawl")
    parser.add_argument("profile", nargs='?', help="Profile type to use")
    parser.add_argument("--max-depth", type=int, help="Maximum crawl depth")
    parser.add_argument("--max-pages", type=int, help="Maximum pages to crawl")
    parser.add_argument("--save", action="store_true", help="Save results to file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--list-profiles", action="store_true", help="List available profiles")
    parser.add_argument("--profile-info", help="Get info about a specific profile")
    parser.add_argument("--quick", action="store_true", help="Quick scan (depth=1, pages=1)")
    parser.add_argument("--deep", action="store_true", help="Deep analysis with extended limits")
    
    args = parser.parse_args()
    
    crawler = ProfileCrawler()
    
    # Handle list profiles command
    if args.list_profiles:
        profiles = crawler.list_available_profiles()
        print("Available Profiles:")
        print("=" * 50)
        for profile_type, description in profiles.items():
            print(f"{profile_type}: {description}")
        return
    
    # Handle profile info command
    if args.profile_info:
        info = crawler.get_profile_info(args.profile_info)
        if info:
            print(f"Profile Information for '{args.profile_info}':")
            print("=" * 50)
            print(json.dumps(info, indent=2))
        else:
            print(f"Profile '{args.profile_info}' not found")
        return
    
    # Check if required arguments are provided for crawling
    if not args.url or not args.profile:
        if not args.list_profiles and not args.profile_info:
            parser.error("URL and profile are required unless using --list-profiles or --profile-info")
        return
    
    try:
        # Perform crawling based on options
        if args.quick:
            result = await crawler.quick_scan(args.url, args.profile)
        elif args.deep:
            result = await crawler.deep_analysis(args.url, args.profile)
        else:
            result = await crawler.crawl_with_profile(
                url=args.url,
                profile_type=args.profile,
                max_depth=args.max_depth,
                max_pages=args.max_pages,
                save_results=args.save,
                output_file=args.output
            )
        
        # Output results
        print("Crawl Results:")
        print("=" * 50)
        
        # Print summary
        crawl_info = result.get("crawl_info", {})
        summary = result.get("summary", {})
        
        print(f"URL: {crawl_info.get('url')}")
        print(f"Profile: {crawl_info.get('profile_used')}")
        print(f"Success: {crawl_info.get('success')}")
        print(f"Duration: {crawl_info.get('crawl_duration', 0):.2f}s")
        print(f"Elements Found: {summary.get('total_elements', 0)}")
        print(f"Page Type: {result.get('page_analysis', {}).get('page_type', 'unknown')}")
        print(f"Accessibility Score: {result.get('page_analysis', {}).get('accessibility_score', 0):.2f}")
        
        if args.save and "output_file" in result:
            print(f"Results saved to: {result['output_file']}")
        
        # Print detailed results if not saving to file
        if not args.save:
            print("\\nDetailed Results:")
            print(json.dumps(result, indent=2)[:2000] + "..." if len(json.dumps(result)) > 2000 else json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")


# Simple API functions for easy integration
async def crawl_for_qa_testing(url: str) -> Dict[str, Any]:
    """Simple function for QA testing"""
    crawler = ProfileCrawler()
    return await crawler.crawl_with_profile(url, ProfileType.QA_MANUAL_TESTER.value)


async def crawl_for_automation(url: str) -> Dict[str, Any]:
    """Simple function for automation testing"""
    crawler = ProfileCrawler()
    return await crawler.crawl_with_profile(url, ProfileType.QA_AUTOMATION_TESTER.value)


async def crawl_for_ux_design(url: str) -> Dict[str, Any]:
    """Simple function for UX design analysis"""
    crawler = ProfileCrawler()
    return await crawler.crawl_with_profile(url, ProfileType.UX_DESIGNER.value)


async def crawl_for_ui_design(url: str) -> Dict[str, Any]:
    """Simple function for UI design analysis"""
    crawler = ProfileCrawler()
    return await crawler.crawl_with_profile(url, ProfileType.UI_DESIGNER.value)


async def crawl_for_frontend_dev(url: str) -> Dict[str, Any]:
    """Simple function for frontend development analysis"""
    crawler = ProfileCrawler()
    return await crawler.crawl_with_profile(url, ProfileType.FRONTEND_DEVELOPER.value)


async def crawl_for_accessibility(url: str) -> Dict[str, Any]:
    """Simple function for accessibility auditing"""
    crawler = ProfileCrawler()
    return await crawler.crawl_with_profile(url, ProfileType.ACCESSIBILITY_AUDITOR.value)


# Example usage functions
async def example_usage():
    """Example usage of the profile crawler"""
    crawler = ProfileCrawler()
    
    # List available profiles
    print("Available Profiles:")
    profiles = crawler.list_available_profiles()
    for profile_type, description in profiles.items():
        print(f"- {profile_type}: {description}")
    
    print("\\n" + "="*50)
    
    # Example crawl with QA Manual Tester profile
    try:
        result = await crawler.crawl_with_profile(
            url="https://example.com",
            profile_type=ProfileType.QA_MANUAL_TESTER.value,
            save_results=True
        )
        
        print(f"QA Manual Tester Results:")
        print(f"- Elements found: {result['summary']['total_elements']}")
        print(f"- Interactive elements: {result['summary']['interactive_elements']}")
        print(f"- Accessibility score: {result['page_analysis']['accessibility_score']:.2f}")
        
        if "test_scenarios" in result:
            print(f"- Test scenarios: {len(result['test_scenarios'])}")
        
    except Exception as e:
        print(f"Error in example: {e}")


if __name__ == "__main__":
    asyncio.run(main())