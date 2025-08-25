#!/usr/bin/env python3
"""
Pipeline test script for Steps 1-4 with compatibility fixes
"""
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any

sys.path.append('/home/papa/projects/ui_testing_framework/latest_version')

from step1_element_extractor import UltimateElementExtractor, ExtractionConfig
from step2_gherkin_generator import generate_gherkin_tests
from step3_code_generator import PythonTestCodeGenerator
from step4_test_executor import TestExecutor, ExecutionConfig
from dataclasses import asdict

def convert_element_for_step2(element_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ElementData dict from Step 1 to ExtractedElement compatible dict for Step 2"""
    # Fields that ExtractedElement accepts
    allowed_fields = {
        'tag_name', 'element_type', 'xpath', 'css_selector', 'text_content',
        'id', 'class_names', 'name', 'href', 'is_clickable', 'is_visible',
        'role', 'aria_label', 'placeholder', 'value', 'input_type',
        'interaction_type', 'confidence_score'
    }
    
    # Filter to only allowed fields
    return {k: v for k, v in element_dict.items() if k in allowed_fields}

async def run_pipeline(sites: List[Dict[str, str]]):
    """Run the complete pipeline for testing sites"""
    
    results = {
        'step1': {},
        'step2': {},
        'step3': {},
        'step4': {}
    }
    
    print("="*60)
    print("🚀 TESTING UI FRAMEWORK PIPELINE (Steps 1-4)")
    print("="*60)
    
    # Step 1: Element Extraction
    print("\n" + "="*50)
    print("📍 STEP 1: Element Extraction")
    print("="*50)
    
    config = ExtractionConfig(
        timeout=30,
        enable_stealth=True,
        enable_human_simulation=True,
        headless=False,
        max_elements=10  # Limit for testing
    )
    
    extractor = UltimateElementExtractor(config)
    
    for site in sites:
        print(f"\n🔍 Extracting from {site['name']}...")
        try:
            extracted = await extractor.extract(site['url'])
            elements_as_dicts = [asdict(elem) for elem in extracted]
            
            results['step1'][site['name']] = {
                'success': True,
                'elements_count': len(elements_as_dicts),
                'elements': elements_as_dicts
            }
            print(f"✅ {site['name']}: Extracted {len(elements_as_dicts)} elements")
            
        except Exception as e:
            results['step1'][site['name']] = {
                'success': False,
                'error': str(e),
                'elements': []
            }
            print(f"❌ {site['name']}: {str(e)[:100]}")
    
    # Step 2: Gherkin Generation
    print("\n" + "="*50)
    print("📝 STEP 2: Gherkin Generation")
    print("="*50)
    
    for site_name, data in results['step1'].items():
        if data['success'] and data['elements']:
            print(f"\n📝 Generating Gherkin for {site_name}...")
            try:
                # Convert elements to Step 2 compatible format
                compatible_elements = [convert_element_for_step2(elem) for elem in data['elements'][:5]]
                
                # Generate Gherkin
                feature = await generate_gherkin_tests(
                    elements=compatible_elements,
                    url=next(s['url'] for s in sites if s['name'] == site_name),
                    feature_name=site_name
                )
                
                if feature:
                    results['step2'][site_name] = {
                        'success': True,
                        'feature': feature,
                        'scenarios_count': feature.count('Scenario:')
                    }
                    
                    # Save feature file
                    feature_file = Path(f'{site_name.lower()}.feature')
                    feature_file.write_text(feature)
                    
                    print(f"✅ {site_name}: Generated {feature.count('Scenario:')} scenarios")
                    print(f"   Saved to: {feature_file}")
                else:
                    results['step2'][site_name] = {'success': False, 'error': 'No feature generated'}
                    
            except Exception as e:
                results['step2'][site_name] = {'success': False, 'error': str(e)}
                print(f"❌ {site_name}: {str(e)[:100]}")
    
    # Step 3: Python Code Generation
    print("\n" + "="*50)
    print("🐍 STEP 3: Python Code Generation")
    print("="*50)
    
    generator = PythonTestCodeGenerator()
    
    for site_name, data in results['step2'].items():
        if data.get('success') and data.get('feature'):
            print(f"\n🐍 Generating Python code for {site_name}...")
            try:
                # Save feature to temp file
                feature_file = Path(f'{site_name.lower()}.feature')
                
                # Generate Python code
                test_files = generator.generate_from_feature_file(
                    feature_file=feature_file,
                    elements=results['step1'][site_name]['elements'][:5]
                )
                
                results['step3'][site_name] = {
                    'success': True,
                    'files_generated': list(test_files.keys()),
                    'test_count': sum(1 for f in test_files.values() for line in f.split('\\n') if 'def test_' in line)
                }
                
                # Save generated test files
                for filename, content in test_files.items():
                    Path(filename).write_text(content)
                    print(f"   Generated: {filename}")
                
                print(f"✅ {site_name}: Generated {len(test_files)} test files")
                
            except Exception as e:
                results['step3'][site_name] = {'success': False, 'error': str(e)}
                print(f"❌ {site_name}: {str(e)[:100]}")
    
    # Step 4: Test Execution
    print("\n" + "="*50)
    print("🏃 STEP 4: Test Execution")
    print("="*50)
    
    executor_config = ExecutionConfig(
        parallel=False,  # Sequential for demo
        max_workers=1,
        timeout=30,
        retry_failed=False
    )
    
    executor = TestExecutor(executor_config)
    
    for site_name in results['step3'].keys():
        if results['step3'][site_name].get('success'):
            print(f"\n🏃 Executing tests for {site_name}...")
            try:
                # Find test files for this site
                test_files = [Path(f) for f in results['step3'][site_name]['files_generated'] 
                             if Path(f).exists()]
                
                if test_files:
                    # Execute tests
                    exec_results = await executor.execute(test_files=test_files)
                    
                    results['step4'][site_name] = {
                        'success': True,
                        'total_tests': exec_results['summary']['total'],
                        'passed': exec_results['summary']['passed'],
                        'failed': exec_results['summary']['failed'],
                        'duration': exec_results['summary']['duration']
                    }
                    
                    print(f"✅ {site_name}: {exec_results['summary']['passed']}/{exec_results['summary']['total']} tests passed")
                else:
                    results['step4'][site_name] = {'success': False, 'error': 'No test files found'}
                    
            except Exception as e:
                results['step4'][site_name] = {'success': False, 'error': str(e)}
                print(f"❌ {site_name}: {str(e)[:100]}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 PIPELINE SUMMARY")
    print("="*60)
    
    for step_name, step_results in results.items():
        success_count = sum(1 for r in step_results.values() if r.get('success'))
        total_count = len(step_results)
        print(f"{step_name.upper()}: {success_count}/{total_count} successful")
    
    # Save complete results
    with open('pipeline_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n✅ Results saved to pipeline_results.json")
    
    return results

async def main():
    """Main entry point"""
    # Test with 3 challenging sites
    sites = [
        {'name': 'Supreme', 'url': 'https://www.supreme.com'},
        {'name': 'Instagram', 'url': 'https://www.instagram.com'},
        {'name': 'FingerprintJS', 'url': 'https://fingerprint.com/demo'}
    ]
    
    await run_pipeline(sites)

if __name__ == "__main__":
    asyncio.run(main())