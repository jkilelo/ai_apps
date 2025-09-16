#!/usr/bin/env python3
"""
NEXUS Browser Import Verification Script
========================================
Verifies that all required modules can be imported successfully.
This ensures the environment is properly configured.
"""

import sys
from typing import List, Tuple


def verify_import(module_name: str) -> Tuple[bool, str]:
    """
    Verify that a module can be imported.
    
    Args:
        module_name: Name of the module to import
        
    Returns:
        Tuple of (success, message)
    """
    try:
        __import__(module_name)
        return True, f"[OK] {module_name}"
    except ImportError as e:
        return False, f"[FAIL] {module_name}: {str(e)}"
    except Exception as e:
        return False, f"[WARN] {module_name}: Unexpected error - {str(e)}"


def main():
    """Main verification function."""
    print("=" * 80)
    print("NEXUS Browser Environment Verification")
    print("=" * 80)
    print()
    
    # Core Python modules (should always work)
    print("[*] Verifying Core Python Modules...")
    core_modules = [
        "os",
        "sys",
        "json",
        "asyncio",
        "pathlib",
        "typing",
        "dataclasses",
        "collections",
        "datetime",
        "logging",
        "hashlib",
        "uuid",
        "time",
        "random",
        "math",
    ]
    
    core_success = True
    for module in core_modules:
        success, message = verify_import(module)
        if not success:
            core_success = False
        print(f"  {message}")
    
    print()
    
    # Third-party dependencies
    print("[*] Verifying Third-Party Dependencies...")
    dependencies = [
        # Web Framework
        "fastapi",
        "uvicorn",
        "websockets",
        "pydantic",
        
        # Browser Automation
        "playwright",
        
        # Async and Networking
        "aiohttp",
        "aiofiles",
        "httpx",
        "requests",
        
        # Configuration
        "yaml",
        "dotenv",
        
        # Logging
        "structlog",
        "rich",
        "pythonjsonlogger",  # Correct import name
        
        # Testing
        "pytest",
        "pytest_asyncio",
        "pytest_cov",
        
        # Code Quality
        "black",
        "mypy",
        "flake8",
        
        # CLI
        "typer",
        "click",
        
        # File Operations
        "watchdog",
        
        # Utilities
        "dateutil",
        "pytz",
        
        # Performance
        "orjson",
        "ujson",
        "msgpack",
        
        # Data Validation
        "marshmallow",
        
        # Security
        "cryptography",
    ]
    
    dep_success = True
    failed_deps = []
    for module in dependencies:
        success, message = verify_import(module)
        if not success:
            dep_success = False
            failed_deps.append(module)
        print(f"  {message}")
    
    print()
    
    # Optional dependencies (may not be installed)
    print("[*] Verifying Optional Dependencies...")
    optional = [
        # Quantum Computing
        ("qiskit", "Quantum computing framework"),
        ("pennylane", "Quantum machine learning"),
        ("cirq", "Google quantum computing"),
        
        # AI/ML
        ("openai", "OpenAI API"),
        ("anthropic", "Anthropic Claude API"),
        ("google.generativeai", "Google Gemini API"),
        
        # Scientific Computing
        ("numpy", "Numerical computing"),
        ("scipy", "Scientific computing"),
        ("sklearn", "Machine learning"),
    ]
    
    optional_installed = []
    optional_missing = []
    for module, description in optional:
        success, message = verify_import(module)
        if success:
            optional_installed.append((module, description))
        else:
            optional_missing.append((module, description))
        print(f"  {message} - {description}")
    
    print()
    
    # NEXUS Browser modules
    print("[*] Verifying NEXUS Browser Modules...")
    nexus_modules = [
        "nexus",
        "quantum",
        "mcp_neural",
        "hologram",
        "evolution",
        "consciousness",
        "nexus_progress_tracker",
        "nexus_task_executor",
        "logging_config",
    ]
    
    nexus_success = True
    nexus_failed = []
    for module in nexus_modules:
        success, message = verify_import(module)
        if not success:
            nexus_success = False
            nexus_failed.append(module)
        print(f"  {message}")
    
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    # Summary
    if core_success:
        print("[SUCCESS] All core Python modules verified")
    else:
        print("[ERROR] Some core Python modules failed (this should not happen!)")
    
    if dep_success:
        print("[SUCCESS] All required dependencies installed")
    else:
        print(f"[ERROR] Missing dependencies: {', '.join(failed_deps)}")
        print("   Run: pip install -r requirements-core.txt")
    
    if optional_installed:
        print(f"[SUCCESS] Optional dependencies installed: {len(optional_installed)}")
        for module, desc in optional_installed:
            print(f"   - {module}: {desc}")
    
    if optional_missing:
        print(f"[INFO] Optional dependencies not installed: {len(optional_missing)}")
        for module, desc in optional_missing:
            print(f"   - {module}: {desc}")
    
    if nexus_success:
        print("[SUCCESS] All NEXUS Browser modules found")
    else:
        print(f"[WARNING] Missing NEXUS modules: {', '.join(nexus_failed)}")
        print("   These may need to be implemented or fixed")
    
    print()
    
    # Python version check
    print(f"[*] Python Version: {sys.version}")
    if sys.version_info >= (3, 11):
        print("[SUCCESS] Python 3.11+ requirement satisfied")
    else:
        print("[ERROR] Python 3.11+ required, please upgrade")
    
    print()
    print("=" * 80)
    
    # Overall status
    if core_success and dep_success and nexus_success and sys.version_info >= (3, 11):
        print("[SUCCESS] ENVIRONMENT VERIFICATION SUCCESSFUL!")
        print("   Your NEXUS Browser environment is properly configured.")
        return 0
    else:
        print("[WARNING] ENVIRONMENT VERIFICATION INCOMPLETE")
        print("   Please address the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())