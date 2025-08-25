"""
Verified Comprehensive Test with Exactly Three LLMs
Tests with gemini-2.5-pro, gpt-5, and claude-sonnet-4-20250514
NO EXCEPTIONS - Will stop if attempting to use any other model
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# Setup environment
sys.path.append(str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

# Imports
from llm import query_llm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# CRITICAL: Only these exact models are allowed
REQUIRED_MODELS = [
    ("gemini", "gemini-2.5-pro"),
    ("openai", "gpt-5"),
    ("claude", "claude-sonnet-4-20250514")
]

class VerifiedThreeLLMTester:
    """Test system that ONLY uses the three specified models."""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'models_tested': [],
            'test_sites': [],
            'detailed_results': [],
            'summary': {}
        }
    
    def load_test_sites(self) -> list:
        """Load test sites from challenging sites database."""
        db_path = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\latest_version\challenging_sites_database.json")
        
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        # Select 3 diverse sites
        selected = [
            data['sites'][0],  # Cloudflare
            data['sites'][6],  # PayPal  
            data['sites'][4]   # Supreme
        ]
        
        logger.info(f"Selected sites: {[s['name'] for s in selected]}")
        return selected
    
    def get_mock_elements(self, site_category: str) -> list:
        """Get mock elements based on site category."""
        if 'financial' in site_category.lower():
            return [
                {'id': 'username', 'tag_name': 'input', 'type': 'text', 'required': True},
                {'id': 'password', 'tag_name': 'input', 'type': 'password', 'required': True},
                {'id': 'login_btn', 'tag_name': 'button', 'text': 'Sign In'},
                {'id': 'remember_me', 'tag_name': 'input', 'type': 'checkbox'},
                {'id': 'forgot_link', 'tag_name': 'a', 'text': 'Forgot Password?'}
            ]
        elif 'e-commerce' in site_category.lower():
            return [
                {'id': 'product_search', 'tag_name': 'input', 'type': 'text'},
                {'id': 'add_to_cart', 'tag_name': 'button', 'text': 'Add to Cart'},
                {'id': 'quantity', 'tag_name': 'input', 'type': 'number', 'value': '1'},
                {'id': 'checkout', 'tag_name': 'button', 'text': 'Checkout'},
                {'id': 'price', 'tag_name': 'span', 'text': '$99.99'}
            ]
        else:
            return [
                {'id': 'search', 'tag_name': 'input', 'type': 'text'},
                {'id': 'submit', 'tag_name': 'button', 'text': 'Submit'},
                {'id': 'nav_home', 'tag_name': 'a', 'text': 'Home'},
                {'id': 'contact', 'tag_name': 'a', 'text': 'Contact'}
            ]
    
    async def test_with_model(self, provider: str, model: str, site: dict, strategy: str) -> dict:
        """Test with a specific model - ONLY allows the three required models."""
        
        # CRITICAL VERIFICATION
        if (provider, model) not in REQUIRED_MODELS:
            error_msg = f"STOPPED: Attempted to use unauthorized model {provider}/{model}. Only allowed: {REQUIRED_MODELS}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Testing {site['name']} with {provider}/{model} for {strategy}")
        
        # Get mock elements
        elements = self.get_mock_elements(site['category'])
        
        # Create prompt
        prompt = f"""
        Generate {strategy} test scenarios for {site['name']} ({site['category']}).
        
        Site URL: {site['url']}
        Protection: {site['protection_system']}
        Difficulty: {site['difficulty']}
        
        Available Elements:
        {json.dumps(elements, indent=2)}
        
        Generate exactly 3 test scenarios for {strategy} testing.
        
        Return ONLY a JSON array with this structure:
        [
            {{
                "title": "Test scenario title",
                "priority": "critical|high|medium|low",
                "steps": [
                    {{
                        "action": "Action to perform",
                        "element": "Element to interact with",
                        "data": "Test data if needed",
                        "expected": "Expected result"
                    }}
                ],
                "tags": ["tag1", "tag2"]
            }}
        ]
        """
        
        try:
            start_time = time.time()
            
            # Call the LLM
            messages = [
                {"role": "system", "content": f"You are a QA expert specializing in {strategy} testing. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = query_llm(provider, model, messages)
            elapsed = time.time() - start_time
            
            # Parse response
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            scenarios = json.loads(content)
            
            logger.info(f"✓ Generated {len(scenarios)} scenarios in {elapsed:.1f}s")
            
            return {
                'success': True,
                'provider': provider,
                'model': model,
                'site': site['name'],
                'strategy': strategy,
                'scenarios': scenarios,
                'time': elapsed
            }
            
        except Exception as e:
            logger.error(f"✗ Error with {provider}/{model}: {str(e)[:100]}")
            return {
                'success': False,
                'provider': provider,
                'model': model,
                'site': site['name'],
                'strategy': strategy,
                'error': str(e)[:200],
                'time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def run_comprehensive_test(self):
        """Run the comprehensive test with all three models."""
        
        logger.info("="*60)
        logger.info("VERIFIED COMPREHENSIVE TEST WITH THREE LLMS")
        logger.info("="*60)
        
        # Verify models
        logger.info("Required models:")
        for provider, model in REQUIRED_MODELS:
            logger.info(f"  ✓ {provider}/{model}")
        
        # Load test sites
        sites = self.load_test_sites()
        self.test_results['test_sites'] = [s['name'] for s in sites]
        
        # Test each site with ONE model (to save time but verify all work)
        # We'll rotate through models
        strategies = ['happy_path', 'negative', 'security']
        
        for i, site in enumerate(sites):
            logger.info(f"\n--- Testing {site['name']} ---")
            
            # Use a different model for each site to verify all work
            provider, model = REQUIRED_MODELS[i % len(REQUIRED_MODELS)]
            
            site_results = {
                'site': site['name'],
                'model': f"{provider}/{model}",
                'results': []
            }
            
            for strategy in strategies:
                result = await self.test_with_model(provider, model, site, strategy)
                site_results['results'].append(result)
                
                # Show sample if successful
                if result['success'] and result['scenarios']:
                    first = result['scenarios'][0]
                    logger.info(f"  Sample: {first.get('title', 'N/A')}")
                
                # Rate limiting
                await asyncio.sleep(1)
            
            self.test_results['detailed_results'].append(site_results)
            
            # Save intermediate results
            self._save_intermediate_results(site['name'])
        
        # Now test ONE site with ALL models to verify each works
        logger.info("\n" + "="*60)
        logger.info("VERIFICATION: Testing one site with ALL three models")
        logger.info("="*60)
        
        verification_site = sites[0]  # Use Cloudflare
        verification_results = []
        
        for provider, model in REQUIRED_MODELS:
            logger.info(f"\nVerifying {provider}/{model}...")
            result = await self.test_with_model(provider, model, verification_site, 'happy_path')
            verification_results.append(result)
            
            if result['success']:
                logger.info(f"✓ {provider}/{model} verified working!")
            else:
                logger.info(f"✗ {provider}/{model} had an issue")
            
            await asyncio.sleep(2)
        
        self.test_results['verification'] = verification_results
        
        # Generate summary
        self._generate_summary()
        
        # Save final results
        output_file = f"quantum_verified_three_llms_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"\n✓ Results saved to: {output_file}")
        
        return self.test_results
    
    def _save_intermediate_results(self, site_name: str):
        """Save intermediate results."""
        filename = f"quantum_intermediate_{site_name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
    
    def _generate_summary(self):
        """Generate test summary."""
        total_tests = 0
        successful_tests = 0
        total_scenarios = 0
        model_stats = {}
        
        # Process detailed results
        for site_result in self.test_results['detailed_results']:
            for test in site_result['results']:
                total_tests += 1
                if test['success']:
                    successful_tests += 1
                    total_scenarios += len(test.get('scenarios', []))
                
                model_key = f"{test['provider']}/{test['model']}"
                if model_key not in model_stats:
                    model_stats[model_key] = {'attempts': 0, 'successes': 0, 'scenarios': 0}
                
                model_stats[model_key]['attempts'] += 1
                if test['success']:
                    model_stats[model_key]['successes'] += 1
                    model_stats[model_key]['scenarios'] += len(test.get('scenarios', []))
        
        # Process verification results
        verified_models = []
        for ver in self.test_results.get('verification', []):
            if ver['success']:
                verified_models.append(f"{ver['provider']}/{ver['model']}")
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_scenarios': total_scenarios,
            'model_statistics': model_stats,
            'verified_models': verified_models,
            'all_models_verified': len(verified_models) == len(REQUIRED_MODELS)
        }
        
        # Log summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Successful: {successful_tests}")
        logger.info(f"Success rate: {self.test_results['summary']['success_rate']:.1f}%")
        logger.info(f"Total scenarios: {total_scenarios}")
        
        logger.info("\nModel Performance:")
        for model, stats in model_stats.items():
            success_rate = (stats['successes'] / stats['attempts'] * 100) if stats['attempts'] > 0 else 0
            logger.info(f"  {model}: {stats['successes']}/{stats['attempts']} ({success_rate:.0f}%), {stats['scenarios']} scenarios")
        
        logger.info(f"\nVerified Models: {len(verified_models)}/{len(REQUIRED_MODELS)}")
        for model in verified_models:
            logger.info(f"  ✓ {model}")

async def main():
    """Main function."""
    
    # Final verification before starting
    logger.info("FINAL VERIFICATION: This test will ONLY use these models:")
    for provider, model in REQUIRED_MODELS:
        logger.info(f"  • {provider}/{model}")
    logger.info("\nIf any other model is attempted, the test will STOP.\n")
    
    # Run the test
    tester = VerifiedThreeLLMTester()
    results = await tester.run_comprehensive_test()
    
    # Display key results
    if results['summary']['all_models_verified']:
        logger.info("\n✓✓✓ SUCCESS: All three required models verified working! ✓✓✓")
    else:
        logger.info("\n⚠ Some models could not be verified")
    
    # Show a sample scenario from each model
    logger.info("\n" + "="*60)
    logger.info("SAMPLE SCENARIOS FROM EACH MODEL")
    logger.info("="*60)
    
    shown_models = set()
    for site_result in results['detailed_results']:
        for test in site_result['results']:
            model_key = f"{test['provider']}/{test['model']}"
            if model_key not in shown_models and test['success'] and test.get('scenarios'):
                shown_models.add(model_key)
                logger.info(f"\n{model_key} - {test['strategy']} scenario:")
                logger.info(json.dumps(test['scenarios'][0], indent=2))
                
                if len(shown_models) >= 3:
                    break
    
    return results

if __name__ == "__main__":
    asyncio.run(main())