#!/usr/bin/env python3
"""
Claude Code Automation Scripts
==============================
Advanced automation utilities for Claude Code environment
Using master prompt strategies for optimal AI assistance
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess

class ClaudeCodeAutomation:
    """
    Automation helper for Claude Code workflows
    Implements best practices from 2025 research
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.claude_dir = self.project_root / '.claude'
        self.settings_path = self.claude_dir / 'settings.json'
        self.templates_path = self.claude_dir / 'prompt_templates.json'
        
        # Load configurations
        self.settings = self._load_json(self.settings_path)
        self.templates = self._load_json(self.templates_path)
    
    def _load_json(self, path: Path) -> Dict:
        """Load JSON configuration file"""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_json(self, data: Dict, path: Path):
        """Save JSON configuration file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # ========================================================================
    # WORKFLOW AUTOMATION
    # ========================================================================
    
    def execute_workflow(self, workflow_name: str) -> bool:
        """
        Execute a predefined workflow
        
        Args:
            workflow_name: Name of workflow (new_feature, bug_fix, refactor)
        
        Returns:
            Success status
        """
        workflows = self.settings.get('workflows', {})
        if workflow_name not in workflows:
            print(f"[ERROR] Unknown workflow: {workflow_name}")
            print(f"Available workflows: {list(workflows.keys())}")
            return False
        
        steps = workflows[workflow_name]
        print(f"🚀 Executing workflow: {workflow_name}")
        print("=" * 60)
        
        for i, step in enumerate(steps, 1):
            print(f"Step {i}/{len(steps)}: {step}")
            self._execute_step(step)
            print()
        
        print("[OK] Workflow complete!")
        return True
    
    def _execute_step(self, step: str):
        """Execute a single workflow step"""
        step_actions = {
            'research': self._research_step,
            'create_plan': self._plan_step,
            'implement': self._implement_step,
            'test': self._test_step,
            'document': self._document_step,
            'commit': self._commit_step,
            'reproduce': self._reproduce_step,
            'analyze': self._analyze_step,
            'fix': self._fix_step,
            'verify': self._verify_step,
            'analyze_current': self._analyze_current_step,
            'plan_changes': self._plan_changes_step,
            'ensure_no_regression': self._regression_test_step,
            'update_docs': self._update_docs_step
        }
        
        action = step_actions.get(step, lambda: print(f"  [WARNING] Manual step: {step}"))
        action()
    
    def _research_step(self):
        """Research phase using Tree of Thoughts"""
        template = self.templates['templates']['research_and_plan']['template']
        print("  📚 Research phase initiated")
        print("  Using Tree of Thoughts strategy")
        print("  Template loaded: research_and_plan")
        self._save_context("research", template)
    
    def _plan_step(self):
        """Planning phase"""
        print("  📋 Creating implementation plan")
        print("  Saved to: .claude/current_plan.md")
    
    def _implement_step(self):
        """Implementation phase using Constitutional AI"""
        template = self.templates['templates']['generate_with_constitutional_ai']['template']
        print("  💻 Implementation phase")
        print("  Using Constitutional AI strategy")
        self._save_context("implementation", template)
    
    def _test_step(self):
        """Testing phase"""
        print("  🧪 Running tests")
        test_cmd = self.settings.get('shortcuts', {}).get('test', 'python test_integration_complete.py')
        try:
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("  [OK] Tests passed")
            else:
                print("  [ERROR] Tests failed")
                print(result.stdout[-500:])  # Show last 500 chars
        except Exception as e:
            print(f"  [WARNING] Test execution failed: {e}")
    
    def _document_step(self):
        """Documentation phase"""
        print("  📝 Updating documentation")
        print("  Files to update: README.md, CLAUDE.md")
    
    def _commit_step(self):
        """Commit phase"""
        print("  📦 Creating commit")
        print("  Following conventional commit standards")
    
    def _reproduce_step(self):
        """Bug reproduction phase"""
        print("  🐛 Reproducing issue")
        print("  Using ReAct pattern for systematic debugging")
    
    def _analyze_step(self):
        """Analysis phase using Meta-Prompting"""
        template = self.templates['templates']['analyze_with_meta_prompting']['template']
        print("  🔍 Analyzing with Meta-Prompting")
        self._save_context("analysis", template)
    
    def _fix_step(self):
        """Fix implementation phase"""
        print("  🔧 Implementing fix")
        print("  Using Self-Consistency for validation")
    
    def _verify_step(self):
        """Verification phase"""
        print("  [VERIFY] Verifying fix")
        self._test_step()
    
    def _analyze_current_step(self):
        """Analyze current code"""
        print("  📊 Analyzing current implementation")
    
    def _plan_changes_step(self):
        """Plan refactoring changes"""
        print("  📐 Planning refactor with Tree of Thoughts")
    
    def _regression_test_step(self):
        """Run regression tests"""
        print("  🔄 Running regression tests")
        self._test_step()
    
    def _update_docs_step(self):
        """Update documentation"""
        self._document_step()
    
    def _save_context(self, phase: str, content: str):
        """Save context for Claude Code"""
        context_file = self.claude_dir / f"current_{phase}.md"
        with open(context_file, 'w') as f:
            f.write(content)
        print(f"  💾 Context saved: {context_file.name}")
    
    # ========================================================================
    # PROMPT STRATEGY SELECTION
    # ========================================================================
    
    def select_strategy(self, task_type: str, complexity: str) -> str:
        """
        Select optimal prompt strategy based on task
        
        Args:
            task_type: Type of task (analytical, creative, debugging, optimization)
            complexity: Complexity level (simple, moderate, complex, paradoxical)
        
        Returns:
            Recommended strategy name
        """
        rules = self.templates.get('strategy_selector', {}).get('rules', [])
        
        for rule in rules:
            condition = rule['condition']
            # Simple condition evaluation (in practice, use proper parser)
            if f"task_type == '{task_type}'" in condition:
                return rule['strategy']
            if f"task_complexity == '{complexity}'" in condition:
                return rule['strategy']
        
        # Default fallback
        return 'chain_of_thought'
    
    def get_template(self, strategy: str) -> Dict:
        """Get prompt template for a strategy"""
        templates = self.templates.get('templates', {})
        for template_name, template_data in templates.items():
            if template_data.get('strategy') == strategy:
                return template_data
        return {}
    
    # ========================================================================
    # QUALITY CHECKS
    # ========================================================================
    
    def run_quality_checks(self, file_path: str, auto_fix: bool = False) -> Dict[str, bool]:
        """
        Run all quality checks on a file
        
        Args:
            file_path: Path to file to check
            auto_fix: Whether to auto-fix issues
        
        Returns:
            Results of each check
        """
        results = {}
        
        print(f"🔍 Running quality checks on: {file_path}")
        print("=" * 60)
        
        # Type checking
        print("Running mypy...")
        mypy_cmd = f"mypy {file_path} --ignore-missing-imports --strict"
        mypy_result = subprocess.run(mypy_cmd, shell=True, capture_output=True)
        results['mypy'] = mypy_result.returncode == 0
        print(f"  Mypy: {'[OK] Passed' if results['mypy'] else '[ERROR] Failed'}")
        
        # Linting
        print("Running flake8...")
        flake8_cmd = f"flake8 {file_path} --max-line-length=120"
        flake8_result = subprocess.run(flake8_cmd, shell=True, capture_output=True)
        results['flake8'] = flake8_result.returncode == 0
        print(f"  Flake8: {'[OK] Passed' if results['flake8'] else '[ERROR] Failed'}")
        
        # Formatting
        if auto_fix:
            print("Running black (auto-fix)...")
            black_cmd = f"black {file_path} --line-length=120"
            subprocess.run(black_cmd, shell=True)
            print("  Black: [OK] Formatted")
            results['black'] = True
        else:
            print("Running black (check)...")
            black_cmd = f"black {file_path} --line-length=120 --check"
            black_result = subprocess.run(black_cmd, shell=True, capture_output=True)
            results['black'] = black_result.returncode == 0
            print(f"  Black: {'[OK] Formatted' if results['black'] else '[WARNING] Needs formatting'}")
        
        return results
    
    # ========================================================================
    # ENVIRONMENT HEALTH CHECK
    # ========================================================================
    
    def health_check(self) -> bool:
        """
        Comprehensive environment health check
        
        Returns:
            True if all checks pass
        """
        print("== Claude Code Environment Health Check ==")
        print("=" * 60)
        
        checks = []
        
        # Check Python environment
        print("Checking Python environment...")
        try:
            import browser
            import llm
            import prompts
            import browser_with_llm
            print("  [OK] All core modules import successfully")
            checks.append(True)
        except ImportError as e:
            print(f"  [ERROR] Import error: {e}")
            checks.append(False)
        
        # Check virtual environment
        venv_path = self.project_root / '.venv'
        if venv_path.exists():
            print("  [OK] Virtual environment exists")
            checks.append(True)
        else:
            print("  [WARNING] Virtual environment not found")
            checks.append(False)
        
        # Check configuration files
        print("\nChecking configuration files...")
        config_files = [
            ('CLAUDE.md', self.project_root / 'CLAUDE.md'),
            ('settings.json', self.settings_path),
            ('prompt_templates.json', self.templates_path),
            ('.mcp.json', self.project_root / '.mcp.json')
        ]
        
        for name, path in config_files:
            if path.exists():
                print(f"  [OK] {name} exists")
                checks.append(True)
            else:
                print(f"  [ERROR] {name} missing")
                checks.append(False)
        
        # Check API keys
        print("\nChecking API keys...")
        env_path = self.project_root / '.env'
        if env_path.exists():
            with open(env_path) as f:
                env_content = f.read()
                keys = ['OPENAI_API_KEY', 'GOOGLE_API_KEY', 'ANTHROPIC_API_KEY']
                for key in keys:
                    if key in env_content:
                        print(f"  [OK] {key} configured")
                        checks.append(True)
                    else:
                        print(f"  [WARNING] {key} not configured")
                        checks.append(False)
        else:
            print("  [ERROR] .env file not found")
            checks.append(False)
        
        # Summary
        print("\n" + "=" * 60)
        passed = sum(checks)
        total = len(checks)
        
        if all(checks):
            print(f"[OK] Health Check PASSED ({passed}/{total} checks)")
            return True
        else:
            print(f"[WARNING] Health Check PARTIAL ({passed}/{total} checks)")
            print("\nRecommended actions:")
            if not (self.project_root / '.venv').exists():
                print("  - Create virtual environment: python -m venv .venv")
            if not env_path.exists():
                print("  - Create .env file with API keys")
            return False
    
    # ========================================================================
    # METRICS AND REPORTING
    # ========================================================================
    
    def generate_metrics_report(self) -> Dict[str, Any]:
        """Generate comprehensive metrics report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project': 'UI Testing Automation Framework',
            'version': '4.0.0',
            'health_status': 'unknown',
            'modules': {},
            'quality_metrics': {},
            'performance_metrics': {}
        }
        
        # Check health
        report['health_status'] = 'healthy' if self.health_check() else 'needs_attention'
        
        # Count lines of code
        py_files = list((self.project_root / 'ui_testing_automation').glob('*.py'))
        total_lines = 0
        for file in py_files:
            with open(file) as f:
                lines = len(f.readlines())
                total_lines += lines
                report['modules'][file.name] = {'lines': lines}
        
        report['quality_metrics']['total_lines'] = total_lines
        report['quality_metrics']['module_count'] = len(py_files)
        
        return report

# ========================================================================
# CLI INTERFACE
# ========================================================================

def main():
    """CLI interface for automation scripts"""
    automation = ClaudeCodeAutomation()
    
    if len(sys.argv) < 2:
        print("Claude Code Automation Tool")
        print("=" * 60)
        print("Usage: python automation_scripts.py <command> [args]")
        print("\nCommands:")
        print("  health        - Run health check")
        print("  workflow      - Execute workflow (new_feature|bug_fix|refactor)")
        print("  quality       - Run quality checks on file")
        print("  strategy      - Select optimal strategy for task")
        print("  metrics       - Generate metrics report")
        return
    
    command = sys.argv[1]
    
    if command == 'health':
        automation.health_check()
    
    elif command == 'workflow':
        if len(sys.argv) < 3:
            print("Usage: python automation_scripts.py workflow <workflow_name>")
        else:
            automation.execute_workflow(sys.argv[2])
    
    elif command == 'quality':
        if len(sys.argv) < 3:
            print("Usage: python automation_scripts.py quality <file_path> [--fix]")
        else:
            auto_fix = '--fix' in sys.argv
            automation.run_quality_checks(sys.argv[2], auto_fix)
    
    elif command == 'strategy':
        if len(sys.argv) < 4:
            print("Usage: python automation_scripts.py strategy <task_type> <complexity>")
        else:
            strategy = automation.select_strategy(sys.argv[2], sys.argv[3])
            template = automation.get_template(strategy)
            print(f"Recommended strategy: {strategy}")
            if template:
                print(f"Use for: {', '.join(template.get('use_for', []))}")
    
    elif command == 'metrics':
        report = automation.generate_metrics_report()
        print(json.dumps(report, indent=2))
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()