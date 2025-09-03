#!/usr/bin/env python3
"""
Quick Demo: V2 LLM-Native System in Action
===========================================
This demonstrates the V2 system working with real AI.
"""

import asyncio
import os
import sys
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')


async def quick_demo():
    """Quick demonstration of V2 with real LLM"""
    
    print("=" * 80)
    print("V2 LLM-NATIVE QUICK DEMO")
    print("=" * 80)
    
    # Direct LLM test
    print("\n[1] Testing direct LLM call...")
    from llm_client import call_default_llm
    
    response = await call_default_llm(
        [{"role": "user", "content": "Generate a test case name for login functionality"}],
        temperature=0.5,
        max_tokens=50
    )
    
    print(f"AI Response: {response}")
    
    print("\n" + "=" * 80)
    print("[SUCCESS] V2 is working with real LLM!")
    print("The system is truly LLM-native - no fallbacks.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(quick_demo())