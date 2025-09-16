"""
Comprehensive Live Testing with Multiple LLMs
Tests real sites from challenging_sites_database.json using:
- gemini-2.5-pro
- gpt-5
- claude-sonnet-4-20250514
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Setup environment
sys.path.append(str(Path(__file__).parent))
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import modules
from quantum_enhanced_ui_testing_system import (
    QuantumEnhancedUITestingSystem,
    QuantumSystemConfig,
    QuantumPromptEngine,
    QuantumReasoningEngine
)
from ultimate_stealth_browser_llm_enhanced import UltimateStealthBrowserLLMEnhanced
from llm import query_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# IMPORTANT: Only these models will be tested
REQUIRED_MODELS = [
    ("gemini", "gemini-2.5-pro"),
    ("openai", "gpt-5"),
    ("claude", "claude-sonnet-4-20250514")
]

class ComprehensiveLiveTestSystem:
    """Comprehensive testing system with multiple LLMs."""
    
    def __init__(self):
        self.config = QuantumSystemConfig(
            max_elements=100,
            extraction_timeout=60,
            headless=False,
            enable_stealth=True,
            enable_chain_of_thought=True,
            enable_tree_of_thoughts=True,
            enable_meta_prompting=True,
            test_strategies=['happy_path', 'negative', 'security', 'accessibility']
        )
        
        self.prompt_engine = QuantumPromptEngine(self.config)
        self.reasoning_engine = QuantumReasoningEngine(self.config)
        self.browser = UltimateStealthBrowserLLMEnhanced()
        
        # Test results storage
        self.all_results = {
            'test_run': datetime.now().isoformat(),
            'models_tested': [],
            'sites_tested': [],
            'detailed_results': [],
            'summary': {}
        }
    
    async def extract_elements_from_site(self, site_info: Dict) -> Dict:
        """Extract elements from a real site."""
        try:
            logger.info(f"Extracting elements from {site_info['name']}...")
            result = await self.browser.extract_with_llm_context(site_info['url'])
            
            if result and 'elements' in result:
                logger.info(f"✓ Extracted {len(result['elements'])} elements from {site_info['name']}")
                return {
                    'success': True,
                    'elements': result['elements'],
                    'metadata': result.get('metadata', {})
                }
            else:
                logger.warning(f"No elements extracted from {site_info['name']}")
                return {
                    'success': False,
                    'elements': self._generate_fallback_elements(site_info),
                    'metadata': {'fallback': True}
                }
                
        except Exception as e:
            logger.error(f"Error extracting from {site_info['name']}: {str(e)}")
            return {
                'success': False,
                'elements': self._generate_fallback_elements(site_info),
                'error': str(e),
                'metadata': {'fallback': True}
            }
    
    def _generate_fallback_elements(self, site_info: Dict) -> List[Dict]:
        """Generate fallback elements based on site category."""
        category = site_info.get('category', '').lower()
        
        if 'e-commerce' in category:
            return [
                {'id': 'search', 'tag_name': 'input', 'type': 'text', 'placeholder': 'Search products'},
                {'id': 'add_to_cart', 'tag_name': 'button', 'text_content': 'Add to Cart'},
                {'id': 'checkout', 'tag_name': 'button', 'text_content': 'Checkout'},
                {'id': 'quantity', 'tag_name': 'input', 'type': 'number', 'value': '1'},
                {'id': 'product_image', 'tag_name': 'img', 'alt': 'Product'},
                {'id': 'price', 'tag_name': 'span', 'text_content': '$99.99'}
            ]
        elif 'financial' in category:
            return [
                {'id': 'username', 'tag_name': 'input', 'type': 'text', 'required': True},
                {'id': 'password', 'tag_name': 'input', 'type': 'password', 'required': True},
                {'id': 'account_number', 'tag_name': 'input', 'type': 'text', 'pattern': '[0-9]+'},
                {'id': 'login', 'tag_name': 'button', 'text_content': 'Sign In'},
                {'id': 'forgot_password', 'tag_name': 'a', 'text_content': 'Forgot Password?'},
                {'id': 'security_question', 'tag_name': 'select', 'required': True}
            ]
        else:
            return [
                {'id': 'nav_home', 'tag_name': 'a', 'text_content': 'Home'},
                {'id': 'nav_about', 'tag_name': 'a', 'text_content': 'About'},
                {'id': 'contact_form', 'tag_name': 'form', 'action': '/contact'},
                {'id': 'email', 'tag_name': 'input', 'type': 'email'},
                {'id': 'submit', 'tag_name': 'button', 'text_content': 'Submit'}
            ]
    
    async def generate_test_with_llm(self, 
                                    provider: str,
                                    model: str,
                                    elements: List[Dict],
                                    site_info: Dict,
                                    strategy: str) -> Dict:
        """Generate test scenarios using specified LLM."""
        
        # Verify we're using only the required models
        if (provider, model) not in REQUIRED_MODELS:
            logger.error(f"STOPPING: Attempted to use unauthorized model {provider}/{model}")
            raise ValueError(f"Only these models are allowed: {REQUIRED_MODELS}")
        
        try:
            # Analyze elements first
            analysis = self.reasoning_engine.analyze_elements(elements)
            
            # Create enhanced prompt
            prompt = self._create_comprehensive_prompt(
                elements, site_info, strategy, analysis
            )
            
            # Apply quantum enhancements
            if strategy in ['security', 'accessibility']:
                prompt = self.prompt_engine._apply_chain_of_thought(prompt)
            
            if self.config.enable_meta_prompting:
                prompt = self.prompt_engine._apply_meta_prompting(prompt)
            
            # Log the model being used
            logger.info(f"Calling {provider}/{model} for {strategy} scenarios...")
            
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert QA automation engineer specializing in {strategy} testing. Generate comprehensive, executable test scenarios in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Call the LLM with timeout handling
            start_time = time.time()
            response = query_llm(provider, model, messages)
            elapsed = time.time() - start_time
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Clean JSON
            if content.startswith("```"):
                parts = content.split("```")
                if len(parts) > 1:
                    content = parts[1]
                    if content.startswith("json"):
                        content = content[4:]
            
            scenarios = json.loads(content)
            
            # Ensure it's a list
            if isinstance(scenarios, dict):
                if 'scenarios' in scenarios:
                    scenarios = scenarios['scenarios']
                else:
                    scenarios = [scenarios]
            
            logger.info(f"✓ {provider}/{model} generated {len(scenarios)} {strategy} scenarios in {elapsed:.1f}s")
            
            return {
                'success': True,
                'provider': provider,
                'model': model,
                'strategy': strategy,
                'scenarios': scenarios,
                'generation_time': elapsed,
                'elements_count': len(elements)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for {provider}/{model}: {str(e)}")
            return {
                'success': False,
                'provider': provider,
                'model': model,
                'strategy': strategy,
                'error': f"JSON parsing error: {str(e)}",
                'generation_time': time.time() - start_time if 'start_time' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"Error with {provider}/{model}: {str(e)}")
            return {
                'success': False,
                'provider': provider,
                'model': model,
                'strategy': strategy,
                'error': str(e),
                'generation_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def _create_comprehensive_prompt(self, 
                                    elements: List[Dict],
                                    site_info: Dict,
                                    strategy: str,
                                    analysis: Dict) -> str:
        """Create a comprehensive prompt for test generation."""
        
        # Prepare element summary
        element_types = {}
        for elem in elements:
            tag = elem.get('tag_name', 'unknown')
            element_types[tag] = element_types.get(tag, 0) + 1
        
        prompt = f"""
        Generate comprehensive {strategy} test scenarios for {site_info['name']}.
        
        Site Information:
        - URL: {site_info['url']}
        - Category: {site_info['category']}
        - Protection Level: {site_info['difficulty']}
        - Protection System: {site_info.get('protection_system', 'Unknown')}
        
        Page Analysis:
        - Total Elements: {len(elements)}
        - Element Types: {json.dumps(element_types, indent=2)}
        - Interactive Elements: {sum(1 for e in elements if e.get('is_interactive'))}
        
        Key Insights:
        {json.dumps(analysis['insights'][:5], indent=2)}
        
        Testing Recommendations:
        {json.dumps(analysis['recommendations'][:3], indent=2)}
        
        Top Priority Elements (first 10):
        """
        
        # Add priority elements
        priority_elements = []
        for elem_id, priority in list(analysis['test_priorities'].items())[:10]:
            for elem in elements:
                if elem.get('id') == elem_id:
                    priority_elements.append({
                        'id': elem_id,
                        'tag': elem.get('tag_name'),
                        'type': elem.get('type'),
                        'text': (elem.get('text_content', '') or '')[:30],
                        'priority': priority
                    })
                    break
        
        prompt += json.dumps(priority_elements, indent=2)
        
        # Strategy-specific instructions
        if strategy == 'happy_path':
            prompt += """
            
            Generate 5-8 happy path test scenarios that:
            1. Cover primary user workflows
            2. Use realistic, valid data
            3. Test successful outcomes
            4. Verify positive user experiences
            5. Include both simple and complex workflows
            """
        elif strategy == 'negative':
            prompt += """
            
            Generate 5-8 negative test scenarios that:
            1. Test with invalid/malformed data
            2. Test boundary conditions and edge cases
            3. Verify error handling and messages
            4. Test unauthorized access attempts
            5. Check for proper validation
            6. Test with empty/null/undefined values
            """
        elif strategy == 'security':
            prompt += """
            
            Generate 5-8 security test scenarios that:
            1. Test for SQL injection vulnerabilities
            2. Check for XSS (Cross-Site Scripting) attacks
            3. Test authentication and authorization
            4. Verify data encryption and protection
            5. Test for CSRF vulnerabilities
            6. Check for information disclosure
            7. Test session management
            """
        elif strategy == 'accessibility':
            prompt += """
            
            Generate 5-8 accessibility test scenarios that:
            1. Test keyboard navigation
            2. Verify screen reader compatibility
            3. Check ARIA labels and roles
            4. Test color contrast ratios
            5. Verify focus indicators
            6. Test with assistive technologies
            7. Check for WCAG 2.1 compliance
            """
        
        prompt += """
        
        Return a JSON array where each scenario MUST have this exact structure:
        [
            {
                "id": "unique_scenario_id",
                "title": "Clear, descriptive title",
                "description": "Brief description of what is being tested",
                "priority": "critical|high|medium|low",
                "category": "functional|security|performance|accessibility",
                "preconditions": ["List of setup requirements"],
                "steps": [
                    {
                        "step_number": 1,
                        "action": "Specific action to perform",
                        "element": "Element selector or identifier",
                        "data": "Test data if applicable",
                        "expected_result": "What should happen"
                    }
                ],
                "postconditions": ["Expected state after test"],
                "tags": ["relevant", "tags", "for", "categorization"]
            }
        ]
        
        Ensure all scenarios are specific to the site and use actual element IDs where possible.
        """
        
        return prompt
    
    async def test_site_with_all_models(self, site_info: Dict) -> Dict:
        """Test a single site with all required models."""
        site_result = {
            'site': site_info,
            'timestamp': datetime.now().isoformat(),
            'extraction': {},
            'test_results': []
        }
        
        # Step 1: Extract elements from the site
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing Site: {site_info['name']}")
        logger.info(f"URL: {site_info['url']}")
        logger.info(f"Category: {site_info['category']}")
        logger.info(f"Difficulty: {site_info['difficulty']}")
        logger.info(f"{'='*60}")
        
        extraction_result = await self.extract_elements_from_site(site_info)
        site_result['extraction'] = extraction_result
        
        elements = extraction_result['elements']
        logger.info(f"Working with {len(elements)} elements")
        
        # Step 2: Test with each required model
        for provider, model in REQUIRED_MODELS:
            logger.info(f"\n--- Testing with {provider}/{model} ---")
            
            model_results = {
                'provider': provider,
                'model': model,
                'strategies': {}
            }
            
            # Test each strategy
            for strategy in ['happy_path', 'negative', 'security']:
                logger.info(f"Generating {strategy} scenarios...")
                
                result = await self.generate_test_with_llm(
                    provider, model, elements, site_info, strategy
                )
                
                model_results['strategies'][strategy] = result
                
                # Log sample scenario if successful
                if result.get('success') and result.get('scenarios'):
                    first_scenario = result['scenarios'][0]
                    logger.info(f"  Sample: {first_scenario.get('title', 'No title')}")
                    logger.info(f"  Priority: {first_scenario.get('priority', 'N/A')}")
                    logger.info(f"  Steps: {len(first_scenario.get('steps', []))}")
                
                # Rate limiting between API calls
                await asyncio.sleep(2)
            
            site_result['test_results'].append(model_results)
            
            # Pause between models
            await asyncio.sleep(3)
        
        return site_result
    
    async def run_comprehensive_test(self, sites_to_test: List[Dict]) -> Dict:
        """Run comprehensive test on multiple sites."""
        logger.info("Starting Comprehensive Live Testing")
        logger.info(f"Sites to test: {len(sites_to_test)}")
        logger.info(f"Models to use: {[f'{p}/{m}' for p, m in REQUIRED_MODELS]}")
        
        for site in sites_to_test:
            try:
                site_result = await self.test_site_with_all_models(site)
                self.all_results['detailed_results'].append(site_result)
                self.all_results['sites_tested'].append(site['name'])
                
                # Save intermediate results
                self._save_results(f"quantum_live_intermediate_{site['id']}.json")
                
            except Exception as e:
                logger.error(f"Error testing {site['name']}: {str(e)}")
                self.all_results['detailed_results'].append({
                    'site': site,
                    'error': str(e),
                    'success': False
                })
            
            # Pause between sites
            await asyncio.sleep(5)
        
        # Generate summary
        self._generate_summary()
        
        # Save final results
        output_file = f"quantum_live_test_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_results(output_file)
        
        logger.info(f"\n{'='*60}")
        logger.info("COMPREHENSIVE TESTING COMPLETE")
        logger.info(f"Results saved to: {output_file}")
        logger.info(f"{'='*60}")
        
        return self.all_results
    
    def _generate_summary(self):
        """Generate test summary."""
        total_scenarios = 0
        successful_generations = 0
        total_attempts = 0
        model_performance = {}
        
        for result in self.all_results['detailed_results']:
            for model_result in result.get('test_results', []):
                model_key = f"{model_result['provider']}/{model_result['model']}"
                
                if model_key not in model_performance:
                    model_performance[model_key] = {
                        'attempts': 0,
                        'successes': 0,
                        'scenarios': 0,
                        'avg_time': []
                    }
                
                for strategy, strategy_result in model_result['strategies'].items():
                    total_attempts += 1
                    model_performance[model_key]['attempts'] += 1
                    
                    if strategy_result.get('success'):
                        successful_generations += 1
                        model_performance[model_key]['successes'] += 1
                        
                        scenarios = strategy_result.get('scenarios', [])
                        total_scenarios += len(scenarios)
                        model_performance[model_key]['scenarios'] += len(scenarios)
                        
                        if 'generation_time' in strategy_result:
                            model_performance[model_key]['avg_time'].append(
                                strategy_result['generation_time']
                            )
        
        # Calculate averages
        for model_key, perf in model_performance.items():
            if perf['avg_time']:
                perf['avg_generation_time'] = sum(perf['avg_time']) / len(perf['avg_time'])
            else:
                perf['avg_generation_time'] = 0
            del perf['avg_time']
            
            perf['success_rate'] = (perf['successes'] / perf['attempts'] * 100) if perf['attempts'] > 0 else 0
        
        self.all_results['summary'] = {
            'total_sites': len(self.all_results['sites_tested']),
            'total_attempts': total_attempts,
            'successful_generations': successful_generations,
            'total_scenarios': total_scenarios,
            'overall_success_rate': (successful_generations / total_attempts * 100) if total_attempts > 0 else 0,
            'model_performance': model_performance,
            'models_tested': list(model_performance.keys())
        }
        
        # Log summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Sites tested: {self.all_results['summary']['total_sites']}")
        logger.info(f"Total generation attempts: {total_attempts}")
        logger.info(f"Successful generations: {successful_generations}")
        logger.info(f"Total scenarios created: {total_scenarios}")
        logger.info(f"Overall success rate: {self.all_results['summary']['overall_success_rate']:.1f}%")
        
        logger.info("\nModel Performance:")
        for model, perf in model_performance.items():
            logger.info(f"\n{model}:")
            logger.info(f"  Success rate: {perf['success_rate']:.1f}%")
            logger.info(f"  Scenarios generated: {perf['scenarios']}")
            logger.info(f"  Avg generation time: {perf['avg_generation_time']:.1f}s")
    
    def _save_results(self, filename: str):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.all_results, f, indent=2, default=str)
    
    async def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'browser'):
            await self.browser.cleanup()

async def main():
    """Main function to run comprehensive tests."""
    
    # Load challenging sites database
    sites_db_path = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\latest_version\challenging_sites_database.json")
    
    with open(sites_db_path, 'r') as f:
        sites_database = json.load(f)
    
    # Select 3 sites with different difficulty levels
    sites_to_test = [
        sites_database['sites'][0],  # Cloudflare - Bot Protection (high)
        sites_database['sites'][6],  # PayPal - Financial (high)
        sites_database['sites'][4],  # Supreme - E-commerce (extreme)
    ]
    
    logger.info("="*60)
    logger.info("COMPREHENSIVE LIVE TESTING WITH REQUIRED LLMS")
    logger.info("="*60)
    logger.info(f"Models to test: {[f'{p}/{m}' for p, m in REQUIRED_MODELS]}")
    logger.info(f"Sites selected: {[s['name'] for s in sites_to_test]}")
    logger.info("="*60)
    
    # Initialize test system
    tester = ComprehensiveLiveTestSystem()
    
    try:
        # Run comprehensive tests
        results = await tester.run_comprehensive_test(sites_to_test)
        
        # Display final summary
        logger.info("\n" + "="*60)
        logger.info("FINAL RESULTS")
        logger.info("="*60)
        
        for site_result in results['detailed_results']:
            site_name = site_result['site']['name']
            logger.info(f"\n{site_name}:")
            
            for model_result in site_result.get('test_results', []):
                model = f"{model_result['provider']}/{model_result['model']}"
                successful_strategies = sum(
                    1 for s in model_result['strategies'].values() 
                    if s.get('success')
                )
                total_scenarios = sum(
                    len(s.get('scenarios', [])) 
                    for s in model_result['strategies'].values() 
                    if s.get('success')
                )
                logger.info(f"  {model}: {successful_strategies}/3 strategies, {total_scenarios} scenarios")
        
        logger.info("\n✓ Testing completed successfully!")
        
    except Exception as e:
        logger.error(f"Testing failed: {str(e)}")
        raise
    
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    # Verify required models before starting
    logger.info("Verifying required models...")
    for provider, model in REQUIRED_MODELS:
        logger.info(f"  - {provider}/{model}: Required")
    
    logger.info("\nStarting comprehensive live testing...")
    logger.info("This may take up to 10 minutes. Please be patient.")
    
    asyncio.run(main())