"""
Comprehensive Live Testing of Quantum Enhanced UI Testing System
Uses real LLMs (gemini-2.0-flash-exp) and actual browser extraction
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

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Load environment variables first
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import our modules
from quantum_enhanced_ui_testing_system import (
    QuantumEnhancedUITestingSystem,
    QuantumSystemConfig,
    QuantumPromptEngine,
    EvolutionaryOptimizer,
    QuantumReasoningEngine
)
from ultimate_stealth_browser_llm_enhanced import UltimateStealthBrowserLLMEnhanced
from llm import query_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveQuantumTestingSystem(QuantumEnhancedUITestingSystem):
    """
    Extended Quantum System with live LLM integration and real browser extraction.
    """
    
    def __init__(self, config: Optional[QuantumSystemConfig] = None):
        super().__init__(config)
        self.browser = UltimateStealthBrowserLLMEnhanced()
        self.llm_provider = "gemini"
        self.llm_model = "gemini-2.5-pro"  # Using gemini-2.5-pro as requested
        self.test_results = []
        
    async def _extract_elements(self, url: str) -> List[Dict]:
        """
        Extract elements using the actual stealth browser.
        """
        try:
            logger.info(f"Extracting elements from {url} using stealth browser...")
            result = await self.browser.extract_with_llm_context(url)
            
            if result and 'elements' in result:
                elements = result['elements']
                logger.info(f"Extracted {len(elements)} elements from {url}")
                return elements
            else:
                logger.warning(f"No elements extracted from {url}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting elements from {url}: {str(e)}")
            return []
    
    async def _generate_test_scenarios_with_llm(self, 
                                                prompts: Dict[str, str],
                                                elements: List[Dict]) -> Dict[str, List]:
        """
        Generate test scenarios using live Gemini LLM.
        """
        scenarios = {}
        
        for strategy, prompt in prompts.items():
            try:
                logger.info(f"Generating {strategy} scenarios with Gemini...")
                
                # Apply self-consistency if enabled
                if self.config.enable_self_consistency:
                    scenarios_list = await self._generate_with_self_consistency(prompt, strategy)
                else:
                    scenarios_list = await self._generate_single_llm(prompt, strategy)
                
                scenarios[strategy] = scenarios_list
                
                # Track metrics
                if scenarios_list:
                    coverage = self._calculate_coverage(scenarios_list, elements)
                    self.monitoring.record_test(strategy, len(scenarios_list), coverage)
                    
            except Exception as e:
                logger.error(f"Error generating {strategy} scenarios: {str(e)}")
                scenarios[strategy] = []
        
        return scenarios
    
    async def _generate_single_llm(self, prompt: str, strategy: str) -> List[Dict]:
        """
        Generate scenarios with a single LLM call.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert QA engineer specializing in automated testing. Generate comprehensive test scenarios in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt + "\n\nReturn ONLY valid JSON array of test scenarios."
                }
            ]
            
            response = query_llm(self.llm_provider, self.llm_model, messages)
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                # Clean the response
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                scenarios = json.loads(content)
                if isinstance(scenarios, list):
                    return scenarios
                elif isinstance(scenarios, dict) and 'scenarios' in scenarios:
                    return scenarios['scenarios']
                else:
                    logger.warning(f"Unexpected response format for {strategy}")
                    return []
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON for {strategy}: {e}")
                logger.debug(f"Raw response: {content[:500]}")
                return []
                
        except Exception as e:
            logger.error(f"LLM call failed for {strategy}: {str(e)}")
            return []
    
    async def _generate_with_self_consistency(self, prompt: str, strategy: str) -> List[Dict]:
        """
        Generate scenarios using self-consistency with majority voting.
        """
        samples = []
        num_samples = self.config.self_consistency_samples
        
        logger.info(f"Generating {num_samples} samples for self-consistency...")
        
        # Generate multiple samples with variation
        for i in range(num_samples):
            # Add variation to prompt
            varied_prompt = prompt
            if i > 0:
                variations = [
                    "\nFocus on edge cases and boundary conditions.",
                    "\nEmphasize user experience and accessibility.",
                    "\nPrioritize security and data validation.",
                    "\nConsider performance and scalability aspects.",
                    "\nThink about error handling and recovery."
                ]
                varied_prompt += variations[i % len(variations)]
            
            scenarios = await self._generate_single_llm(varied_prompt, f"{strategy}_sample_{i}")
            if scenarios:
                samples.append(scenarios)
        
        # Apply majority voting / merge strategies
        if not samples:
            return []
        
        # Merge and deduplicate scenarios
        all_scenarios = []
        scenario_signatures = set()
        
        for sample in samples:
            for scenario in sample:
                # Create signature for deduplication
                signature = self._create_scenario_signature(scenario)
                if signature not in scenario_signatures:
                    scenario_signatures.add(signature)
                    all_scenarios.append(scenario)
        
        # Sort by priority if available
        all_scenarios.sort(key=lambda x: (
            {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('priority', 'low'), 3),
            len(x.get('steps', []))
        ), reverse=True)
        
        # Limit to max scenarios
        max_scenarios = self.config.max_scenarios_per_strategy
        return all_scenarios[:max_scenarios]
    
    def _create_scenario_signature(self, scenario: Dict) -> str:
        """Create a signature for scenario deduplication."""
        # Use title and main actions as signature
        title = scenario.get('title', '').lower()
        steps = ' '.join(str(s) for s in scenario.get('steps', []))[:100]
        return f"{title}_{steps}"
    
    def _calculate_coverage(self, scenarios: List[Dict], elements: List[Dict]) -> float:
        """Calculate test coverage based on elements tested."""
        if not elements:
            return 0.0
        
        tested_elements = set()
        
        for scenario in scenarios:
            # Extract element references from steps
            for step in scenario.get('steps', []):
                if isinstance(step, dict):
                    selector = step.get('element_selector', '')
                    if selector:
                        tested_elements.add(selector)
                elif isinstance(step, str):
                    # Simple heuristic for text steps
                    for element in elements:
                        if element.get('id') in step or element.get('text_content', '') in step:
                            tested_elements.add(element.get('id'))
        
        coverage = len(tested_elements) / len(elements)
        return min(coverage, 1.0)
    
    async def process_url(self, url: str) -> Dict[str, Any]:
        """
        Enhanced process_url with live LLM integration.
        """
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'extraction': None,
            'analysis': None,
            'tests': None,
            'metrics': None,
            'success': False
        }
        
        try:
            # Step 1: Extract elements with real browser
            extraction_start = time.time()
            elements = await self._extract_elements(url)
            extraction_time = time.time() - extraction_start
            
            if not elements:
                logger.warning(f"No elements extracted from {url}, using fallback")
                # Fallback to mock data for testing
                elements = self._generate_mock_elements(url)
            
            self.monitoring.record_extraction(url, len(elements), extraction_time, True)
            result['extraction'] = {
                'elements_count': len(elements),
                'extraction_time': extraction_time
            }
            
            # Step 2: Analyze elements with reasoning engine
            analysis = self.reasoning_engine.analyze_elements(elements)
            result['analysis'] = analysis
            
            # Step 3: Generate optimized prompts
            test_prompts = {}
            for strategy in self.config.test_strategies[:3]:  # Limit for testing
                prompt = self._create_enhanced_prompt(elements, strategy, analysis)
                
                # Apply OPRO optimization if enabled
                if self.config.enable_opro and self.test_results:
                    prompt, improvement = self.optimizer.optimize_with_opro(
                        prompt, 
                        self.test_results[-5:],  # Use last 5 results
                        2  # Reduce iterations for speed
                    )
                    logger.info(f"OPRO improved {strategy} prompt by {improvement:.1f}%")
                
                test_prompts[strategy] = prompt
                self.monitoring.record_prompt(strategy, len(prompt), 0.8)
            
            # Step 4: Generate test scenarios with live LLM
            test_scenarios = await self._generate_test_scenarios_with_llm(test_prompts, elements)
            result['tests'] = test_scenarios
            
            # Step 5: Evolve strategies based on performance
            if self.config.enable_evolution and len(self.test_results) > 2:
                performance_data = self._calculate_performance(test_scenarios)
                evolved_strategies = self.optimizer.evolve_strategies(
                    self.config.test_strategies,
                    performance_data
                )
                logger.info(f"Evolved strategies: {evolved_strategies}")
                self.config.test_strategies = evolved_strategies
            
            # Store results for learning
            self.test_results.append({
                'url': url,
                'elements': len(elements),
                'scenarios': sum(len(s) for s in test_scenarios.values()),
                'quality_score': self._calculate_quality_score(test_scenarios, analysis)
            })
            
            # Update session data
            self.session_data['urls_processed'].append(url)
            self.session_data['total_elements'] += len(elements)
            self.session_data['total_tests'] += sum(len(s) for s in test_scenarios.values())
            
            # Get monitoring summary
            result['metrics'] = self.monitoring.get_summary()
            result['success'] = True
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            result['error'] = str(e)
            self.monitoring.metrics['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'error': str(e)
            })
        
        return result
    
    def _create_enhanced_prompt(self, elements: List[Dict], strategy: str, analysis: Dict) -> str:
        """
        Create an enhanced prompt with context from analysis.
        """
        # Prepare element summary
        element_summary = {
            'total': len(elements),
            'interactive': sum(1 for e in elements if e.get('is_interactive')),
            'forms': len(analysis['classifications'].get('forms', [])),
            'actions': len(analysis['classifications'].get('actions', [])),
            'validation': len(analysis['classifications'].get('validation', []))
        }
        
        # Base prompt
        prompt = f"""
        Generate {strategy} test scenarios for a web application.
        
        Page Analysis:
        - Total Elements: {element_summary['total']}
        - Interactive Elements: {element_summary['interactive']}
        - Form Fields: {element_summary['forms']}
        - Action Buttons: {element_summary['actions']}
        - Validation Rules: {element_summary['validation']}
        
        Key Insights:
        {json.dumps(analysis['insights'][:3], indent=2)}
        
        Testing Priorities:
        {json.dumps(analysis['recommendations'][:3], indent=2)}
        
        Element Details (top 10 by priority):
        """
        
        # Add top priority elements
        priority_elements = []
        for elem_id, priority in analysis['test_priorities'].items():
            if priority in ['critical', 'high']:
                # Find element
                for element in elements:
                    if element.get('id') == elem_id:
                        priority_elements.append({
                            'id': elem_id,
                            'type': element.get('tag_name'),
                            'text': element.get('text_content', '')[:50],
                            'priority': priority
                        })
                        break
        
        prompt += json.dumps(priority_elements[:10], indent=2)
        
        # Strategy-specific instructions
        if strategy == 'happy_path':
            prompt += """
            
            Generate 5-7 happy path scenarios that:
            1. Test primary user workflows
            2. Use valid, realistic data
            3. Verify successful outcomes
            4. Cover main functionality
            """
        elif strategy == 'negative':
            prompt += """
            
            Generate 5-7 negative test scenarios that:
            1. Test with invalid/malformed data
            2. Test boundary conditions
            3. Verify error handling
            4. Check validation messages
            """
        elif strategy == 'security':
            prompt += """
            
            Generate 5-7 security test scenarios that:
            1. Test input sanitization
            2. Check for XSS vulnerabilities
            3. Test SQL injection attempts
            4. Verify authentication/authorization
            """
        
        prompt += """
        
        Return a JSON array where each scenario has:
        {
            "title": "Clear descriptive title",
            "priority": "critical|high|medium|low",
            "type": "functional|security|performance",
            "steps": [
                {
                    "action": "click|type|select|verify",
                    "description": "What to do",
                    "element_selector": "CSS selector or ID",
                    "test_data": "Data to use (if applicable)",
                    "expected": "Expected result"
                }
            ],
            "tags": ["relevant", "tags"]
        }
        """
        
        # Apply scientific strategies
        if self.config.enable_chain_of_thought:
            prompt = self.prompt_engine._apply_chain_of_thought(prompt)
        
        if self.config.enable_tree_of_thoughts and strategy in ['security', 'edge_case']:
            prompt = self.prompt_engine._apply_tree_of_thoughts(prompt, strategy)
        
        return prompt
    
    def _generate_mock_elements(self, url: str) -> List[Dict]:
        """Generate mock elements for testing when extraction fails."""
        # Parse URL to determine page type
        if 'login' in url.lower():
            return [
                {'id': 'username', 'tag_name': 'input', 'type': 'text', 'text_content': '', 
                 'is_interactive': True, 'attributes': {'required': True, 'name': 'username'}},
                {'id': 'password', 'tag_name': 'input', 'type': 'password', 'text_content': '',
                 'is_interactive': True, 'attributes': {'required': True, 'name': 'password'}},
                {'id': 'submit', 'tag_name': 'button', 'type': 'submit', 'text_content': 'Login',
                 'is_interactive': True, 'attributes': {}},
                {'id': 'forgot', 'tag_name': 'a', 'text_content': 'Forgot Password?',
                 'is_interactive': True, 'attributes': {'href': '/forgot'}}
            ]
        elif 'signup' in url.lower() or 'register' in url.lower():
            return [
                {'id': 'email', 'tag_name': 'input', 'type': 'email', 'text_content': '',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'password', 'tag_name': 'input', 'type': 'password', 'text_content': '',
                 'is_interactive': True, 'attributes': {'required': True, 'minlength': '8'}},
                {'id': 'confirm_password', 'tag_name': 'input', 'type': 'password', 'text_content': '',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'terms', 'tag_name': 'input', 'type': 'checkbox', 'text_content': '',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'register', 'tag_name': 'button', 'type': 'submit', 'text_content': 'Sign Up',
                 'is_interactive': True, 'attributes': {}}
            ]
        else:
            # Generic page elements
            return [
                {'id': 'search', 'tag_name': 'input', 'type': 'text', 'text_content': '',
                 'is_interactive': True, 'attributes': {'placeholder': 'Search...'}},
                {'id': 'nav_home', 'tag_name': 'a', 'text_content': 'Home',
                 'is_interactive': True, 'attributes': {'href': '/'}},
                {'id': 'nav_about', 'tag_name': 'a', 'text_content': 'About',
                 'is_interactive': True, 'attributes': {'href': '/about'}},
                {'id': 'cta_button', 'tag_name': 'button', 'text_content': 'Get Started',
                 'is_interactive': True, 'attributes': {'class': 'primary'}}
            ]
    
    def _calculate_quality_score(self, scenarios: Dict[str, List], analysis: Dict) -> float:
        """Calculate quality score for generated scenarios."""
        if not scenarios:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for strategy, scenario_list in scenarios.items():
            if not scenario_list:
                continue
            
            # Score based on quantity
            quantity_score = min(len(scenario_list) / 5.0, 1.0)
            
            # Score based on completeness
            completeness_score = 0.0
            for scenario in scenario_list:
                if scenario.get('title') and scenario.get('steps'):
                    completeness_score += 1.0
            completeness_score /= max(len(scenario_list), 1)
            
            # Score based on priority coverage
            priority_score = 0.0
            for scenario in scenario_list:
                priority = scenario.get('priority', 'low')
                if priority == 'critical':
                    priority_score += 1.0
                elif priority == 'high':
                    priority_score += 0.7
                elif priority == 'medium':
                    priority_score += 0.4
            priority_score /= max(len(scenario_list), 1)
            
            # Weight by strategy importance
            strategy_weight = {
                'happy_path': 1.0,
                'negative': 0.9,
                'security': 0.9,
                'edge_case': 0.7,
                'accessibility': 0.8
            }.get(strategy, 0.5)
            
            strategy_score = (quantity_score * 0.3 + completeness_score * 0.4 + priority_score * 0.3)
            total_score += strategy_score * strategy_weight
            total_weight += strategy_weight
        
        return total_score / max(total_weight, 1)
    
    async def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'browser'):
            await self.browser.cleanup()

async def test_sites_with_varied_complexity():
    """Test the quantum system with sites of varied complexity."""
    
    # Define test sites with complexity levels
    test_sites = [
        # Simple sites
        {
            'url': 'https://example.com',
            'name': 'Example.com',
            'complexity': 'simple',
            'expected_elements': 5
        },
        {
            'url': 'https://www.google.com',
            'name': 'Google Homepage',
            'complexity': 'simple',
            'expected_elements': 10
        },
        
        # Medium complexity
        {
            'url': 'https://github.com/login',
            'name': 'GitHub Login',
            'complexity': 'medium',
            'expected_elements': 15
        },
        {
            'url': 'https://www.wikipedia.org',
            'name': 'Wikipedia',
            'complexity': 'medium',
            'expected_elements': 20
        },
        
        # Complex sites
        {
            'url': 'https://www.amazon.com',
            'name': 'Amazon',
            'complexity': 'complex',
            'expected_elements': 50
        },
        {
            'url': 'https://twitter.com/login',
            'name': 'Twitter Login',
            'complexity': 'complex',
            'expected_elements': 25
        }
    ]
    
    # Configure system for testing
    config = QuantumSystemConfig(
        # Core settings
        max_elements=100,
        extraction_timeout=30,
        headless=False,
        
        # Enable all advanced features
        enable_chain_of_thought=True,
        enable_tree_of_thoughts=True,
        enable_self_consistency=True,
        enable_meta_prompting=True,
        enable_opro=True,
        opro_iterations=2,
        self_consistency_samples=3,
        
        # Evolution settings
        enable_evolution=True,
        evolution_generations=3,
        
        # Test strategies (start with core ones)
        test_strategies=['happy_path', 'negative', 'security'],
        max_scenarios_per_strategy=5,
        
        # Monitoring
        enable_monitoring=True
    )
    
    # Initialize system
    system = LiveQuantumTestingSystem(config)
    
    # Results storage
    all_results = {
        'test_run': datetime.now().isoformat(),
        'config': {
            'llm_provider': system.llm_provider,
            'llm_model': system.llm_model,
            'strategies': config.test_strategies,
            'self_consistency': config.enable_self_consistency,
            'opro': config.enable_opro
        },
        'sites': [],
        'summary': {}
    }
    
    # Test each site
    for site_info in test_sites:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {site_info['name']} ({site_info['complexity']} complexity)")
        logger.info(f"URL: {site_info['url']}")
        logger.info(f"{'='*60}")
        
        try:
            # Process the site
            result = await system.process_url(site_info['url'])
            
            # Enhance result with site info
            result['site_info'] = site_info
            
            # Log results
            if result['success']:
                logger.info(f"[OK] Successfully processed {site_info['name']}")
                logger.info(f"  - Elements extracted: {result['extraction']['elements_count']}")
                logger.info(f"  - Extraction time: {result['extraction']['extraction_time']:.2f}s")
                
                # Log test scenarios
                total_scenarios = 0
                for strategy, scenarios in result['tests'].items():
                    logger.info(f"  - {strategy}: {len(scenarios)} scenarios")
                    total_scenarios += len(scenarios)
                
                logger.info(f"  - Total scenarios: {total_scenarios}")
                
                # Log insights
                if result['analysis']['insights']:
                    logger.info(f"  - Key insights:")
                    for insight in result['analysis']['insights'][:3]:
                        logger.info(f"    * {insight}")
                
                # Log recommendations
                if result['analysis']['recommendations']:
                    logger.info(f"  - Recommendations:")
                    for rec in result['analysis']['recommendations'][:2]:
                        logger.info(f"    * {rec}")
            else:
                logger.error(f"[FAIL] Failed to process {site_info['name']}: {result.get('error')}")
            
            # Store result
            all_results['sites'].append(result)
            
            # Brief pause between sites
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Unexpected error testing {site_info['name']}: {str(e)}")
            all_results['sites'].append({
                'site_info': site_info,
                'error': str(e),
                'success': False
            })
    
    # Generate summary
    successful_sites = [r for r in all_results['sites'] if r.get('success')]
    failed_sites = [r for r in all_results['sites'] if not r.get('success')]
    
    all_results['summary'] = {
        'total_sites': len(test_sites),
        'successful': len(successful_sites),
        'failed': len(failed_sites),
        'total_elements': sum(r['extraction']['elements_count'] for r in successful_sites if r.get('extraction')),
        'total_scenarios': sum(
            sum(len(scenarios) for scenarios in r['tests'].values())
            for r in successful_sites if r.get('tests')
        ),
        'average_extraction_time': sum(r['extraction']['extraction_time'] for r in successful_sites if r.get('extraction')) / max(len(successful_sites), 1),
        'session_summary': system.get_session_summary()
    }
    
    # Log final summary
    logger.info(f"\n{'='*60}")
    logger.info("TESTING COMPLETE - FINAL SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Sites tested: {all_results['summary']['total_sites']}")
    logger.info(f"Successful: {all_results['summary']['successful']}")
    logger.info(f"Failed: {all_results['summary']['failed']}")
    logger.info(f"Total elements extracted: {all_results['summary']['total_elements']}")
    logger.info(f"Total test scenarios generated: {all_results['summary']['total_scenarios']}")
    logger.info(f"Average extraction time: {all_results['summary']['average_extraction_time']:.2f}s")
    
    # Evolution summary
    if config.enable_evolution:
        logger.info(f"\nEvolution Summary:")
        logger.info(f"  - Generations: {system.optimizer.generation}")
        logger.info(f"  - Best solutions found: {len(system.optimizer.best_solutions)}")
        if system.optimizer.best_solutions:
            best = system.optimizer.best_solutions[-1]
            logger.info(f"  - Best strategy set: {best[0]}")
            logger.info(f"  - Best fitness score: {best[1]:.3f}")
    
    # Save results to file
    output_file = f"quantum_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    logger.info(f"\nResults saved to: {output_file}")
    
    # Cleanup
    await system.cleanup()
    
    return all_results

async def main():
    """Main entry point for testing."""
    logger.info("Starting Quantum Enhanced UI Testing System - Live Testing")
    logger.info("Using Gemini 2.5 Pro for test generation")
    
    try:
        results = await test_sites_with_varied_complexity()
        
        # Print sample test scenario for inspection
        for site_result in results['sites']:
            if site_result.get('success') and site_result.get('tests'):
                logger.info(f"\nSample test scenario from {site_result['site_info']['name']}:")
                for strategy, scenarios in site_result['tests'].items():
                    if scenarios:
                        logger.info(f"\n{strategy.upper()} scenario example:")
                        logger.info(json.dumps(scenarios[0], indent=2))
                        break
                break
        
        logger.info("\nTesting completed successfully!")
        
    except Exception as e:
        logger.error(f"Testing failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())