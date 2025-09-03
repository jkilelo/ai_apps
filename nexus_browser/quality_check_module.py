#!/usr/bin/env python3
"""Quality check for a specific module."""

import sys
from pathlib import Path
from quality_check import verify_module

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quality_check_module.py <module_file>")
        sys.exit(1)
    
    module_path = Path(sys.argv[1])
    if not module_path.exists():
        print(f"[ERROR] File not found: {module_path}")
        sys.exit(1)
    
    result = verify_module(module_path)
    
    if not result["passed"]:
        print(f"\n[QUALITY] {module_path.name} FAILED quality checks")
        sys.exit(1)
    else:
        print(f"\n[QUALITY] {module_path.name} meets ALL constitutional requirements")
        print("[QUALITY] Ready for production")