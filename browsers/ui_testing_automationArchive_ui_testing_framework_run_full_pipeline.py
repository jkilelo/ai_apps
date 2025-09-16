#!/usr/bin/env python3
"""
FULL PIPELINE EXECUTION SCRIPT
==============================
Runs all steps from running_steps_enhanced.txt sequentially.
"""

import os
import sys
import time
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

class PipelineRunner:
    """Runs the complete UI Testing Framework pipeline"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_python = self.project_root.parent / ".venv" / "Scripts" / "python.exe"
        self.results = {}
        self.start_time = datetime.now()
        
    def run_command(self, cmd, timeout=60):
        """Run a command and return success status"""
        print(f"\n[RUNNING] {cmd}")
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                print("[OK] Command succeeded")
                return True, result.stdout
            else:
                print(f"[FAIL] Command failed with code {result.returncode}")
                print(f"Error: {result.stderr}")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            print(f"[FAIL] Command timed out after {timeout} seconds")
            return False, "Timeout"
        except Exception as e:
            print(f"[FAIL] Command error: {e}")
            return False, str(e)
    
    def step_0_check_foundation(self):
        """Step 0: Check foundation modules"""
        print("\n" + "="*60)
        print("STEP 0: CHECKING FOUNDATION MODULES")
        print("="*60)
        
        # Check if modules exist
        modules = ['browser.py', 'llm.py', 'prompts.py', 'utils.py']
        all_exist = True
        
        for module in modules:
            module_path = self.project_root / module
            if module_path.exists():
                print(f"[OK] {module} exists")
                
                # Try to run a basic import test with proper path
                module_name = module[:-3]
                test_cmd = f'"{self.venv_python}" -c "import sys; sys.path.insert(0, r\'{self.project_root}\'); import {module_name}; print(\'Import OK\')"'
                success, output = self.run_command(test_cmd, timeout=10)
                if not success:
                    print(f"  Import failed: {output[:200]}")
                    all_exist = False
            else:
                print(f"[FAIL] {module} not found")
                all_exist = False
        
        self.results['step_0'] = all_exist
        return all_exist
    
    def step_1_check_html(self):
        """Step 1: Check HTML file"""
        print("\n" + "="*60)
        print("STEP 1: CHECKING HTML FILE")
        print("="*60)
        
        html_path = self.project_root / "index.html"
        if html_path.exists():
            print("[OK] index.html exists")
            
            # Check content
            content = html_path.read_text()
            checks = [
                ('form' in content, "Contains form element"),
                ('id="username"' in content or "id='username'" in content, "Form has id='username'"),
                ('<input' in content, "Has input field"),
                ('submit' in content.lower(), "Has submit button")
            ]
            
            all_pass = True
            for check, desc in checks:
                if check:
                    print(f"[OK] {desc}")
                else:
                    print(f"[FAIL] {desc}")
                    all_pass = False
            
            self.results['step_1'] = all_pass
            return all_pass
        else:
            print("[FAIL] index.html not found")
            self.results['step_1'] = False
            return False
    
    def step_2_start_server(self):
        """Step 2: Start web server"""
        print("\n" + "="*60)
        print("STEP 2: STARTING WEB SERVER")
        print("="*60)
        
        # Check if server is already running
        import requests
        try:
            response = requests.get('http://localhost:8000', timeout=2)
            print("[OK] Server already running on port 8000")
            self.results['step_2'] = True
            return True
        except:
            print("[INFO] Server not running, attempting to start...")
        
        # Try to start server
        server_script = self.project_root / "simple_server.py"
        if not server_script.exists():
            print("[FAIL] simple_server.py not found")
            self.results['step_2'] = False
            return False
        
        # Start server in background (note: this won't work perfectly in subprocess)
        print("[INFO] Please start the server manually in another terminal:")
        print(f'       cd "{self.project_root}"')
        print(f'       "{self.venv_python}" simple_server.py')
        print("\n[WARN] Skipping server start (requires manual action)")
        self.results['step_2'] = 'manual'
        return True
    
    def step_3_extract_no_llm(self):
        """Step 3: Extract elements without LLM"""
        print("\n" + "="*60)
        print("STEP 3: ELEMENT EXTRACTION WITHOUT LLM")
        print("="*60)
        print("[INFO] Browser automation can be slow - allowing 2 minutes")
        
        cli_script = self.project_root / "element_extractor_no_llm_cli.py"
        if not cli_script.exists():
            print("[FAIL] element_extractor_no_llm_cli.py not found")
            self.results['step_3'] = False
            return False
        
        # Delete old output if exists
        output_file = self.project_root / "localhost_8000_no_llm_elements.json"
        if output_file.exists():
            print(f"[INFO] Removing old output: {output_file.name}")
            output_file.unlink()
        
        # Run extraction with longer timeout
        cmd = f'"{self.venv_python}" "{cli_script}" --url http://localhost:8000 --verbose'
        print("[INFO] Starting browser extraction (may take up to 2 minutes)...")
        success, output = self.run_command(cmd, timeout=120)
        
        # Check if output was created
        if output_file.exists():
            print(f"[OK] Output created: {output_file.name}")
            
            # Validate JSON
            import json
            try:
                with open(output_file) as f:
                    data = json.load(f)
                print(f"[OK] Valid JSON with {len(data.get('elements', []))} elements")
                self.results['step_3'] = True
                return True
            except Exception as e:
                print(f"[FAIL] Invalid JSON: {e}")
                self.results['step_3'] = False
                return False
        else:
            print("[FAIL] Output file not created")
            self.results['step_3'] = False
            return False
    
    def step_4_extract_with_llm(self):
        """Step 4: Extract elements with LLM enhancement"""
        print("\n" + "="*60)
        print("STEP 4: ELEMENT EXTRACTION WITH LLM")
        print("="*60)
        print("[CRITICAL] LLM calls can take 30-90 seconds each - allowing 5 minutes")
        
        cli_script = self.project_root / "element_extractor_with_llm_cli.py"
        input_file = self.project_root / "localhost_8000_no_llm_elements.json"
        
        if not cli_script.exists():
            print("[FAIL] element_extractor_with_llm_cli.py not found")
            self.results['step_4'] = False
            return False
        
        if not input_file.exists():
            print("[FAIL] Input from Step 3 not found")
            self.results['step_4'] = False
            return False
        
        # Delete old output if exists
        output_file = self.project_root / "localhost_8000_with_llm_elements.json"
        if output_file.exists():
            print(f"[INFO] Removing old output: {output_file.name}")
            output_file.unlink()
        
        # Run extraction with much longer timeout for LLM
        cmd = f'"{self.venv_python}" "{cli_script}" --input "{input_file}" --verbose'
        print("[INFO] Starting LLM enhancement (may take up to 5 minutes)...")
        print("[INFO] Watch for periodic 'Calling LLM...' messages")
        success, output = self.run_command(cmd, timeout=300)
        
        # Check if output was created
        if output_file.exists():
            print(f"[OK] Output created: {output_file.name}")
            
            # Validate JSON
            import json
            try:
                with open(output_file) as f:
                    data = json.load(f)
                print(f"[OK] Valid JSON with page_type: {data.get('page_type', 'unknown')}")
                self.results['step_4'] = True
                return True
            except Exception as e:
                print(f"[FAIL] Invalid JSON: {e}")
                self.results['step_4'] = False
                return False
        else:
            print("[FAIL] Output file not created")
            self.results['step_4'] = False
            return False
    
    def step_5_generate_tests(self):
        """Step 5: Generate tests with LLM"""
        print("\n" + "="*60)
        print("STEP 5: TEST GENERATION WITH LLM")
        print("="*60)
        print("[CRITICAL] Test generation makes 10-20+ LLM calls - allowing 10 minutes!")
        
        cli_script = self.project_root / "test_generation_with_llm_cli.py"
        input_file = self.project_root / "localhost_8000_with_llm_elements.json"
        
        if not cli_script.exists():
            print("[FAIL] test_generation_with_llm_cli.py not found")
            self.results['step_5'] = False
            return False
        
        if not input_file.exists():
            print("[FAIL] Input from Step 4 not found")
            self.results['step_5'] = False
            return False
        
        # Delete old output if exists
        output_file = self.project_root / "localhost_8000_with_llm_tests.json"
        if output_file.exists():
            print(f"[INFO] Removing old output: {output_file.name}")
            output_file.unlink()
        
        # Run generation with VERY long timeout for multiple LLM calls
        cmd = f'"{self.venv_python}" "{cli_script}" --input "{input_file}" --verbose'
        print("[INFO] Starting test generation (may take up to 10 minutes)...")
        print("[INFO] Expected: 2 min for analysis, 6 min for scenarios, 2 min for code gen")
        print("[INFO] DO NOT INTERRUPT if you see periodic LLM activity!")
        success, output = self.run_command(cmd, timeout=600)
        
        # Check if output was created
        if output_file.exists():
            print(f"[OK] Output created: {output_file.name}")
            
            # Validate JSON
            import json
            try:
                with open(output_file) as f:
                    data = json.load(f)
                scenarios = len(data.get('test_scenarios', []))
                categories = data.get('categories_covered', [])
                print(f"[OK] Valid JSON with {scenarios} test scenarios")
                print(f"[OK] Categories: {', '.join(categories)}")
                self.results['step_5'] = True
                return True
            except Exception as e:
                print(f"[FAIL] Invalid JSON: {e}")
                self.results['step_5'] = False
                return False
        else:
            print("[FAIL] Output file not created")
            self.results['step_5'] = False
            return False
    
    def run_full_pipeline(self):
        """Run the complete pipeline"""
        print("\n" + "="*60)
        print("FULL PIPELINE EXECUTION")
        print("="*60)
        print(f"Project: {self.project_root}")
        print(f"Python: {self.venv_python}")
        print(f"Started: {self.start_time.isoformat()}")
        
        # Run all steps
        steps = [
            (self.step_0_check_foundation, "Foundation Modules"),
            (self.step_1_check_html, "HTML File"),
            (self.step_2_start_server, "Web Server"),
            (self.step_3_extract_no_llm, "Extract without LLM"),
            (self.step_4_extract_with_llm, "Extract with LLM"),
            (self.step_5_generate_tests, "Generate Tests")
        ]
        
        for step_func, step_name in steps:
            if not step_func():
                print(f"\n[WARN] Step failed: {step_name}")
                # Continue anyway to see what works
        
        # Summary
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*60)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*60)
        
        for step, result in self.results.items():
            status = "[PASS]" if result == True else "[MANUAL]" if result == 'manual' else "[FAIL]"
            print(f"{step}: {status}")
        
        print(f"\nTotal time: {duration:.2f} seconds")
        
        # Check overall success
        passed = sum(1 for r in self.results.values() if r == True)
        total = len(self.results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Success rate: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("\n[SUCCESS] Pipeline execution completed successfully!")
        else:
            print("\n[WARNING] Pipeline execution had issues, review the results above")
        
        return success_rate >= 80


def main():
    """Main entry point"""
    runner = PipelineRunner()
    success = runner.run_full_pipeline()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()