#!/usr/bin/env python3
"""
Claude Code Setup for UI Testing Automation
===========================================
Project-specific Claude Code environment configuration
"""

import json
import os
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
PARENT_DIR = PROJECT_ROOT.parent
VENV_PATH = PARENT_DIR.parent.parent / '.venv'

def setup_claude_environment():
    """Setup Claude Code environment for ui_testing_automation project"""
    
    print("=" * 60)
    print("Claude Code Setup - UI Testing Automation Project")
    print("=" * 60)
    print(f"Project: {PROJECT_ROOT}")
    print()
    
    # Check if running from correct directory
    if PROJECT_ROOT.name != "ui_testing_automation":
        print("[ERROR] This script must be run from ui_testing_automation directory")
        return False
    
    # Create .claude directory if it doesn't exist
    claude_dir = PROJECT_ROOT / '.claude'
    claude_dir.mkdir(exist_ok=True)
    
    # Check for required files
    print("Checking project structure...")
    required_files = {
        'CLAUDE.md': PROJECT_ROOT / 'CLAUDE.md',
        '.mcp.json': PROJECT_ROOT / '.mcp.json',
        'settings.json': claude_dir / 'settings.json',
        'prompt_templates.json': claude_dir / 'prompt_templates.json',
        'automation_scripts.py': claude_dir / 'automation_scripts.py'
    }
    
    for name, path in required_files.items():
        if path.exists():
            print(f"  [OK] {name} exists")
        else:
            print(f"  [MISSING] {name}")
    
    # Check Python modules
    print("\nChecking Python modules...")
    sys.path.insert(0, str(PROJECT_ROOT))
    
    modules_status = {}
    try:
        import browser
        modules_status['browser.py'] = "OK - Stealth browser loaded"
    except ImportError as e:
        modules_status['browser.py'] = f"ERROR - {e}"
    
    try:
        import llm
        modules_status['llm.py'] = "OK - LLM module loaded"
    except ImportError as e:
        modules_status['llm.py'] = f"ERROR - {e}"
    
    try:
        import ui_testing_automation.base.prompts as prompts
        modules_status['prompts.py'] = "OK - Prompt strategies loaded"
    except ImportError as e:
        modules_status['prompts.py'] = f"ERROR - {e}"
    
    try:
        import browser_with_llm
        modules_status['browser_with_llm.py'] = "OK - Integration layer loaded"
    except ImportError as e:
        modules_status['browser_with_llm.py'] = f"ERROR - {e}"
    
    for module, status in modules_status.items():
        print(f"  {module}: {status}")
    
    # Check environment variables
    print("\nChecking environment variables...")
    env_path = PARENT_DIR / '.env'
    if env_path.exists():
        print(f"  [OK] .env file found at: {env_path}")
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        api_keys = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
        }
        
        for key, value in api_keys.items():
            if value:
                print(f"  [OK] {key} configured (length: {len(value)})")
            else:
                print(f"  [WARNING] {key} not configured")
    else:
        print(f"  [ERROR] .env file not found at: {env_path}")
    
    # Show how to use Claude Code in this project
    print("\n" + "=" * 60)
    print("HOW TO USE CLAUDE CODE WITH THIS PROJECT")
    print("=" * 60)
    print()
    print("1. Start Claude Code in THIS directory:")
    print(f"   cd {PROJECT_ROOT}")
    print("   claude code")
    print()
    print("2. Claude will automatically load CLAUDE.md for context")
    print()
    print("3. Use project-specific commands:")
    print("   # Run tests")
    print("   python test_integration_complete.py")
    print()
    print("   # Check quality")
    print("   python .claude/automation_scripts.py quality <file>")
    print()
    print("   # Run workflow")
    print("   python .claude/automation_scripts.py workflow new_feature")
    print()
    print("4. Key architectural rules:")
    print("   - browser.py: Independent, no LLM")
    print("   - llm.py: Single source of truth")
    print("   - browser_with_llm.py: ONLY integration point")
    print("   - All AI modules use browser_with_llm.py")
    print()
    print("5. When Claude asks about the project:")
    print("   - Focus is ONLY ui_testing_automation")
    print("   - Ignore parent ai_apps directory")
    print("   - Use existing patterns in this project")
    print()
    
    return True

def quick_test():
    """Quick test of the environment"""
    print("=" * 60)
    print("QUICK ENVIRONMENT TEST")
    print("=" * 60)
    
    # Test imports
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from browser import UltimateStealthBrowser, StealthConfig
        from llm import call_default_llm
        from ui_testing_automation.base.prompts import PromptEngine
        from browser_with_llm import BrowserWithLLM
        
        print("[SUCCESS] All core modules import correctly!")
        print()
        print("Architecture verified:")
        print("  Layer 0: browser.py, llm.py, prompts.py")
        print("  Layer 1: browser_with_llm.py")
        print("  Layer 2: Domain modules (extractors, generators)")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print()
        print("Make sure you're running from ui_testing_automation directory")
        print("and that the virtual environment is activated:")
        print("  ..\\..\\..\\venv\\Scripts\\activate")
        
        return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        quick_test()
    else:
        setup_claude_environment()
        print("\n" + "=" * 60)
        print("Run 'python claude_setup.py test' to verify imports")
        print("=" * 60)

if __name__ == "__main__":
    main()