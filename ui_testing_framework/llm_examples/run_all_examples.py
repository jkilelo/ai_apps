#!/usr/bin/env python3
"""
Run All LLM Examples
===================

This script runs all QA workflow examples in sequence or individually.
Perfect for demonstrating the full capabilities of the LLM framework.

Usage:
- Run all examples: python run_all_examples.py
- Run specific example: python run_all_examples.py --example 01
- List available examples: python run_all_examples.py --list
"""

import sys
from pathlib import Path
import argparse
import time
import subprocess
import json
from datetime import datetime

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm


class ExampleRunner:
    """Manages and executes all LLM examples."""
    
    def __init__(self):
        self.examples_dir = Path(__file__).parent
        self.examples = {
            "01": {
                "name": "Basic Test Generation",
                "file": "01_basic_test_generation.py",
                "description": "Fundamental test case generation for common QA scenarios",
                "duration": "2-3 minutes"
            },
            "02": {
                "name": "Daily QA Workflows", 
                "file": "02_daily_qa_workflows.py",
                "description": "Real-world QA workflows: standup, bug triage, sprint planning",
                "duration": "3-4 minutes"
            },
            "03": {
                "name": "Advanced Strategies",
                "file": "03_advanced_strategies.py", 
                "description": "All 21 master prompt strategies with QA examples",
                "duration": "4-5 minutes"
            },
            "04": {
                "name": "Automated Test Code Generation",
                "file": "04_automated_test_code_generation.py",
                "description": "Generate executable test code for multiple frameworks",
                "duration": "3-4 minutes"
            },
            "05": {
                "name": "Batch Processing",
                "file": "05_batch_processing.py",
                "description": "Efficient batch processing with parallel execution",
                "duration": "4-5 minutes"
            },
            "06": {
                "name": "Production Utilities",
                "file": "06_production_utilities.py",
                "description": "Production-ready QA utilities and management tools",
                "duration": "2-3 minutes"
            }
        }
        
    def list_examples(self):
        """List all available examples."""
        print("[LIST] AVAILABLE LLM EXAMPLES")
        print("=" * 40)
        
        for key, example in self.examples.items():
            print(f"{key}. {example['name']}")
            print(f"   File: {example['file']}")
            print(f"   Description: {example['description']}")
            print(f"   Duration: {example['duration']}")
            print()
    
    def run_example(self, example_key: str):
        """Run a specific example."""
        if example_key not in self.examples:
            print(f"❌ Example '{example_key}' not found!")
            return False
            
        example = self.examples[example_key]
        example_file = self.examples_dir / example['file']
        
        if not example_file.exists():
            print(f"❌ Example file not found: {example_file}")
            return False
        
        print(f"[RUN] RUNNING EXAMPLE {example_key}: {example['name']}")
        print("=" * 60)
        print(f"Description: {example['description']}")
        print(f"Estimated duration: {example['duration']}")
        print()
        
        start_time = time.time()
        
        try:
            # Get Python executable path
            python_exe = sys.executable
            
            # Run the example
            result = subprocess.run(
                [python_exe, str(example_file)],
                capture_output=True,
                text=True,
                cwd=str(self.examples_dir)
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print("[OK] EXAMPLE COMPLETED SUCCESSFULLY!")
                print(f"[TIME] Execution time: {execution_time:.1f} seconds")
                print()
                print("OUTPUT:")
                print("-" * 40)
                print(result.stdout)
                if result.stderr:
                    print("WARNINGS/INFO:")
                    print("-" * 40)
                    print(result.stderr)
                return True
            else:
                print("[FAIL] EXAMPLE FAILED!")
                print(f"[TIME] Execution time: {execution_time:.1f} seconds")
                print("ERROR OUTPUT:")
                print("-" * 40)
                print(result.stderr)
                print("STDOUT:")
                print("-" * 40)
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"[ERROR] Error running example: {e}")
            return False
    
    def run_all_examples(self, skip_on_error: bool = False):
        """Run all examples in sequence."""
        print("[ALL] RUNNING ALL LLM EXAMPLES")
        print("===============================")
        print("This will run all 6 examples demonstrating the full LLM framework.")
        print("Total estimated time: 18-24 minutes")
        print()
        
        results = {}
        total_start_time = time.time()
        
        for key in sorted(self.examples.keys()):
            print(f"\n{'='*80}")
            success = self.run_example(key)
            results[key] = {
                "name": self.examples[key]['name'],
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            
            if not success and skip_on_error:
                print(f"[SKIP] Skipping remaining examples due to failure in {key}")
                break
            
            # Brief pause between examples
            if key != list(self.examples.keys())[-1]:
                print("[PAUSE] Pausing 5 seconds before next example...")
                time.sleep(5)
        
        total_time = time.time() - total_start_time
        
        # Generate summary
        self.generate_execution_summary(results, total_time)
        
        return results
    
    def generate_execution_summary(self, results: dict, total_time: float):
        """Generate execution summary with LLM insights."""
        print(f"\n{'='*80}")
        print("[SUMMARY] EXECUTION SUMMARY")
        print("=" * 27)
        
        successful = sum(1 for r in results.values() if r['success'])
        total = len(results)
        
        print(f"Examples completed: {successful}/{total}")
        print(f"Success rate: {(successful/total)*100:.1f}%")
        print(f"Total execution time: {total_time/60:.1f} minutes")
        print()
        
        print("Example Results:")
        for key, result in results.items():
            status = "[PASS]" if result['success'] else "[FAIL]"
            print(f"  {key}. {result['name']}: {status}")
        
        # Generate insights using LLM
        results_summary = json.dumps(results, indent=2)
        
        messages = [{
            "role": "user",
            "content": f"""
            Analyze these LLM example execution results:
            
            {results_summary}
            
            Total execution time: {total_time/60:.1f} minutes
            Success rate: {(successful/total)*100:.1f}%
            
            Provide:
            1. Overall assessment of the framework demonstration
            2. Key capabilities showcased
            3. Performance insights
            4. Recommendations for QA teams
            5. Next steps for implementation
            
            Keep it concise but insightful for QA managers evaluating this framework.
            """
        }]
        
        try:
            response = query_llm(messages)
            print("\n[AI] LLM INSIGHTS:")
            print("=" * 17)
            print(response.content)
        except Exception as e:
            print(f"Note: Could not generate LLM insights: {e}")
        
        # Save results to file
        summary_file = self.examples_dir / f"execution_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump({
                "execution_date": datetime.now().isoformat(),
                "total_examples": total,
                "successful_examples": successful,
                "success_rate": (successful/total)*100,
                "total_execution_time_minutes": total_time/60,
                "results": results
            }, f, indent=2)
        
        print(f"\n[FILE] Summary saved to: {summary_file}")
    
    def interactive_mode(self):
        """Run examples in interactive mode."""
        print("[INTERACTIVE] INTERACTIVE MODE")
        print("=" * 30)
        print("Choose examples to run or run all at once.")
        print()
        
        while True:
            self.list_examples()
            print("Commands:")
            print("  Enter example number (01-06) to run specific example")
            print("  'all' - Run all examples")
            print("  'quit' - Exit interactive mode")
            print()
            
            choice = input("Your choice: ").strip().lower()
            
            if choice == 'quit':
                print("[QUIT] Goodbye!")
                break
            elif choice == 'all':
                self.run_all_examples()
            elif choice in self.examples:
                self.run_example(choice)
            else:
                print(f"[ERROR] Invalid choice: {choice}")
                print()


def main():
    """Main entry point for the example runner."""
    parser = argparse.ArgumentParser(
        description="Run LLM QA Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_examples.py                    # Interactive mode
  python run_all_examples.py --all              # Run all examples
  python run_all_examples.py --example 01       # Run specific example
  python run_all_examples.py --list             # List all examples
        """
    )
    
    parser.add_argument('--example', help='Run specific example (01-06)')
    parser.add_argument('--all', action='store_true', help='Run all examples')
    parser.add_argument('--list', action='store_true', help='List available examples')
    parser.add_argument('--skip-on-error', action='store_true', 
                       help='Skip remaining examples if one fails')
    
    args = parser.parse_args()
    
    runner = ExampleRunner()
    
    if args.list:
        runner.list_examples()
    elif args.example:
        runner.run_example(args.example.zfill(2))
    elif args.all:
        runner.run_all_examples(skip_on_error=args.skip_on_error)
    else:
        runner.interactive_mode()


if __name__ == "__main__":
    main()