"""
Quick test of Quantum System with Gemini-2.5-pro
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys
import os
import time

# Setup paths and environment
sys.path.append(str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

# Imports
from quantum_enhanced_ui_testing_system import QuantumSystemConfig, QuantumPromptEngine
from llm import query_llm

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def test_gemini_integration():
    """Quick test of Gemini-2.5-pro integration."""
    
    # Mock elements for testing
    test_elements = [
        {'id': 'email', 'tag_name': 'input', 'type': 'email', 'required': True},
        {'id': 'password', 'tag_name': 'input', 'type': 'password', 'required': True},
        {'id': 'submit', 'tag_name': 'button', 'text_content': 'Login'}
    ]
    
    # Configure quantum system
    config = QuantumSystemConfig(
        enable_chain_of_thought=True,
        enable_meta_prompting=True
    )
    prompt_engine = QuantumPromptEngine(config)
    
    results = {
        'model': 'gemini-2.5-pro',
        'timestamp': datetime.now().isoformat(),
        'tests': []
    }
    
    # Test each strategy
    strategies = ['happy_path', 'negative', 'security']
    
    for strategy in strategies:
        logger.info(f"\n[Testing {strategy}]")
        
        # Create enhanced prompt
        prompt = f"""
        Generate {strategy} test scenarios for these UI elements:
        {json.dumps(test_elements, indent=2)}
        
        Return exactly 2 test scenarios as a JSON array.
        Each scenario must have: title, priority, and steps array.
        """
        
        # Apply quantum enhancements
        if strategy == 'security':
            prompt = prompt_engine._apply_chain_of_thought(prompt)
        
        try:
            start_time = time.time()
            
            # Call Gemini-2.5-pro
            response = query_llm("gemini", "gemini-2.5-pro", [
                {"role": "system", "content": "You are a QA expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ])
            
            elapsed = time.time() - start_time
            content = response.choices[0].message.content.strip()
            
            # Clean JSON
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            scenarios = json.loads(content)
            
            logger.info(f"✓ Generated {len(scenarios)} scenarios in {elapsed:.1f}s")
            
            # Show first scenario
            if scenarios:
                logger.info(f"  Example: {scenarios[0].get('title', 'N/A')}")
            
            results['tests'].append({
                'strategy': strategy,
                'success': True,
                'scenarios': len(scenarios),
                'time': elapsed,
                'sample': scenarios[0] if scenarios else None
            })
            
        except Exception as e:
            logger.error(f"✗ Failed: {str(e)[:100]}")
            results['tests'].append({
                'strategy': strategy,
                'success': False,
                'error': str(e)[:200]
            })
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    
    successful = sum(1 for t in results['tests'] if t.get('success'))
    total_scenarios = sum(t.get('scenarios', 0) for t in results['tests'])
    avg_time = sum(t.get('time', 0) for t in results['tests']) / len(results['tests'])
    
    logger.info(f"Model: gemini-2.5-pro")
    logger.info(f"Strategies tested: {len(results['tests'])}")
    logger.info(f"Successful: {successful}/{len(results['tests'])}")
    logger.info(f"Total scenarios: {total_scenarios}")
    logger.info(f"Average time: {avg_time:.1f}s")
    
    # Save results
    output_file = f"quantum_quick_test_{datetime.now().strftime('%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nResults saved to: {output_file}")
    
    # Display a sample scenario
    for test in results['tests']:
        if test.get('sample'):
            logger.info(f"\nSample {test['strategy']} scenario:")
            logger.info(json.dumps(test['sample'], indent=2))
            break
    
    return results

if __name__ == "__main__":
    print("Testing Quantum Enhanced System with Gemini-2.5-pro")
    print("="*50)
    asyncio.run(test_gemini_integration())