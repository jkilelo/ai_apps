#!/usr/bin/env python3
"""
V2 LLM-Native System - Setup Script
====================================
This script sets up the V2 system on any machine.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("V2 LLM-NATIVE SYSTEM - AUTOMATED SETUP")
    print("=" * 70)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 70)


def check_python_version():
    """Ensure Python 3.7+"""
    if sys.version_info < (3, 7):
        print("[ERROR] Python 3.7 or higher is required!")
        print(f"You have Python {sys.version}")
        sys.exit(1)
    print("[OK] Python version check passed")


def create_virtual_env():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("[INFO] Virtual environment already exists")
        return venv_path
    
    print("[INFO] Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("[OK] Virtual environment created")
    return venv_path


def get_pip_command():
    """Get the pip command for the virtual environment"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")


def get_python_command():
    """Get the python command for the virtual environment"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")


def install_requirements():
    """Install required packages"""
    pip_cmd = get_pip_command()
    
    print("[INFO] Upgrading pip...")
    subprocess.run([str(pip_cmd), "install", "--upgrade", "pip"], check=True)
    
    print("[INFO] Installing requirements...")
    subprocess.run([str(pip_cmd), "install", "-r", "requirements.txt"], check=True)
    print("[OK] All packages installed")


def install_playwright_browsers():
    """Install Playwright browsers"""
    python_cmd = get_python_command()
    
    print("[INFO] Installing Playwright browsers...")
    subprocess.run([str(python_cmd), "-m", "playwright", "install", "chromium"], check=True)
    print("[OK] Playwright browsers installed")


def setup_env_file():
    """Setup .env file from template"""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("[INFO] .env file already exists")
        response = input("Do you want to update it? (y/n): ").lower()
        if response != 'y':
            return
    
    if not env_template.exists():
        print("[WARNING] .env.template not found")
        return
    
    print("\n" + "=" * 70)
    print("IMPORTANT: API Keys Required")
    print("=" * 70)
    print("You need at least ONE of these API keys:")
    print("1. OpenAI API Key (https://platform.openai.com/api-keys)")
    print("2. Anthropic API Key (https://console.anthropic.com/)")
    print("3. Google API Key (https://makersuite.google.com/app/apikey)")
    print("=" * 70)
    
    # Copy template to .env
    import shutil
    shutil.copy2(env_template, env_file)
    
    print("\n[ACTION REQUIRED] Edit .env file and add your API keys")
    print(f"File location: {env_file.absolute()}")
    
    if platform.system() == "Windows":
        subprocess.run(["notepad", str(env_file)], check=False)
    else:
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.run([editor, str(env_file)], check=False)


def test_installation():
    """Test if the installation works"""
    python_cmd = get_python_command()
    
    print("\n[INFO] Testing installation...")
    
    test_script = """
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

async def test():
    try:
        # Test imports
        from test_automation_framework.ai_test_generator import verify_llm_system
        print("[OK] Imports successful")
        
        # Test LLM connection
        from llm_client import call_default_llm
        response = await call_default_llm(
            [{"role": "user", "content": "Say 'Setup successful'"}],
            temperature=0.1,
            max_tokens=20
        )
        print(f"[OK] LLM Response: {response}")
        return True
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

success = asyncio.run(test())
sys.exit(0 if success else 1)
"""
    
    # Write test script
    test_file = Path("_test_setup.py")
    test_file.write_text(test_script)
    
    try:
        result = subprocess.run([str(python_cmd), str(test_file)], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("[SUCCESS] Installation test passed!")
        else:
            print("[WARNING] Installation test failed. Check your API keys in .env")
            print(result.stderr)
    finally:
        test_file.unlink(missing_ok=True)


def print_next_steps():
    """Print next steps for the user"""
    python_cmd = get_python_command()
    
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print(f"1. Activate virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print(f"\n2. Run an example:")
    print(f"   {python_cmd} workplace_agents_v2/examples/quick_demo.py")
    
    print(f"\n3. Or test with your own script:")
    print(f"   {python_cmd} your_test_script.py")
    
    print("\nFor more examples, see workplace_agents_v2/examples/")
    print("=" * 70)


def main():
    """Main setup process"""
    try:
        print_banner()
        check_python_version()
        create_virtual_env()
        install_requirements()
        install_playwright_browsers()
        setup_env_file()
        
        # Ask if user wants to test
        response = input("\nDo you want to test the installation? (y/n): ").lower()
        if response == 'y':
            test_installation()
        
        print_next_steps()
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Setup failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()