"""
Test Quantum System with Gemini-2.5-pro LLM Integration
Focus on LLM test generation without browser extraction
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import modules
from quantum_enhanced_ui_testing_system import (
    QuantumEnhancedUITestingSystem,
    QuantumSystemConfig,
    QuantumPromptEngine
)
from llm import query_llm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplifiedQuantumTester:
    """Simplified tester focusing on LLM integration."""
    
    def __init__(self):
        self.config = QuantumSystemConfig(
            enable_chain_of_thought=True,
            enable_tree_of_thoughts=True,
            enable_self_consistency=False,  # Disable for speed
            enable_meta_prompting=True,
            test_strategies=['happy_path', 'negative', 'security']
        )
        self.prompt_engine = QuantumPromptEngine(self.config)
        self.llm_provider = "gemini"
        self.llm_model = "gemini-2.5-pro"
        
    def generate_mock_elements(self, page_type: str) -> list:
        """Generate mock elements for testing."""
        if page_type == "login":
            return [
                {'id': 'username', 'tag_name': 'input', 'type': 'text', 
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'password', 'tag_name': 'input', 'type': 'password',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'remember_me', 'tag_name': 'input', 'type': 'checkbox',
                 'is_interactive': True, 'attributes': {}},
                {'id': 'submit_btn', 'tag_name': 'button', 'text_content': 'Login',
                 'is_interactive': True, 'attributes': {'type': 'submit'}},
                {'id': 'forgot_link', 'tag_name': 'a', 'text_content': 'Forgot Password?',
                 'is_interactive': True, 'attributes': {'href': '/forgot'}}
            ]
        elif page_type == "signup":
            return [
                {'id': 'email', 'tag_name': 'input', 'type': 'email',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'username', 'tag_name': 'input', 'type': 'text',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'password', 'tag_name': 'input', 'type': 'password',
                 'is_interactive': True, 'attributes': {'required': True, 'minlength': '8'}},
                {'id': 'confirm_pwd', 'tag_name': 'input', 'type': 'password',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'terms', 'tag_name': 'input', 'type': 'checkbox',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'signup_btn', 'tag_name': 'button', 'text_content': 'Create Account',
                 'is_interactive': True, 'attributes': {'type': 'submit'}}
            ]
        elif page_type == "checkout":
            return [
                {'id': 'card_number', 'tag_name': 'input', 'type': 'text',
                 'is_interactive': True, 'attributes': {'required': True, 'maxlength': '16'}},
                {'id': 'card_name', 'tag_name': 'input', 'type': 'text',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'expiry', 'tag_name': 'input', 'type': 'text',
                 'is_interactive': True, 'attributes': {'required': True, 'pattern': 'MM/YY'}},
                {'id': 'cvv', 'tag_name': 'input', 'type': 'text',
                 'is_interactive': True, 'attributes': {'required': True, 'maxlength': '3'}},
                {'id': 'billing_address', 'tag_name': 'textarea',
                 'is_interactive': True, 'attributes': {'required': True}},
                {'id': 'place_order', 'tag_name': 'button', 'text_content': 'Place Order',
                 'is_interactive': True, 'attributes': {'type': 'submit'}}
            ]
        else:
            return [
                {'id': 'search', 'tag_name': 'input', 'type': 'text',
                 'is_interactive': True, 'attributes': {'placeholder': 'Search...'}},
                {'id': 'menu_btn', 'tag_name': 'button', 'text_content': 'Menu',
                 'is_interactive': True, 'attributes': {}},
                {'id': 'cta_btn', 'tag_name': 'button', 'text_content': 'Get Started',
                 'is_interactive': True, 'attributes': {'class': 'primary'}}
            ]
    
    async def test_llm_generation(self, page_type: str, strategy: str):
        """Test LLM generation for a specific page type and strategy."""
        logger.info(f"\nTesting {strategy} generation for {page_type} page...")
        
        # Get mock elements
        elements = self.generate_mock_elements(page_type)
        
        # Generate prompt with quantum enhancements
        base_prompt = f"""
        Generate {strategy} test scenarios for a {page_type} page.
        
        Elements on the page:
        {json.dumps(elements, indent=2)}
        
        Create 3-5 test scenarios that thoroughly test the {page_type} functionality.
        
        Return ONLY a JSON array where each scenario has this structure:
        {{
            "title": "Clear descriptive title",
            "priority": "critical|high|medium|low",
            "steps": [
                {{
                    "action": "Type of action",
                    "target": "Element to interact with",
                    "data": "Test data if applicable",
                    "expected": "Expected result"
                }}
            ],
            "tags": ["relevant", "tags"]
        }}
        """
        
        # Apply enhancements
        if self.config.enable_chain_of_thought and strategy in ['security', 'edge_case']:
            base_prompt = self.prompt_engine._apply_chain_of_thought(base_prompt)
        
        if self.config.enable_meta_prompting:
            base_prompt = self.prompt_engine._apply_meta_prompting(base_prompt)
        
        # Add strategy-specific instructions
        if strategy == "happy_path":
            base_prompt += "\n\nFocus on successful user flows with valid data."
        elif strategy == "negative":
            base_prompt += "\n\nFocus on error cases, invalid data, and validation testing."
        elif strategy == "security":
            base_prompt += "\n\nFocus on security vulnerabilities, injection attacks, and authorization."
        
        try:
            # Call Gemini-2.5-pro
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert QA engineer. Generate comprehensive test scenarios in valid JSON format only."
                },
                {
                    "role": "user",
                    "content": base_prompt
                }
            ]
            
            logger.info(f"Calling {self.llm_model}...")
            response = query_llm(self.llm_provider, self.llm_model, messages)
            content = response.choices[0].message.content
            
            # Parse response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            scenarios = json.loads(content)
            
            logger.info(f"✓ Generated {len(scenarios)} {strategy} scenarios for {page_type}")
            
            # Display first scenario as example
            if scenarios:
                logger.info(f"\nExample scenario: {scenarios[0]['title']}")
                logger.info(f"Priority: {scenarios[0].get('priority', 'medium')}")
                logger.info(f"Steps: {len(scenarios[0].get('steps', []))}")
                
            return scenarios
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw response: {content[:200]}...")
            return []
        except Exception as e:
            logger.error(f"Error generating scenarios: {e}")
            return []

async def main():
    """Main test function."""
    logger.info("="*60)
    logger.info("QUANTUM ENHANCED UI TESTING - LLM INTEGRATION TEST")
    logger.info(f"Using Gemini-2.5-pro for test generation")
    logger.info("="*60)
    
    tester = SimplifiedQuantumTester()
    
    # Test combinations
    test_cases = [
        ("login", "happy_path"),
        ("login", "negative"),
        ("login", "security"),
        ("signup", "happy_path"),
        ("signup", "negative"),
        ("checkout", "security"),
        ("checkout", "negative"),
        ("generic", "happy_path")
    ]
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'llm_model': tester.llm_model,
        'test_cases': []
    }
    
    for page_type, strategy in test_cases:
        logger.info(f"\n{'='*40}")
        logger.info(f"Testing: {page_type} - {strategy}")
        logger.info(f"{'='*40}")
        
        scenarios = await tester.test_llm_generation(page_type, strategy)
        
        results['test_cases'].append({
            'page_type': page_type,
            'strategy': strategy,
            'scenarios_count': len(scenarios),
            'scenarios': scenarios,
            'success': len(scenarios) > 0
        })
        
        # Brief pause between API calls
        await asyncio.sleep(1)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    successful = sum(1 for tc in results['test_cases'] if tc['success'])
    total = len(results['test_cases'])
    
    logger.info(f"Total test cases: {total}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {total - successful}")
    
    total_scenarios = sum(tc['scenarios_count'] for tc in results['test_cases'])
    logger.info(f"Total scenarios generated: {total_scenarios}")
    
    # Save results
    output_file = f"quantum_llm_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nResults saved to: {output_file}")
    
    # Display sample scenario
    for tc in results['test_cases']:
        if tc['scenarios']:
            logger.info(f"\n{'='*40}")
            logger.info(f"Sample {tc['strategy']} scenario for {tc['page_type']}:")
            logger.info(json.dumps(tc['scenarios'][0], indent=2))
            break
    
    return results

if __name__ == "__main__":
    asyncio.run(main())