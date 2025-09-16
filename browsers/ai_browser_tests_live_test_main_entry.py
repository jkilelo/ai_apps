#!/usr/bin/env python3
"""
Quick Live Test for AI Browser Main Entry Point

This script tests the main.py entry point with a real task using actual API keys.
It's a simpler test focused on validating the complete system works end-to-end.
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import os

# Test configuration
TEST_TASKS = [
    {
        "name": "Google Search Test",
        "command": [
            "python", "src/main.py",
            "--task", "Search for 'Python programming tutorials' and click on the first result",
            "--url", "https://www.google.com",
            "--headless", "false",
            "--max-steps", "10",
            "--debug"
        ],
        "expected": "completed"
    },
    {
        "name": "Wikipedia Navigation Test",  
        "command": [
            "python", "src/main.py",
            "--task", "Go to Wikipedia and search for 'Artificial Intelligence'",
            "--url", "https://www.wikipedia.org",
            "--headless", "false",
            "--max-steps", "10"
        ],
        "expected": "completed"
    },
    {
        "name": "GitHub Repository Test",
        "command": [
            "python", "src/main.py",
            "--task", "Navigate to GitHub and search for 'playwright python'",
            "--url", "https://github.com",
            "--headless", "false",
            "--max-steps", "10"
        ],
        "expected": "completed"
    }
]

STEALTH_TEST = {
    "name": "Stealth Capability Test",
    "command": [
        "python", "src/main.py",
        "--test-stealth"
    ],
    "expected": "passed"
}


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60 + "\n")


def run_command(command, name):
    """Run a command and capture output"""
    print(f"Running: {name}")
    print(f"Command: {' '.join(command)}\n")
    
    try:
        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            cwd=Path(__file__).parent.parent.parent  # Run from project root
        )
        
        # Print output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        # Check return code
        if result.returncode == 0:
            print(f"\n✅ {name}: SUCCESS (exit code: 0)")
            return True
        else:
            print(f"\n❌ {name}: FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⏱️ {name}: TIMEOUT (exceeded 120 seconds)")
        return False
    except Exception as e:
        print(f"\n❌ {name}: ERROR - {e}")
        return False


def check_environment():
    """Check that the environment is properly set up"""
    print_header("ENVIRONMENT CHECK")
    
    checks = {
        "Python": sys.version,
        "Working Directory": os.getcwd(),
        "Main Script": "✓" if Path("src/main.py").exists() else "✗ Missing",
        "Config File": "✓" if Path("configs/production.json").exists() else "✗ Missing",
        ".env File": "✓" if Path(".env").exists() else "✗ Missing"
    }
    
    # Check API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    api_keys = {
        "OPENAI_API_KEY": "✓" if os.getenv("OPENAI_API_KEY") else "✗ Missing",
        "ANTHROPIC_API_KEY": "✓" if os.getenv("ANTHROPIC_API_KEY") else "✗ Missing",
        "GOOGLE_API_KEY": "✓" if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") else "✗ Missing"
    }
    
    print("System Information:")
    for key, value in checks.items():
        print(f"  {key}: {value}")
    
    print("\nAPI Keys:")
    for key, value in api_keys.items():
        print(f"  {key}: {value}")
    
    # Check if all required components exist
    all_good = all("✓" in str(v) for v in checks.values() if "✗" not in str(v))
    all_good = all_good and all("✓" in v for v in api_keys.values())
    
    if all_good:
        print("\n✅ Environment check passed!")
        return True
    else:
        print("\n⚠️ Some environment checks failed. Tests may not work properly.")
        return False


def main():
    """Main test runner"""
    print_header("AI BROWSER v2.0.0 - LIVE SYSTEM TEST")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not check_environment():
        print("\n⚠️ Please fix environment issues before running tests.")
        return 1
    
    # Track results
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Run stealth test first
    print_header("STEALTH CAPABILITY TEST")
    if run_command(STEALTH_TEST["command"], STEALTH_TEST["name"]):
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["total"] += 1
    
    # Run task tests
    print_header("TASK EXECUTION TESTS")
    for test in TEST_TASKS:
        if run_command(test["command"], test["name"]):
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1
        
        # Small delay between tests
        print("\nWaiting 3 seconds before next test...")
        import time
        time.sleep(3)
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    
    if results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED! The AI Browser is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {results['failed']} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())