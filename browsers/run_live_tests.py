#!/usr/bin/env python3
"""
Live Test Runner for AI Browser v2.0.0

This script provides a menu-driven interface to run various live tests
of the AI Browser system with real API connections and browser automation.

Usage:
    python run_live_tests.py              # Interactive menu
    python run_live_tests.py --all        # Run all tests
    python run_live_tests.py --quick      # Run quick validation
    python run_live_tests.py --full       # Run comprehensive tests
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
from typing import List, Dict, Any

# Fix Windows Unicode handling
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class TestRunner:
    """Interactive test runner for AI Browser"""
    
    def __init__(self):
        self.tests = {
            "1": {
                "name": "Quick Environment Check",
                "description": "Verify environment setup and API keys",
                "command": "python -c \"from dotenv import load_dotenv; import os; load_dotenv(); print('Environment loaded successfully'); print(f'OpenAI: {bool(os.getenv(\\\"OPENAI_API_KEY\\\"))}'); print(f'Anthropic: {bool(os.getenv(\\\"ANTHROPIC_API_KEY\\\"))}'); print(f'Google: {bool(os.getenv(\\\"GOOGLE_API_KEY\\\"))}')\""
            },
            "2": {
                "name": "Test Main Entry Point",
                "description": "Run main.py with simple tasks",
                "command": "python tests/live/test_main_entry.py"
            },
            "3": {
                "name": "Comprehensive System Test",
                "description": "Test all layers with real APIs",
                "command": "python tests/live/test_live_system.py"
            },
            "4": {
                "name": "Stealth Capability Test",
                "description": "Test bot detection evasion",
                "command": "python src/main.py --test-stealth"
            },
            "5": {
                "name": "Google Search Task",
                "description": "Execute real search task on Google",
                "command": "python src/main.py --task \"Search for 'OpenAI GPT-4' on Google\" --url https://www.google.com --headless false --max-steps 5"
            },
            "6": {
                "name": "Wikipedia Task",
                "description": "Navigate and search on Wikipedia",
                "command": "python src/main.py --task \"Go to Wikipedia and search for Machine Learning\" --url https://www.wikipedia.org --headless false --max-steps 5"
            },
            "7": {
                "name": "LLM Connection Test",
                "description": "Test all LLM provider connections",
                "command": "python test_live_llm.py"
            },
            "8": {
                "name": "Memory System Test",
                "description": "Test database connections (SQLite, Qdrant, FalkorDB)",
                "command": "python -c \"import asyncio; from src.memory.memory_manager import MemoryManager; async def test(): m = MemoryManager(); await m.initialize(); print('Memory system initialized successfully'); await m.close(); asyncio.run(test())\""
            },
            "9": {
                "name": "Plugin System Test",
                "description": "Test plugin loading and execution",
                "command": "python -c \"import asyncio; from src.extensibility.plugin_manager import PluginManager; async def test(): p = PluginManager(); await p.discover_plugins(); print(f'Successfully loaded {len(p.plugins)} plugins'); asyncio.run(test())\""
            },
            "10": {
                "name": "Production Config Test",
                "description": "Run with production configuration",
                "command": "python src/main.py --task \"Navigate to example.com\" --url https://example.com --config configs/production.json --headless true --max-steps 3"
            }
        }
        
        self.test_suites = {
            "quick": ["1", "4", "7"],
            "full": ["1", "2", "3", "4", "7", "8", "9"],
            "browser": ["4", "5", "6"],
            "api": ["1", "7", "8"],
            "all": list(self.tests.keys())
        }
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f" {title} ".center(70, "="))
        print("="*70 + "\n")
    
    def print_menu(self):
        """Display interactive menu"""
        self.print_header("AI BROWSER v2.0.0 - LIVE TEST RUNNER")
        
        print("Individual Tests:")
        for key, test in self.tests.items():
            print(f"  [{key}] {test['name']}")
            print(f"      {test['description']}")
        
        print("\nTest Suites:")
        print("  [Q] Quick Validation (environment + basic tests)")
        print("  [F] Full Test Suite (comprehensive testing)")
        print("  [B] Browser Tests (automation and stealth)")
        print("  [A] API Tests (LLM and database connections)")
        print("  [ALL] Run All Tests")
        
        print("\n  [0] Exit")
        print("\n" + "-"*70)
    
    def run_test(self, test_id: str) -> bool:
        """Run a single test"""
        if test_id not in self.tests:
            print(f"❌ Invalid test ID: {test_id}")
            return False
        
        test = self.tests[test_id]
        self.print_header(test["name"])
        print(f"Description: {test['description']}")
        print(f"Command: {test['command']}\n")
        
        try:
            # Run the test command
            result = subprocess.run(
                test["command"],
                shell=True,
                capture_output=False,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"\n[PASS] {test['name']}: SUCCESS")
                return True
            else:
                print(f"\n[FAIL] {test['name']}: FAILED (exit code: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"\n[TIMEOUT] {test['name']}: TIMEOUT")
            return False
        except KeyboardInterrupt:
            print(f"\n[INTERRUPTED] {test['name']}: INTERRUPTED")
            return False
        except Exception as e:
            print(f"\n[ERROR] {test['name']}: ERROR - {e}")
            return False
    
    def run_suite(self, suite_name: str) -> Dict[str, int]:
        """Run a test suite"""
        if suite_name not in self.test_suites:
            print(f"❌ Invalid suite: {suite_name}")
            return {"passed": 0, "failed": 0}
        
        test_ids = self.test_suites[suite_name]
        self.print_header(f"Running {suite_name.upper()} Test Suite")
        
        results = {"passed": 0, "failed": 0, "total": len(test_ids)}
        
        for test_id in test_ids:
            if self.run_test(test_id):
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            # Small delay between tests
            if test_id != test_ids[-1]:
                print("\nWaiting 2 seconds before next test...")
                import time
                time.sleep(2)
        
        return results
    
    def print_summary(self, results: Dict[str, int]):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        print(f"Total Tests: {results['total']}")
        print(f"Passed: {results['passed']} [SUCCESS]")
        print(f"Failed: {results['failed']} [FAILED]")
        
        if results['total'] > 0:
            success_rate = (results['passed'] / results['total']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if results['failed'] == 0:
                print("\n[SUCCESS] ALL TESTS PASSED! System is fully operational.")
            else:
                print(f"\n[WARNING] {results['failed']} test(s) failed. Review the output above.")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        while True:
            self.print_menu()
            
            try:
                choice = input("Select test to run: ").strip().upper()
                
                if choice == "0":
                    print("\nExiting test runner. Goodbye!")
                    break
                elif choice == "Q":
                    results = self.run_suite("quick")
                    self.print_summary(results)
                elif choice == "F":
                    results = self.run_suite("full")
                    self.print_summary(results)
                elif choice == "B":
                    results = self.run_suite("browser")
                    self.print_summary(results)
                elif choice == "A":
                    results = self.run_suite("api")
                    self.print_summary(results)
                elif choice == "ALL":
                    results = self.run_suite("all")
                    self.print_summary(results)
                elif choice in self.tests:
                    self.run_test(choice)
                else:
                    print(f"\n[ERROR] Invalid choice: {choice}")
                
                if choice != "0":
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"\n[ERROR] Error: {e}")
                input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Live Test Runner for AI Browser v2.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick validation tests"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run comprehensive test suite"
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Run browser automation tests"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run API connection tests"
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Run specific test by ID (1-10)"
    )
    
    args = parser.parse_args()
    runner = TestRunner()
    
    # Check Python version
    if sys.version_info < (3, 11):
        print(f"[WARNING] Python {sys.version_info.major}.{sys.version_info.minor} detected.")
        print("This project requires Python 3.11 or higher for optimal performance.")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Run based on arguments
    if args.all:
        results = runner.run_suite("all")
        runner.print_summary(results)
    elif args.quick:
        results = runner.run_suite("quick")
        runner.print_summary(results)
    elif args.full:
        results = runner.run_suite("full")
        runner.print_summary(results)
    elif args.browser:
        results = runner.run_suite("browser")
        runner.print_summary(results)
    elif args.api:
        results = runner.run_suite("api")
        runner.print_summary(results)
    elif args.test:
        runner.run_test(args.test)
    else:
        # Interactive mode
        runner.interactive_mode()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())