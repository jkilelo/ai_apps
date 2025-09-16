#!/usr/bin/env python3
"""
COMPREHENSIVE PIPELINE AUDIT SCRIPT
===================================
Automatically audits the entire UI Testing Framework pipeline.
Run this to verify all modules and steps are working correctly.
"""

import os
import sys
import json
import subprocess
import importlib
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

class PipelineAuditor:
    """Comprehensive auditor for UI Testing Framework pipeline"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.parent_dir = self.project_root.parent
        self.venv_python = self.parent_dir / ".venv" / "Scripts" / "python.exe"
        self.audit_results = {}
        self.total_checks = 0
        self.passed_checks = 0
        
    def check(self, name: str, condition: bool) -> bool:
        """Record a check result"""
        self.total_checks += 1
        if condition:
            self.passed_checks += 1
            print(f"[OK] {name}")
        else:
            print(f"[FAIL] {name}")
        self.audit_results[name] = condition
        return condition
    
    def run_command(self, cmd: str) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def audit_step_0_foundation(self) -> bool:
        """Audit foundation modules: browser.py, llm.py, prompts.py"""
        print("\n" + "="*60)
        print("STEP 0: FOUNDATION MODULES AUDIT")
        print("="*60)
        
        all_pass = True
        
        # Check file existence
        browser_exists = self.check(
            "browser.py exists", 
            (self.project_root / "browser.py").exists()
        )
        llm_exists = self.check(
            "llm.py exists", 
            (self.project_root / "llm.py").exists()
        )
        prompts_exists = self.check(
            "prompts.py exists", 
            (self.project_root / "prompts.py").exists()
        )
        utils_exists = self.check(
            "utils.py exists", 
            (self.project_root / "utils.py").exists()
        )
        
        if not (browser_exists and llm_exists and prompts_exists):
            return False
        
        # Test browser.py
        print("\n--- Browser.py Audits ---")
        try:
            import browser
            self.check("browser.py imports successfully", True)
            self.check("UltimateStealthBrowser exists", hasattr(browser, 'UltimateStealthBrowser'))
            self.check("StealthConfig exists", hasattr(browser, 'StealthConfig'))
        except Exception as e:
            self.check("browser.py imports successfully", False)
            all_pass = False
        
        # Test llm.py
        print("\n--- LLM.py Audits ---")
        try:
            import llm
            self.check("llm.py imports successfully", True)
            self.check("call_default_llm exists", hasattr(llm, 'call_default_llm'))
            self.check("LLMResponse exists", hasattr(llm, 'LLMResponse'))
            
            # Check LLM models config
            llm_models_exists = self.check(
                "llm_models.json exists",
                (self.project_root / "llm_models.json").exists()
            )
            
            # Test simple LLM call
            try:
                response = llm.call_default_llm([{'role': 'user', 'content': 'Say OK'}])
                self.check("LLM call works", True)
                self.check("LLM returns LLMResponse", hasattr(response, 'content'))
            except Exception as e:
                self.check("LLM call works", False)
                print(f"  LLM Error: {e}")
        except Exception as e:
            self.check("llm.py imports successfully", False)
            all_pass = False
        
        # Test prompts.py
        print("\n--- Prompts.py Audits ---")
        try:
            import prompts
            self.check("prompts.py imports successfully", True)
            self.check("PromptEngine exists", hasattr(prompts, 'PromptEngine'))
            self.check("PromptStrategy exists", hasattr(prompts, 'PromptStrategy'))
            
            # Count strategies
            if hasattr(prompts, 'PromptStrategy'):
                strategies = list(prompts.PromptStrategy)
                self.check(f"Has 21 strategies", len(strategies) == 21)
            else:
                self.check("Has 21 strategies", False)
        except Exception as e:
            self.check("prompts.py imports successfully", False)
            all_pass = False
        
        # Test utils.py
        print("\n--- Utils.py Audits ---")
        if utils_exists:
            try:
                import utils
                self.check("utils.py imports successfully", True)
                self.check("format_url_for_filename exists", hasattr(utils, 'format_url_for_filename'))
                
                # Test URL formatting
                if hasattr(utils, 'format_url_for_filename'):
                    result = utils.format_url_for_filename('http://localhost:8000')
                    self.check("URL formatting works correctly", result == 'localhost_8000')
            except Exception as e:
                self.check("utils.py imports successfully", False)
                all_pass = False
        
        return all_pass
    
    def audit_step_1_html(self) -> bool:
        """Audit HTML file creation"""
        print("\n" + "="*60)
        print("STEP 1: HTML FILE AUDIT")
        print("="*60)
        
        html_path = self.project_root / "index.html"
        html_exists = self.check("index.html exists", html_path.exists())
        
        if not html_exists:
            return False
        
        # Check HTML content
        try:
            content = html_path.read_text()
            self.check("Contains form element", '<form' in content)
            self.check("Form has id='username'", 'id="username"' in content or "id='username'" in content)
            self.check("Has input field", '<input' in content)
            self.check("Has submit button", 'type="submit"' in content or '<button' in content)
            self.check("Has label element", '<label' in content)
            return True
        except Exception as e:
            print(f"  Error reading HTML: {e}")
            return False
    
    def audit_step_2_server(self) -> bool:
        """Audit web server"""
        print("\n" + "="*60)
        print("STEP 2: WEB SERVER AUDIT")
        print("="*60)
        
        server_path = self.project_root / "simple_server.py"
        server_exists = self.check("simple_server.py exists", server_path.exists())
        
        if not server_exists:
            return False
        
        # Check if server is accessible
        try:
            import requests
            response = requests.get('http://localhost:8000', timeout=5)
            self.check("Server responds on port 8000", response.status_code == 200)
            self.check("Server serves HTML content", 'form' in response.text.lower())
            return True
        except Exception as e:
            self.check("Server responds on port 8000", False)
            print(f"  Server not running or not accessible: {e}")
            print("  Please start the server with: python simple_server.py")
            return False
    
    def audit_step_3_no_llm(self) -> bool:
        """Audit element extraction without LLM"""
        print("\n" + "="*60)
        print("STEP 3: ELEMENT EXTRACTION WITHOUT LLM")
        print("="*60)
        
        # Check module files
        module_exists = self.check(
            "elements_extractor_no_llm.py exists",
            (self.project_root / "elements_extractor_no_llm.py").exists()
        )
        cli_exists = self.check(
            "element_extractor_no_llm_cli.py exists",
            (self.project_root / "element_extractor_no_llm_cli.py").exists()
        )
        
        if not (module_exists or cli_exists):
            return False
        
        # Check output file
        output_file = self.project_root / "localhost_8000_no_llm_elements.json"
        output_exists = self.check("Output JSON exists", output_file.exists())
        
        if output_exists:
            try:
                with open(output_file) as f:
                    data = json.load(f)
                self.check("JSON is valid", True)
                self.check("Has 'url' field", 'url' in data)
                self.check("Has 'formatted_url' field", 'formatted_url' in data)
                self.check("formatted_url is 'localhost_8000'", data.get('formatted_url') == 'localhost_8000')
                self.check("Has 'elements' array", 'elements' in data and isinstance(data['elements'], list))
                self.check("Has at least 4 elements", len(data.get('elements', [])) >= 4)
                self.check("Has 'screenshots' array", 'screenshots' in data)
                return True
            except Exception as e:
                self.check("JSON is valid", False)
                print(f"  JSON Error: {e}")
                return False
        else:
            print("  Run: python element_extractor_no_llm_cli.py --url http://localhost:8000")
            return False
    
    def audit_step_4_with_llm(self) -> bool:
        """Audit element extraction with LLM"""
        print("\n" + "="*60)
        print("STEP 4: ELEMENT EXTRACTION WITH LLM")
        print("="*60)
        
        # Check module files
        module_exists = self.check(
            "elements_extractor_with_llm.py exists",
            (self.project_root / "elements_extractor_with_llm.py").exists()
        )
        cli_exists = self.check(
            "element_extractor_with_llm_cli.py exists",
            (self.project_root / "element_extractor_with_llm_cli.py").exists()
        )
        
        # Check input from step 3
        input_file = self.project_root / "localhost_8000_no_llm_elements.json"
        input_exists = self.check("Input from Step 3 exists", input_file.exists())
        
        # Check output file
        output_file = self.project_root / "localhost_8000_with_llm_elements.json"
        output_exists = self.check("Output JSON exists", output_file.exists())
        
        if output_exists:
            try:
                with open(output_file) as f:
                    data = json.load(f)
                self.check("JSON is valid", True)
                self.check("Has 'url' field", 'url' in data)
                self.check("Has 'formatted_url' field", 'formatted_url' in data)
                self.check("formatted_url is 'localhost_8000'", data.get('formatted_url') == 'localhost_8000')
                self.check("Has 'page_type' field", 'page_type' in data)
                self.check("Page type identified", data.get('page_type') != 'unknown')
                self.check("Has 'enriched_elements' array", 'enriched_elements' in data)
                self.check("Has 'llm_insights' object", 'llm_insights' in data)
                self.check("Has 'test_scenarios' array", 'test_scenarios' in data)
                return True
            except Exception as e:
                self.check("JSON is valid", False)
                print(f"  JSON Error: {e}")
                return False
        else:
            print("  Run: python element_extractor_with_llm_cli.py --input localhost_8000_no_llm_elements.json")
            return False
    
    def audit_step_5_test_gen(self) -> bool:
        """Audit test generation with LLM"""
        print("\n" + "="*60)
        print("STEP 5: TEST GENERATION WITH LLM")
        print("="*60)
        
        # Check module files
        module_exists = self.check(
            "test_generation_with_llm.py exists",
            (self.project_root / "test_generation_with_llm.py").exists()
        )
        cli_exists = self.check(
            "test_generation_with_llm_cli.py exists",
            (self.project_root / "test_generation_with_llm_cli.py").exists()
        )
        
        # Check input from step 4
        input_file = self.project_root / "localhost_8000_with_llm_elements.json"
        input_exists = self.check("Input from Step 4 exists", input_file.exists())
        
        # Check output file
        output_file = self.project_root / "localhost_8000_with_llm_tests.json"
        output_exists = self.check("Output JSON exists", output_file.exists())
        
        if output_exists:
            try:
                with open(output_file) as f:
                    data = json.load(f)
                self.check("JSON is valid", True)
                self.check("Has 'url' field", 'url' in data)
                self.check("Has 'formatted_url' field", 'formatted_url' in data)
                self.check("formatted_url is 'localhost_8000'", data.get('formatted_url') == 'localhost_8000')
                self.check("Has 'test_scenarios' array", 'test_scenarios' in data)
                self.check("Has at least 10 scenarios", len(data.get('test_scenarios', [])) >= 10)
                self.check("Has 'categories_covered' array", 'categories_covered' in data)
                self.check("Has 'test_suite' object", 'test_suite' in data)
                
                # Check categories
                categories = data.get('categories_covered', [])
                self.check("Includes 'functional' tests", 'functional' in categories)
                self.check("Includes 'validation' tests", 'validation' in categories)
                self.check("Includes 'security' tests", 'security' in categories)
                return True
            except Exception as e:
                self.check("JSON is valid", False)
                print(f"  JSON Error: {e}")
                return False
        else:
            print("  Run: python test_generation_with_llm_cli.py --input localhost_8000_with_llm_elements.json")
            return False
    
    def run_full_audit(self) -> bool:
        """Run complete pipeline audit"""
        print("\n" + "="*60)
        print("UI TESTING FRAMEWORK - COMPREHENSIVE PIPELINE AUDIT")
        print("="*60)
        print(f"Project Root: {self.project_root}")
        print(f"Python: {self.venv_python}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run all audit steps
        step0_pass = self.audit_step_0_foundation()
        step1_pass = self.audit_step_1_html()
        step2_pass = self.audit_step_2_server()
        step3_pass = self.audit_step_3_no_llm()
        step4_pass = self.audit_step_4_with_llm()
        step5_pass = self.audit_step_5_test_gen()
        
        # Summary
        print("\n" + "="*60)
        print("AUDIT SUMMARY")
        print("="*60)
        print(f"Total Checks: {self.total_checks}")
        print(f"Passed: {self.passed_checks}")
        print(f"Failed: {self.total_checks - self.passed_checks}")
        print(f"Success Rate: {(self.passed_checks/self.total_checks*100):.1f}%")
        
        print("\nStep Results:")
        print(f"  Step 0 (Foundation): {'[PASS]' if step0_pass else '[FAIL]'}")
        print(f"  Step 1 (HTML): {'[PASS]' if step1_pass else '[FAIL]'}")
        print(f"  Step 2 (Server): {'[PASS]' if step2_pass else '[FAIL]'}")
        print(f"  Step 3 (No LLM): {'[PASS]' if step3_pass else '[FAIL]'}")
        print(f"  Step 4 (With LLM): {'[PASS]' if step4_pass else '[FAIL]'}")
        print(f"  Step 5 (Test Gen): {'[PASS]' if step5_pass else '[FAIL]'}")
        
        all_pass = all([step0_pass, step1_pass, step2_pass, step3_pass, step4_pass, step5_pass])
        
        if all_pass:
            print("\n[SUCCESS] PIPELINE FULLY VALIDATED AND OPERATIONAL!")
            print("Framework Status: PRODUCTION READY")
        else:
            print("\n[WARNING] PIPELINE VALIDATION FAILED")
            print("Please fix the issues identified above and re-run audit")
        
        # Save audit report
        report_file = self.project_root / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_checks': self.total_checks,
                'passed_checks': self.passed_checks,
                'success_rate': self.passed_checks/self.total_checks,
                'all_pass': all_pass,
                'results': self.audit_results
            }, f, indent=2)
        print(f"\nAudit report saved to: {report_file}")
        
        return all_pass


def main():
    """Main entry point"""
    auditor = PipelineAuditor()
    success = auditor.run_full_audit()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()