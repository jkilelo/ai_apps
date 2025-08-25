#!/usr/bin/env python3
"""
Comprehensive Test Suite for Ultimate Stealth Browser LLM Enhanced
Tests the enhanced extraction capabilities against challenging sites.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ultimate_stealth_browser_llm_enhanced import (
    UltimateStealthBrowserLLMEnhanced,
    LLMEnhancedExtractionStrategy
)
from ultimate_stealth_browser import StealthConfig, StealthLevel
from ui_testing_v3.llm_optimized_element_structure import (
    ElementCategory,
    TestPriority,
    InteractionPattern,
    ValidationRule
)


class LLMEnhancedBrowserTester:
    """Comprehensive tester for LLM-enhanced browser extraction"""
    
    def __init__(self):
        self.results = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'LLM Enhanced Extraction',
                'browser': 'Ultimate Stealth Browser LLM Enhanced'
            },
            'sites_tested': [],
            'feature_coverage': {
                'semantic_context': {'tested': 0, 'found': 0},
                'business_context': {'tested': 0, 'found': 0},
                'hierarchy': {'tested': 0, 'found': 0},
                'validation_rules': {'tested': 0, 'found': 0},
                'accessibility': {'tested': 0, 'found': 0},
                'interaction_patterns': {'tested': 0, 'found': 0},
                'form_relationships': {'tested': 0, 'found': 0},
                'visual_context': {'tested': 0, 'found': 0},
                'state_context': {'tested': 0, 'found': 0},
                'user_journeys': {'tested': 0, 'found': 0},
                'critical_paths': {'tested': 0, 'found': 0},
                'security_considerations': {'tested': 0, 'found': 0}
            },
            'summary': {
                'total_sites': 0,
                'successful': 0,
                'failed': 0,
                'total_elements': 0,
                'total_time': 0
            }
        }
    
    async def test_site(self, browser: UltimateStealthBrowserLLMEnhanced, site: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single site and extract comprehensive LLM context"""
        
        print(f"\n{'='*60}")
        print(f"Testing: {site['name']}")
        print(f"URL: {site['url']}")
        print(f"Difficulty: {site['difficulty']}")
        print(f"Protection: {site['protection_system']}")
        print('='*60)
        
        start_time = time.time()
        site_result = {
            'name': site['name'],
            'url': site['url'],
            'category': site['category'],
            'difficulty': site['difficulty'],
            'protection_system': site['protection_system'],
            'success': False,
            'extraction_time': 0,
            'error': None,
            'metrics': {}
        }
        
        try:
            # Extract with LLM optimization
            page_structure = await browser.extract_elements_for_llm(site['url'])
            
            # Analyze extraction quality
            site_result['success'] = True
            site_result['extraction_time'] = round(time.time() - start_time, 2)
            
            # Count elements by category
            element_counts = {}
            total_elements = 0
            for category, elements in page_structure.elements_by_category.items():
                count = len(elements)
                element_counts[category.value] = count
                total_elements += count
            
            site_result['metrics'] = {
                'total_elements': total_elements,
                'elements_by_category': element_counts,
                'page_type': page_structure.page_type,
                'business_purpose': page_structure.business_purpose,
                'user_journeys': len(page_structure.user_journeys),
                'critical_paths': len(page_structure.critical_paths),
                'page_validations': len(page_structure.page_validations),
                'security_considerations': len(page_structure.security_considerations)
            }
            
            # Analyze feature richness
            feature_analysis = self.analyze_features(page_structure)
            site_result['feature_analysis'] = feature_analysis
            
            # Update feature coverage statistics
            self.update_feature_coverage(feature_analysis)
            
            # Print summary
            print(f"[SUCCESS] - Extracted {total_elements} elements in {site_result['extraction_time']}s")
            print(f"  Page Type: {page_structure.page_type}")
            print(f"  Business Purpose: {page_structure.business_purpose[:50]}...")
            print(f"  Categories: {list(element_counts.keys())}")
            print(f"  User Journeys: {len(page_structure.user_journeys)}")
            print(f"  Critical Paths: {len(page_structure.critical_paths)}")
            
            # Detailed feature analysis
            print("\n  Feature Richness:")
            for feature, data in feature_analysis.items():
                if data['found'] > 0:
                    print(f"    {feature}: {data['found']} elements with {data['quality']}")
            
            # Save detailed extraction for this site
            self.save_site_extraction(site['name'], page_structure)
            
        except Exception as e:
            site_result['success'] = False
            site_result['error'] = str(e)
            site_result['extraction_time'] = round(time.time() - start_time, 2)
            print(f"[FAILED]: {e}")
        
        return site_result
    
    def analyze_features(self, page_structure) -> Dict[str, Any]:
        """Analyze the richness of extracted features"""
        
        analysis = {
            'semantic_context': {'found': 0, 'quality': 'none'},
            'business_context': {'found': 0, 'quality': 'none'},
            'hierarchy': {'found': 0, 'quality': 'none'},
            'validation_rules': {'found': 0, 'quality': 'none'},
            'accessibility': {'found': 0, 'quality': 'none'},
            'interaction_patterns': {'found': 0, 'quality': 'none'},
            'form_relationships': {'found': 0, 'quality': 'none'},
            'visual_context': {'found': 0, 'quality': 'none'},
            'state_context': {'found': 0, 'quality': 'none'}
        }
        
        # Analyze all elements
        for category, elements in page_structure.elements_by_category.items():
            for element in elements:
                # Semantic context
                if element.semantic and element.semantic.primary_purpose:
                    analysis['semantic_context']['found'] += 1
                    if element.semantic.business_function:
                        analysis['semantic_context']['quality'] = 'rich'
                    elif analysis['semantic_context']['quality'] == 'none':
                        analysis['semantic_context']['quality'] = 'basic'
                
                # Business context
                if element.semantic and element.semantic.business_function:
                    analysis['business_context']['found'] += 1
                    analysis['business_context']['quality'] = 'present'
                
                # Hierarchy
                if element.hierarchy and (element.hierarchy.parent_section or element.hierarchy.parent_form):
                    analysis['hierarchy']['found'] += 1
                    if element.hierarchy.siblings and element.hierarchy.navigation_order is not None:
                        analysis['hierarchy']['quality'] = 'comprehensive'
                    elif analysis['hierarchy']['quality'] == 'none':
                        analysis['hierarchy']['quality'] = 'basic'
                
                # Validation rules
                if element.validation and element.validation.rules:
                    analysis['validation_rules']['found'] += 1
                    if element.validation.valid_values and element.validation.invalid_values:
                        analysis['validation_rules']['quality'] = 'comprehensive'
                    elif analysis['validation_rules']['quality'] == 'none':
                        analysis['validation_rules']['quality'] = 'basic'
                
                # Accessibility
                if element.accessibility and (element.accessibility.aria_role or element.accessibility.aria_label):
                    analysis['accessibility']['found'] += 1
                    if element.accessibility.wcag_level:
                        analysis['accessibility']['quality'] = 'wcag_compliant'
                    elif analysis['accessibility']['quality'] == 'none':
                        analysis['accessibility']['quality'] = 'basic'
                
                # Interaction patterns
                if element.interaction and element.interaction.primary_interaction:
                    analysis['interaction_patterns']['found'] += 1
                    if element.interaction.expected_outcomes and element.interaction.error_scenarios:
                        analysis['interaction_patterns']['quality'] = 'comprehensive'
                    elif analysis['interaction_patterns']['quality'] == 'none':
                        analysis['interaction_patterns']['quality'] = 'basic'
                
                # Visual context
                if element.visual and element.visual.is_visible:
                    analysis['visual_context']['found'] += 1
                    if element.visual.responsive_behavior:
                        analysis['visual_context']['quality'] = 'responsive'
                    elif analysis['visual_context']['quality'] == 'none':
                        analysis['visual_context']['quality'] = 'basic'
                
                # State context
                if element.state:
                    analysis['state_context']['found'] += 1
                    if element.state.depends_on or element.state.affects:
                        analysis['state_context']['quality'] = 'relational'
                    elif analysis['state_context']['quality'] == 'none':
                        analysis['state_context']['quality'] = 'basic'
        
        return analysis
    
    def update_feature_coverage(self, feature_analysis: Dict[str, Any]):
        """Update overall feature coverage statistics"""
        for feature, data in feature_analysis.items():
            if feature in self.results['feature_coverage']:
                self.results['feature_coverage'][feature]['tested'] += 1
                if data['found'] > 0:
                    self.results['feature_coverage'][feature]['found'] += 1
    
    def save_site_extraction(self, site_name: str, page_structure):
        """Save detailed extraction for a specific site"""
        output_file = f"llm_extraction_{site_name.replace(' ', '_').replace('.', '_')}.json"
        
        # Convert to dict for JSON serialization
        extraction_data = page_structure.model_dump()
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(extraction_data, f, indent=2, default=str)
        
        print(f"  Saved detailed extraction to: {output_file}")
    
    async def test_sites(self, sites: List[Dict[str, Any]]):
        """Test multiple sites"""
        
        print("\n" + "="*80)
        print("LLM-ENHANCED BROWSER COMPREHENSIVE TEST")
        print("="*80)
        print(f"Testing {len(sites)} challenging sites")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Configure browser
        config = StealthConfig(
            level=StealthLevel.MAXIMUM,
            headless=False,
            detect_frameworks=True,
            detect_captcha=True,
            handle_cookies=True,
            bypass_cloudflare=True,
            bypass_f5_networks=True,
            bypass_shape_security=True,
            bypass_datadome=True
        )
        
        # Test each site
        async with UltimateStealthBrowserLLMEnhanced(config) as browser:
            for i, site in enumerate(sites, 1):
                print(f"\n[{i}/{len(sites)}]", end="")
                
                # Test the site
                site_result = await self.test_site(browser, site)
                self.results['sites_tested'].append(site_result)
                
                # Update summary
                self.results['summary']['total_sites'] += 1
                if site_result['success']:
                    self.results['summary']['successful'] += 1
                    self.results['summary']['total_elements'] += site_result['metrics'].get('total_elements', 0)
                else:
                    self.results['summary']['failed'] += 1
                
                self.results['summary']['total_time'] += site_result['extraction_time']
                
                # Delay between sites
                if i < len(sites):
                    await asyncio.sleep(3)
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        summary = self.results['summary']
        success_rate = (summary['successful'] / summary['total_sites'] * 100) if summary['total_sites'] > 0 else 0
        
        print(f"\nOverall Results:")
        print(f"  Total Sites Tested: {summary['total_sites']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Total Elements Extracted: {summary['total_elements']}")
        print(f"  Total Time: {summary['total_time']:.2f}s")
        print(f"  Average Time per Site: {summary['total_time']/summary['total_sites']:.2f}s")
        
        # Feature coverage analysis
        print(f"\nFeature Coverage Analysis:")
        print(f"  {'Feature':<25} {'Sites with Feature':<20} {'Coverage %':<15}")
        print(f"  {'-'*60}")
        
        for feature, coverage in self.results['feature_coverage'].items():
            if coverage['tested'] > 0:
                coverage_pct = (coverage['found'] / coverage['tested'] * 100)
                coverage_str = f"{coverage['found']}/{coverage['tested']}"
                print(f"  {feature:<25} {coverage_str:<20} {coverage_pct:.1f}%")
        
        # Site-by-site results
        print(f"\nSite-by-Site Results:")
        print(f"  {'Site':<20} {'Status':<10} {'Elements':<12} {'Page Type':<15} {'Time (s)':<10}")
        print(f"  {'-'*75}")
        
        for site in self.results['sites_tested']:
            status = "Success" if site['success'] else "Failed"
            elements = site['metrics'].get('total_elements', 0) if site['success'] else 'N/A'
            page_type = site['metrics'].get('page_type', 'N/A') if site['success'] else 'N/A'
            
            print(f"  {site['name']:<20} {status:<10} {str(elements):<12} {page_type:<15} {site['extraction_time']:<10.2f}")
        
        # Category distribution
        print(f"\nElement Category Distribution:")
        category_totals = {}
        for site in self.results['sites_tested']:
            if site['success'] and 'elements_by_category' in site['metrics']:
                for category, count in site['metrics']['elements_by_category'].items():
                    category_totals[category] = category_totals.get(category, 0) + count
        
        if category_totals:
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            for category, total in sorted_categories[:10]:
                print(f"    {category:<20}: {total:>5} elements")
        
        # Failed sites analysis
        failed_sites = [s for s in self.results['sites_tested'] if not s['success']]
        if failed_sites:
            print(f"\nFailed Sites Analysis:")
            for site in failed_sites:
                print(f"  {site['name']}: {site['error']}")
        
        # High-value extractions
        print(f"\nHigh-Value Extractions (sites with rich context):")
        rich_sites = []
        for site in self.results['sites_tested']:
            if site['success']:
                metrics = site['metrics']
                richness_score = (
                    metrics.get('user_journeys', 0) * 10 +
                    metrics.get('critical_paths', 0) * 10 +
                    metrics.get('page_validations', 0) * 5 +
                    metrics.get('security_considerations', 0) * 5
                )
                if richness_score > 0:
                    rich_sites.append((site['name'], richness_score, metrics))
        
        rich_sites.sort(key=lambda x: x[1], reverse=True)
        for name, score, metrics in rich_sites[:5]:
            print(f"  {name}: Score={score}")
            print(f"    - User Journeys: {metrics.get('user_journeys', 0)}")
            print(f"    - Critical Paths: {metrics.get('critical_paths', 0)}")
            print(f"    - Validations: {metrics.get('page_validations', 0)}")
            print(f"    - Security Considerations: {metrics.get('security_considerations', 0)}")
    
    def save_results(self):
        """Save comprehensive test results"""
        output_file = f"llm_enhanced_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nResults saved to: {output_file}")
        return output_file


async def main():
    """Main test function"""
    
    # Load challenging sites database
    db_path = Path("latest_version/challenging_sites_database.json")
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    # Select diverse sites for comprehensive testing
    test_categories = {
        'Bot Protection': 2,      # Cloudflare, DataDome
        'E-commerce': 3,         # Nike, Supreme, Best Buy
        'Financial': 2,          # PayPal, Chase
        'Social Media': 2,       # Instagram, LinkedIn
        'Testing': 2,            # Bot Test, FingerprintJS
        'Government': 1,         # IRS
        'Search': 1              # Google
    }
    
    sites_to_test = []
    
    for category, count in test_categories.items():
        category_sites = [s for s in database['sites'] if s['category'] == category]
        # Prioritize higher difficulty sites
        category_sites.sort(key=lambda x: ['low', 'medium', 'high', 'very_high', 'extreme'].index(x['difficulty']), reverse=True)
        sites_to_test.extend(category_sites[:count])
    
    print(f"Selected {len(sites_to_test)} sites for comprehensive testing:")
    for site in sites_to_test:
        print(f"  - {site['name']} ({site['category']}, {site['difficulty']})")
    
    # Run tests
    tester = LLMEnhancedBrowserTester()
    await tester.test_sites(sites_to_test)
    
    # Print summary
    tester.print_summary()
    
    # Save results
    tester.save_results()
    
    print("\n" + "="*80)
    print("LLM-ENHANCED BROWSER TESTING COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()