#!/usr/bin/env python3
"""
Script to run all examples and collect error metrics
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import re

# List of example files
EXAMPLES = [
    "basic_usage.py",
    "advanced_automation.py",
    "enhanced_ecommerce_research.py",
    "fixed_academic_research.py",
    "google_search_example.py",
    "react_orchestrator_demo.py",
    "real_world_academic_research.py",
    "real_world_ecommerce_research.py",
    "real_world_financial_data.py",
    "real_world_job_automation.py",
    "real_world_news_monitoring.py",
    "real_world_real_estate_research.py",
    "real_world_social_media_analysis.py",
    "real_world_travel_planning.py",
    "security_demo.py",
    "test_ai_browser_integration.py",
    "test_all_fixes.py",
    "test_browser_simple.py",
    "test_fixed_system.py",
    "test_llm_providers.py",
    "working_system_demo.py"
]

def extract_errors(output):
    """Extract error patterns from output"""
    errors = []
    
    # Common error patterns
    patterns = [
        r"KeyError: '([^']+)'",
        r"ERROR.*?: (.+)",
        r"CRITICAL.*?: (.+)",
        r"Traceback \(most recent call last\):",
        r"UnicodeEncodeError: (.+)",
        r"TypeError: (.+)",
        r"AttributeError: (.+)",
        r"ValueError: (.+)",
        r"ImportError: (.+)",
        r"ModuleNotFoundError: (.+)",
        r"Failed to (.+)",
        r"Error: (.+)",
        r"WARNING.*?: (.+)",
        r"EOFError: (.+)",
        r"TimeoutError: (.+)",
        r"ConnectionError: (.+)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                error_msg = match[0] if match else str(match)
            else:
                error_msg = match
            if error_msg and error_msg not in errors:
                errors.append(error_msg)
    
    return errors

def run_example(filename, timeout=30):
    """Run a single example file and capture output"""
    print(f"Testing {filename}...")
    
    examples_dir = Path(__file__).parent / "examples"
    file_path = examples_dir / filename
    
    if not file_path.exists():
        return {
            "file": filename,
            "status": "NOT_FOUND",
            "errors": [f"File not found: {file_path}"],
            "exit_code": -1
        }
    
    # Some files need input, provide default input
    input_data = ""
    if "academic" in filename or "ecommerce" in filename or "job" in filename:
        input_data = "1\n"  # Select first option
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    try:
        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            input=input_data,
            env=env,
            errors='replace'
        )
        
        combined_output = result.stdout + result.stderr
        errors = extract_errors(combined_output)
        
        # Check for specific common errors
        has_keyerror = "KeyError" in combined_output
        has_unicode_error = "UnicodeEncodeError" in combined_output or "charmap" in combined_output
        has_logging_error = "Logging error in Loguru Handler" in combined_output
        has_timeout = "timeout" in combined_output.lower()
        has_import_error = "ImportError" in combined_output or "ModuleNotFoundError" in combined_output
        
        return {
            "file": filename,
            "status": "SUCCESS" if result.returncode == 0 else "FAILED",
            "exit_code": result.returncode,
            "errors": errors,
            "error_types": {
                "keyerror": has_keyerror,
                "unicode_error": has_unicode_error,
                "logging_error": has_logging_error,
                "timeout": has_timeout,
                "import_error": has_import_error
            },
            "error_count": len(errors)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "file": filename,
            "status": "TIMEOUT",
            "errors": [f"Execution timeout after {timeout} seconds"],
            "exit_code": -2
        }
    except Exception as e:
        return {
            "file": filename,
            "status": "EXCEPTION",
            "errors": [str(e)],
            "exit_code": -3
        }

def main():
    """Run all examples and collect error metrics"""
    
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "examples_tested": [],
        "summary": {
            "total_files": len(EXAMPLES),
            "files_tested": 0,
            "files_with_errors": 0,
            "files_not_found": 0,
            "files_timeout": 0,
            "common_errors": {}
        }
    }
    
    # Test each example
    for example in EXAMPLES:
        print(f"\n{'='*50}")
        result = run_example(example)
        metrics["examples_tested"].append(result)
        
        # Update summary
        metrics["summary"]["files_tested"] += 1
        
        if result["status"] == "NOT_FOUND":
            metrics["summary"]["files_not_found"] += 1
        elif result["status"] == "TIMEOUT":
            metrics["summary"]["files_timeout"] += 1
        elif result.get("errors"):
            metrics["summary"]["files_with_errors"] += 1
        
        # Track common error types
        if "error_types" in result:
            for error_type, has_error in result["error_types"].items():
                if has_error:
                    if error_type not in metrics["summary"]["common_errors"]:
                        metrics["summary"]["common_errors"][error_type] = 0
                    metrics["summary"]["common_errors"][error_type] += 1
    
    # Save results
    output_file = Path(__file__).parent / "error_metrics.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*50}")
    print(f"Error metrics saved to: {output_file}")
    print(f"\nSummary:")
    print(f"  Total files: {metrics['summary']['total_files']}")
    print(f"  Files tested: {metrics['summary']['files_tested']}")
    print(f"  Files with errors: {metrics['summary']['files_with_errors']}")
    print(f"  Files not found: {metrics['summary']['files_not_found']}")
    print(f"  Files timeout: {metrics['summary']['files_timeout']}")
    print(f"\nCommon errors:")
    for error_type, count in metrics['summary']['common_errors'].items():
        print(f"  {error_type}: {count} files")

if __name__ == "__main__":
    main()