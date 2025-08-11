#!/usr/bin/env python3
"""
Pre-flight checks for CODER Agent
Run this to verify your environment is properly configured
"""

import sys
import os
import asyncio
from pathlib import Path
import subprocess

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coder_agent.core.engine_helpers import EngineHelpers
from coder_agent.config.settings import load_config, create_example_config


async def run_preflight_checks():
    """Run comprehensive pre-flight checks"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║               CODER Agent Pre-Flight Checks                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    checks_passed = []
    checks_failed = []
    
    # Check 1: Virtual Environment
    print("🔍 Checking virtual environment...")
    venv_check = await EngineHelpers.check_virtual_environment()
    if venv_check.passed:
        print(f"   ✅ {venv_check.message}")
        checks_passed.append("Virtual Environment")
    else:
        print(f"   ❌ {venv_check.message}")
        checks_failed.append("Virtual Environment")
        print("   💡 Fix: Create and activate a virtual environment:")
        print("      python -m venv venv")
        print("      source venv/bin/activate  # Linux/Mac")
        print("      venv\\Scripts\\activate     # Windows")
    
    # Check 2: Python Version
    print("\n🔍 Checking Python version...")
    python_version = sys.version_info
    if python_version >= (3, 9):
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        checks_passed.append("Python Version")
    else:
        print(f"   ❌ Python {python_version.major}.{python_version.minor} (need 3.9+)")
        checks_failed.append("Python Version")
    
    # Check 3: Required Tools
    print("\n🔍 Checking required tools...")
    tools_check = await EngineHelpers.check_required_tools()
    if tools_check.passed:
        print(f"   ✅ {tools_check.message}")
        checks_passed.append("Required Tools")
    else:
        print(f"   ❌ {tools_check.message}")
        checks_failed.append("Required Tools")
        for tool in tools_check.details.get("missing", []):
            print(f"   💡 Install {tool}")
    
    # Check 4: LLM Configuration
    print("\n🔍 Checking LLM configuration...")
    llm_check = await EngineHelpers.check_llm_connection()
    if llm_check.passed:
        print(f"   ✅ {llm_check.message}")
        checks_passed.append("LLM Configuration")
    else:
        print(f"   ❌ {llm_check.message}")
        checks_failed.append("LLM Configuration")
        print("   💡 Fix: Set one of these environment variables:")
        print("      export OPENAI_API_KEY='your-key'")
        print("      export ANTHROPIC_API_KEY='your-key'")
    
    # Check 5: Dependencies
    print("\n🔍 Checking Python dependencies...")
    try:
        import pydantic
        import structlog
        import click
        print(f"   ✅ Core dependencies installed")
        checks_passed.append("Dependencies")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e.name}")
        checks_failed.append("Dependencies")
        print("   💡 Fix: pip install -r requirements.txt")
    
    # Check 6: Configuration
    print("\n🔍 Checking configuration...")
    try:
        config = load_config()
        print(f"   ✅ Configuration loaded")
        checks_passed.append("Configuration")
    except Exception as e:
        print(f"   ⚠️  Using default configuration: {e}")
        print("   💡 Create a config file for customization:")
        print("      python -m coder_agent.preflight --create-config")
    
    # Check 7: Disk Space
    print("\n🔍 Checking disk space...")
    import shutil
    stat = shutil.disk_usage(".")
    free_gb = stat.free / (1024 ** 3)
    if free_gb > 1:
        print(f"   ✅ {free_gb:.1f} GB free disk space")
        checks_passed.append("Disk Space")
    else:
        print(f"   ⚠️  Low disk space: {free_gb:.1f} GB")
    
    # Summary
    print("\n" + "=" * 60)
    print("PRE-FLIGHT CHECK SUMMARY")
    print("=" * 60)
    
    total_checks = len(checks_passed) + len(checks_failed)
    print(f"✅ Passed: {len(checks_passed)}/{total_checks}")
    
    if checks_failed:
        print(f"❌ Failed: {len(checks_failed)}/{total_checks}")
        print("\nFailed checks:")
        for check in checks_failed:
            print(f"  • {check}")
        print("\n⚠️  Please fix the issues above before running CODER Agent")
        return False
    else:
        print("\n🚀 All checks passed! CODER Agent is ready to use.")
        print("\nExample usage:")
        print('  python -m coder_agent "Fix the login bug"')
        print('  python -m coder_agent "Add tests for User model" -p ./src')
        return True


def main():
    """Main entry point for preflight checks"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CODER Agent Pre-flight Checks")
    parser.add_argument("--create-config", action="store_true", 
                       help="Create example configuration file")
    args = parser.parse_args()
    
    if args.create_config:
        create_example_config()
        return
    
    # Run checks
    success = asyncio.run(run_preflight_checks())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()