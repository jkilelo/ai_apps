#!/usr/bin/env python3
"""
Quick error collection from running examples
"""

import json
from datetime import datetime
import subprocess
import re

def quick_test_example(filename):
    """Quick test of a single example with short timeout"""
    print(f"Quick testing {filename}...")
    
    # Run with very short timeout and capture stderr
    cmd = f'cd examples && echo "1" | python {filename} 2>&1'
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,  # Very short timeout
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        
        # Extract key errors
        errors = {
            "keyerror_timestamp": "KeyError: '\"timestamp\"'" in output,
            "keyerror_request_id": "KeyError: 'request_id'" in output,
            "unicode_error": "UnicodeEncodeError" in output or "charmap" in output,
            "logging_error": "Logging error in Loguru Handler" in output,
            "eof_error": "EOFError" in output,
            "google_scholar_blocked": "Loading... The system can't perform" in output,
            "element_not_found": "Failed to click element" in output,
            "no_papers_found": "No papers found" in output,
            "browser_agent_error": "BrowserAgent.__init__() got an unexpected keyword argument" in output,
            "timeout_error": "timeout" in output.lower(),
            "import_error": "ImportError" in output or "ModuleNotFoundError" in output
        }
        
        # Count total errors
        error_count = sum(1 for v in errors.values() if v)
        
        return {
            "file": filename,
            "errors_found": error_count,
            "error_types": errors,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "file": filename,
            "errors_found": 1,
            "error_types": {"timeout": True},
            "exit_code": -1
        }
    except Exception as e:
        return {
            "file": filename,
            "errors_found": 1,
            "error_types": {"exception": str(e)},
            "exit_code": -2
        }

# Quick test key examples
key_examples = [
    "basic_usage.py",
    "test_ai_browser_integration.py",
    "real_world_academic_research.py",
    "enhanced_ecommerce_research.py",
    "google_search_example.py"
]

metrics = {
    "timestamp": datetime.now().isoformat(),
    "collection_method": "quick_test",
    "examples_tested": [],
    "summary": {
        "total_files_tested": 0,
        "files_with_errors": 0,
        "common_errors": {
            "keyerror_timestamp": 0,
            "keyerror_request_id": 0,
            "unicode_error": 0,
            "logging_error": 0,
            "google_scholar_blocked": 0,
            "element_not_found": 0,
            "no_papers_found": 0
        }
    }
}

for example in key_examples:
    result = quick_test_example(example)
    metrics["examples_tested"].append(result)
    metrics["summary"]["total_files_tested"] += 1
    
    if result["errors_found"] > 0:
        metrics["summary"]["files_with_errors"] += 1
    
    # Update common error counts
    if "error_types" in result:
        for error_type, has_error in result["error_types"].items():
            if has_error and error_type in metrics["summary"]["common_errors"]:
                metrics["summary"]["common_errors"][error_type] += 1

# Save results
with open("error_metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)

print("\n" + "="*50)
print("Error metrics saved to error_metrics.json")
print(f"\nSummary:")
print(f"  Files tested: {metrics['summary']['total_files_tested']}")
print(f"  Files with errors: {metrics['summary']['files_with_errors']}")
print(f"\nCommon errors found:")
for error_type, count in metrics['summary']['common_errors'].items():
    if count > 0:
        print(f"  {error_type}: {count} files")