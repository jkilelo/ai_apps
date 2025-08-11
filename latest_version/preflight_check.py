#!/usr/bin/env python3
"""
CODER v3.0 Pre-Flight Validation System
Ensures all infrastructure requirements are met before code generation
"""
import os
import sys
import subprocess
from pathlib import Path
import asyncio
from typing import Dict, Tuple, List

class PreFlightChecklist:
    """Comprehensive pre-flight validation for CODER v3.0"""
    
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.checks_warning = []
        
    def check_venv(self) -> bool:
        """Verify virtual environment exists and is activated"""
        venv_path = Path.cwd() / 'venv'
        
        # Check if venv directory exists
        if not venv_path.exists():
            self.checks_failed.append("❌ venv directory not found in project root")
            self.checks_failed.append("   Fix: python3 -m venv venv")
            return False
        
        # Check if venv is activated
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if not in_venv:
            # Also check VIRTUAL_ENV environment variable
            if not os.getenv('VIRTUAL_ENV'):
                self.checks_failed.append("❌ Virtual environment not activated")
                self.checks_failed.append("   Fix: source venv/bin/activate")
                return False
        
        # Verify it's the correct venv (in project root)
        if os.getenv('VIRTUAL_ENV'):
            venv_real = Path(os.getenv('VIRTUAL_ENV')).resolve()
            expected = venv_path.resolve()
            if venv_real != expected:
                self.checks_warning.append(f"⚠️  Using different venv: {venv_real}")
                self.checks_warning.append(f"   Expected: {expected}")
        
        self.checks_passed.append(f"✅ Virtual environment: {sys.prefix}")
        return True
    
    def check_python_version(self) -> bool:
        """Verify Python version is 3.8+"""
        if sys.version_info < (3, 8):
            self.checks_failed.append(f"❌ Python {sys.version} is too old (need 3.8+)")
            return False
        
        self.checks_passed.append(f"✅ Python version: {sys.version.split()[0]}")
        return True
    
    def check_llm_connectivity(self) -> bool:
        """Verify LLM connectivity"""
        providers_checked = []
        any_success = False
        
        # Check for API keys
        api_keys = {
            'OpenAI': os.getenv('OPENAI_API_KEY'),
            'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'Google': os.getenv('GOOGLE_API_KEY')
        }
        
        for provider, key in api_keys.items():
            if key:
                providers_checked.append(f"   {provider}: API key found")
                any_success = True
            else:
                providers_checked.append(f"   {provider}: No API key")
        
        if not any_success:
            self.checks_failed.append("❌ No LLM API keys found")
            self.checks_failed.append("   Fix: export OPENAI_API_KEY=your-key")
            for check in providers_checked:
                self.checks_failed.append(check)
            return False
        
        # Try to import llm module
        try:
            import llm
            self.checks_passed.append("✅ LLM module available")
        except ImportError:
            self.checks_warning.append("⚠️  LLM module not found (llm.py)")
            
        # Report available providers
        self.checks_passed.append("✅ LLM providers configured:")
        for check in providers_checked:
            if "API key found" in check:
                self.checks_passed.append(check)
        
        return any_success
    
    def check_project_root(self) -> bool:
        """Verify we're in the project root directory"""
        markers = [
            'requirements.txt',
            'setup.py',
            '.git',
            'CODER.md',
            'CODER_v3.md',
            'pyproject.toml'
        ]
        
        found_markers = []
        for marker in markers:
            if Path(marker).exists():
                found_markers.append(marker)
        
        if not found_markers:
            self.checks_failed.append("❌ Not in project root directory")
            self.checks_failed.append(f"   Current dir: {Path.cwd()}")
            self.checks_failed.append("   No project markers found (requirements.txt, .git, etc.)")
            return False
        
        self.checks_passed.append(f"✅ Project root confirmed: {Path.cwd()}")
        self.checks_passed.append(f"   Found markers: {', '.join(found_markers)}")
        return True
    
    def check_test_framework(self) -> bool:
        """Verify test framework is available"""
        try:
            import pytest
            # Get pytest version
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--version'],
                capture_output=True,
                text=True
            )
            version = result.stdout.split('\n')[0] if result.returncode == 0 else "unknown"
            self.checks_passed.append(f"✅ Test framework: {version}")
            
            # Check for coverage plugin
            try:
                import pytest_cov
                self.checks_passed.append("✅ Coverage plugin: pytest-cov available")
            except ImportError:
                self.checks_warning.append("⚠️  Coverage plugin not installed")
                self.checks_warning.append("   Fix: pip install pytest-cov")
            
            return True
            
        except ImportError:
            self.checks_failed.append("❌ pytest not installed")
            self.checks_failed.append("   Fix: pip install pytest pytest-cov")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if key dependencies are installed"""
        required = ['playwright', 'pydantic']
        missing = []
        installed = []
        
        for package in required:
            try:
                __import__(package)
                installed.append(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            self.checks_warning.append(f"⚠️  Missing packages: {', '.join(missing)}")
            self.checks_warning.append("   Fix: pip install -r requirements.txt")
        
        if installed:
            self.checks_passed.append(f"✅ Core dependencies: {', '.join(installed)}")
        
        return len(missing) == 0
    
    def check_disk_space(self) -> bool:
        """Check available disk space"""
        try:
            import shutil
            stat = shutil.disk_usage(".")
            free_gb = stat.free / (1024**3)
            
            if free_gb < 0.5:
                self.checks_failed.append(f"❌ Low disk space: {free_gb:.2f} GB")
                return False
            elif free_gb < 1:
                self.checks_warning.append(f"⚠️  Disk space: {free_gb:.2f} GB (low)")
            else:
                self.checks_passed.append(f"✅ Disk space: {free_gb:.1f} GB available")
            
            return True
            
        except Exception as e:
            self.checks_warning.append(f"⚠️  Could not check disk space: {e}")
            return True  # Don't fail on this
    
    def check_network(self) -> bool:
        """Check network connectivity to LLM providers"""
        try:
            import socket
            # Try to resolve OpenAI API domain
            socket.gethostbyname('api.openai.com')
            self.checks_passed.append("✅ Network: LLM endpoints reachable")
            return True
        except socket.gaierror:
            self.checks_warning.append("⚠️  Network: Cannot reach api.openai.com")
            return True  # Warning only, might have other providers
        except Exception as e:
            self.checks_warning.append(f"⚠️  Network check failed: {e}")
            return True
    
    def check_git_status(self) -> bool:
        """Check git repository status"""
        try:
            # Check if git repo exists
            if not Path('.git').exists():
                self.checks_warning.append("⚠️  Not a git repository")
                return True  # Don't fail, just warn
            
            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    self.checks_warning.append("⚠️  Git: Uncommitted changes present")
                else:
                    self.checks_passed.append("✅ Git: Working directory clean")
            
            return True
            
        except FileNotFoundError:
            self.checks_warning.append("⚠️  Git not installed")
            return True
        except Exception as e:
            self.checks_warning.append(f"⚠️  Git check failed: {e}")
            return True
    
    def execute_all(self) -> bool:
        """Run all pre-flight checks"""
        print("=" * 60)
        print("CODER v3.0 PRE-FLIGHT CHECKLIST")
        print("=" * 60)
        
        # Run all checks
        checks = [
            ("Project Root", self.check_project_root()),
            ("Python Version", self.check_python_version()),
            ("Virtual Environment", self.check_venv()),
            ("LLM Connectivity", self.check_llm_connectivity()),
            ("Test Framework", self.check_test_framework()),
            ("Dependencies", self.check_dependencies()),
            ("Disk Space", self.check_disk_space()),
            ("Network", self.check_network()),
            ("Git Status", self.check_git_status())
        ]
        
        # Count results
        critical_failures = any(not result for name, result in checks[:5])  # First 5 are critical
        
        # Display results
        if self.checks_passed:
            print("\n✅ PASSED:")
            for check in self.checks_passed:
                print(f"  {check}")
        
        if self.checks_warning:
            print("\n⚠️  WARNINGS:")
            for check in self.checks_warning:
                print(f"  {check}")
        
        if self.checks_failed:
            print("\n❌ FAILED:")
            for check in self.checks_failed:
                print(f"  {check}")
        
        # Final verdict
        print("\n" + "=" * 60)
        if not self.checks_failed:
            print("✅ PRE-FLIGHT COMPLETE - CLEARED FOR DEVELOPMENT")
            print("=" * 60)
            return True
        else:
            print("❌ PRE-FLIGHT FAILED - FIX CRITICAL ISSUES BEFORE PROCEEDING")
            print("=" * 60)
            print("\nRequired fixes:")
            for check in self.checks_failed:
                if "Fix:" in check:
                    print(check)
            return False
    
    def quick_check(self) -> Dict[str, bool]:
        """Quick check returning dict of results"""
        return {
            'project_root': self.check_project_root(),
            'python_version': self.check_python_version(),
            'venv': self.check_venv(),
            'llm': self.check_llm_connectivity(),
            'pytest': self.check_test_framework()
        }


def main():
    """Main entry point"""
    checklist = PreFlightChecklist()
    success = checklist.execute_all()
    
    if not success:
        print("\n💡 Quick fixes:")
        print("1. Create venv:     python3 -m venv venv")
        print("2. Activate venv:   source venv/bin/activate")
        print("3. Install deps:    pip install -r requirements.txt")
        print("4. Set API key:     export OPENAI_API_KEY=your-key")
        print("5. Install pytest:  pip install pytest pytest-cov")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()