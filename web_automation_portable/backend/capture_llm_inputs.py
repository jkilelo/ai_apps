"""
Capture and save all LLM inputs for redundancy analysis
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global list to capture all LLM inputs
LLM_INPUTS = []
LLM_CALL_COUNTER = 0

# Monkey-patch the LLM call to capture inputs
original_call_llm = None

async def capturing_call_llm(messages: List[Dict[str, str]], **kwargs) -> str:
    """Wrapper to capture LLM inputs before calling"""
    global LLM_CALL_COUNTER, LLM_INPUTS
    
    LLM_CALL_COUNTER += 1
    
    # Capture the input
    llm_input = {
        "call_number": LLM_CALL_COUNTER,
        "timestamp": datetime.now().isoformat(),
        "messages": messages,
        "kwargs": kwargs,
        "total_chars": sum(len(msg.get("content", "")) for msg in messages)
    }
    
    LLM_INPUTS.append(llm_input)
    
    # Save immediately to file
    input_file = Path(f"llm_input_{LLM_CALL_COUNTER:02d}.json")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(llm_input, f, indent=2, ensure_ascii=False)
    
    print(f"[CAPTURE] LLM Call #{LLM_CALL_COUNTER}: {llm_input['total_chars']} chars")
    print(f"[CAPTURE] Saved to {input_file}")
    
    # Call the original LLM function
    return await original_call_llm(messages, **kwargs)

# Import and patch BEFORE importing the test generation module
from llm import call_default_llm
original_call_llm = call_default_llm

# Replace the import in the llm module
import llm
llm.call_default_llm = capturing_call_llm

# Now import the test generation module (it will use our patched version)
from test_generation_with_llm import generate_tests

async def main():
    """Run test generation with input capture"""
    
    print("="*60)
    print("LLM INPUT CAPTURE FOR REDUNDANCY ANALYSIS")
    print("="*60)
    
    # Clean up old capture files
    for old_file in Path(".").glob("llm_input_*.json"):
        old_file.unlink()
        print(f"[CLEANUP] Removed old file: {old_file}")
    
    # Test parameters
    url = "https://example.com"
    categories = ["functional", "accessibility", "validation"]
    max_scenarios = 3
    
    print(f"\n[START] Generating tests for: {url}")
    print(f"[START] Categories: {categories}")
    
    try:
        # Run test generation
        result = await generate_tests(
            url=url,
            categories=categories,
            max_scenarios=max_scenarios
        )
        
        print(f"\n[COMPLETE] Test generation finished")
        print(f"[COMPLETE] Total LLM calls: {LLM_CALL_COUNTER}")
        
        # Save summary of all inputs
        summary = {
            "total_calls": LLM_CALL_COUNTER,
            "total_chars": sum(inp["total_chars"] for inp in LLM_INPUTS),
            "calls": []
        }
        
        for inp in LLM_INPUTS:
            # Extract key info from messages
            system_msg = next((m for m in inp["messages"] if m.get("role") == "system"), None)
            user_msg = next((m for m in inp["messages"] if m.get("role") == "user"), None)
            
            call_summary = {
                "call_number": inp["call_number"],
                "total_chars": inp["total_chars"],
                "system_prompt_length": len(system_msg.get("content", "")) if system_msg else 0,
                "user_prompt_length": len(user_msg.get("content", "")) if user_msg else 0,
                "system_prompt_preview": (system_msg.get("content", "")[:200] + "...") if system_msg else None,
                "user_prompt_preview": (user_msg.get("content", "")[:200] + "...") if user_msg else None
            }
            summary["calls"].append(call_summary)
        
        # Save summary
        with open("llm_inputs_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n[ANALYSIS] Summary saved to llm_inputs_summary.json")
        print(f"[ANALYSIS] Total characters sent to LLM: {summary['total_chars']:,}")
        print(f"[ANALYSIS] Average chars per call: {summary['total_chars'] // LLM_CALL_COUNTER:,}")
        
        # Analyze redundancy
        print("\n" + "="*60)
        print("REDUNDANCY ANALYSIS")
        print("="*60)
        
        # Check for duplicate content across calls
        all_contents = []
        for i, inp in enumerate(LLM_INPUTS, 1):
            for msg in inp["messages"]:
                content = msg.get("content", "")
                all_contents.append((i, msg.get("role"), content))
        
        # Find common substrings
        print("\n[REDUNDANCY] Checking for repeated content patterns...")
        
        # Look for page analysis repetition
        page_analysis_count = sum(1 for _, _, content in all_contents if "https://example.com" in content)
        print(f"  - URL 'https://example.com' appears in {page_analysis_count} messages")
        
        element_count = sum(1 for _, _, content in all_contents if "total_elements" in content or "interactive_elements" in content)
        print(f"  - Element counts mentioned in {element_count} messages")
        
        test_category_count = sum(1 for _, _, content in all_contents if "functional" in content and "accessibility" in content)
        print(f"  - Test categories listed in {test_category_count} messages")
        
        # Check for large prompts
        print("\n[SIZE ANALYSIS] Large prompts (>5000 chars):")
        for inp in LLM_INPUTS:
            if inp["total_chars"] > 5000:
                print(f"  - Call #{inp['call_number']}: {inp['total_chars']:,} chars")
        
        # Check for similar prompts
        print("\n[SIMILARITY] Checking for similar prompt structures...")
        system_prompts = []
        for inp in LLM_INPUTS:
            system_msg = next((m for m in inp["messages"] if m.get("role") == "system"), None)
            if system_msg:
                system_prompts.append((inp["call_number"], system_msg.get("content", "")))
        
        # Compare system prompts
        for i, (call1, prompt1) in enumerate(system_prompts):
            for call2, prompt2 in system_prompts[i+1:]:
                # Check if prompts share significant content
                if len(prompt1) > 100 and len(prompt2) > 100:
                    # Simple check: do they share the first 100 chars?
                    if prompt1[:100] == prompt2[:100]:
                        print(f"  - Calls #{call1} and #{call2} have similar system prompts")
        
        print("\n[COMPLETE] Analysis complete. Check llm_input_*.json files for full details")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Test generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(main())