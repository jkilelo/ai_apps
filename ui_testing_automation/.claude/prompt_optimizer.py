#!/usr/bin/env python3
"""
Advanced Prompt Optimizer for Claude Code
==========================================
Based on analysis of historical prompts and master strategies
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

class PromptQuality(Enum):
    """Quality levels for prompts"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    FAIR = "fair"           # 50-69%
    POOR = "poor"           # <50%

@dataclass
class PromptPattern:
    """Represents an effective prompt pattern"""
    name: str
    description: str
    effectiveness: float  # 0-100%
    template: str
    when_to_use: List[str]
    examples: List[str] = field(default_factory=list)

@dataclass
class OptimizedPrompt:
    """Result of prompt optimization"""
    original: str
    optimized: str
    quality_score: float
    improvements: List[str]
    strategies_applied: List[str]
    estimated_effectiveness: float

class PromptOptimizer:
    """Main prompt optimization engine"""
    
    def __init__(self):
        self.patterns = self._load_effective_patterns()
        self.strategies = self._load_master_strategies()
        self.templates = self._load_templates()
        
    def _load_effective_patterns(self) -> Dict[str, PromptPattern]:
        """Load patterns identified from historical analysis"""
        return {
            "role_definition": PromptPattern(
                name="Expert Role Definition",
                description="Start with 30+ years expert role",
                effectiveness=95.0,
                template="You are an expert {domain} engineer with 30+ years of experience in {specialization}. You excel at {key_skills}.",
                when_to_use=["code_generation", "architecture", "review"],
                examples=[
                    "You are an expert software engineer with 30+ years of experience in Python and clean architecture.",
                    "You are a Senior QA Engineer with 30+ years of experience finding bugs and ensuring quality."
                ]
            ),
            "explicit_criteria": PromptPattern(
                name="Explicit Success Criteria",
                description="Define measurable success criteria",
                effectiveness=92.0,
                template="Success Criteria:\n- [ ] {criterion_1}\n- [ ] {criterion_2}\n- [ ] {criterion_3}",
                when_to_use=["any_task"],
                examples=[
                    "- [ ] Module runs standalone with python module.py",
                    "- [ ] Contains 2+ working examples in __main__"
                ]
            ),
            "strategy_reference": PromptPattern(
                name="Master Strategy Reference",
                description="Reference specific strategies to apply",
                effectiveness=90.0,
                template="Use {strategy_1} for {purpose_1} and {strategy_2} for {purpose_2} from master_prompt_strategies.",
                when_to_use=["complex_tasks", "quality_improvement"],
                examples=[
                    "Use Constitutional AI for quality principles and Self-Consistency for validation.",
                    "Use Tree of Thoughts to explore solutions and Meta-Prompting to self-improve."
                ]
            ),
            "dry_enforcement": PromptPattern(
                name="DRY Principle Enforcement",
                description="Prevent code duplication",
                effectiveness=85.0,
                template="DRY Principle: Reuse {existing_modules}. Never duplicate functionality from {avoid_modules}.",
                when_to_use=["integration", "refactoring"],
                examples=[
                    "DRY Principle: Reuse browser.py, llm.py, prompts.py. Never duplicate their functionality."
                ]
            ),
            "progressive_refinement": PromptPattern(
                name="Progressive Refinement",
                description="Iterative improvement approach",
                effectiveness=88.0,
                template="Phase 1: {initial_task}\nPhase 2: {quality_check}\nPhase 3: {fixes}\nPhase 4: {verification}",
                when_to_use=["complex_implementation", "quality_assurance"],
                examples=[
                    "Phase 1: Implement core functionality\nPhase 2: Run quality checks\nPhase 3: Fix identified issues\nPhase 4: Verify compliance"
                ]
            )
        }
    
    def _load_master_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Load master strategies with effectiveness scores"""
        return {
            "constitutional_ai": {
                "effectiveness": 95,
                "use_for": ["quality", "security", "principles"],
                "prompt_addon": "Apply Constitutional AI principles to ensure {principles}"
            },
            "meta_prompting": {
                "effectiveness": 92,
                "use_for": ["self_improvement", "questioning", "review"],
                "prompt_addon": "Use Meta-Prompting to question and improve {aspect}"
            },
            "self_consistency": {
                "effectiveness": 90,
                "use_for": ["validation", "verification", "consistency"],
                "prompt_addon": "Apply Self-Consistency to validate {outputs}"
            },
            "tree_of_thoughts": {
                "effectiveness": 88,
                "use_for": ["exploration", "optimization", "alternatives"],
                "prompt_addon": "Use Tree of Thoughts to explore {branches}"
            },
            "chain_of_thought": {
                "effectiveness": 85,
                "use_for": ["step_by_step", "reasoning", "explanation"],
                "prompt_addon": "Think step-by-step using Chain of Thought"
            }
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load optimized templates"""
        templates_dir = Path(__file__).parent / "prompt_templates"
        templates = {}
        
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.md"):
                templates[template_file.stem] = template_file.read_text()
                
        return templates
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze a prompt for quality and patterns"""
        analysis = {
            "length": len(prompt),
            "word_count": len(prompt.split()),
            "patterns_found": [],
            "missing_patterns": [],
            "quality_score": 0.0,
            "suggestions": []
        }
        
        # Check for effective patterns
        for pattern_name, pattern in self.patterns.items():
            if self._pattern_present(prompt, pattern):
                analysis["patterns_found"].append(pattern_name)
            else:
                analysis["missing_patterns"].append(pattern_name)
        
        # Calculate quality score
        pattern_score = len(analysis["patterns_found"]) / len(self.patterns) * 100
        
        # Length penalty (too long or too short)
        length_score = 100
        if analysis["word_count"] < 50:
            length_score = 60  # Too short
        elif analysis["word_count"] > 500:
            length_score = 70  # Too long
            
        # Check for clarity markers
        clarity_score = 0
        clarity_markers = ["objective", "success criteria", "constraints", "verification"]
        for marker in clarity_markers:
            if marker.lower() in prompt.lower():
                clarity_score += 25
                
        analysis["quality_score"] = (pattern_score + length_score + clarity_score) / 3
        
        # Generate suggestions
        if analysis["quality_score"] < 70:
            analysis["suggestions"] = self._generate_suggestions(analysis)
            
        return analysis
    
    def _pattern_present(self, prompt: str, pattern: PromptPattern) -> bool:
        """Check if a pattern is present in the prompt"""
        prompt_lower = prompt.lower()
        
        # Pattern-specific checks
        if pattern.name == "Expert Role Definition":
            return "30+ years" in prompt or "expert" in prompt_lower
        elif pattern.name == "Explicit Success Criteria":
            return "success criteria" in prompt_lower or "- [ ]" in prompt
        elif pattern.name == "Master Strategy Reference":
            return "master_prompt_strategies" in prompt or "strategies from" in prompt_lower
        elif pattern.name == "DRY Principle Enforcement":
            return "dry" in prompt_lower or "reuse" in prompt_lower
        elif pattern.name == "Progressive Refinement":
            return "phase" in prompt_lower or "iterative" in prompt_lower
            
        return False
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        for missing in analysis["missing_patterns"]:
            pattern = self.patterns[missing]
            suggestions.append(f"Add {pattern.name}: {pattern.description}")
            
        if analysis["word_count"] > 500:
            suggestions.append("Reduce prompt length - break into smaller, chained prompts")
        elif analysis["word_count"] < 50:
            suggestions.append("Add more detail - specify requirements and constraints")
            
        return suggestions
    
    def optimize_prompt(self, prompt: str, task_type: str = "general") -> OptimizedPrompt:
        """Optimize a prompt based on best practices"""
        analysis = self.analyze_prompt(prompt)
        optimized = prompt
        improvements = []
        strategies_applied = []
        
        # Apply missing patterns
        for missing in analysis["missing_patterns"]:
            pattern = self.patterns[missing]
            if task_type in pattern.when_to_use or "any_task" in pattern.when_to_use:
                # Add pattern to prompt
                if missing == "role_definition" and "expert" not in prompt.lower():
                    prefix = "You are an expert software engineer with 30+ years of experience. "
                    optimized = prefix + optimized
                    improvements.append(f"Added expert role definition")
                    
                elif missing == "explicit_criteria":
                    criteria = "\n\nSuccess Criteria:\n- [ ] Task completed successfully\n- [ ] Quality checks pass\n- [ ] Integration verified\n"
                    optimized += criteria
                    improvements.append("Added explicit success criteria")
                    
                elif missing == "strategy_reference":
                    strategies = "\n\nApply Constitutional AI for quality and Self-Consistency for validation from master_prompt_strategies."
                    optimized += strategies
                    improvements.append("Added strategy references")
                    strategies_applied.extend(["constitutional_ai", "self_consistency"])
        
        # Structure optimization
        if not self._is_well_structured(optimized):
            optimized = self._restructure_prompt(optimized)
            improvements.append("Restructured for clarity")
            
        # Calculate effectiveness
        new_analysis = self.analyze_prompt(optimized)
        
        return OptimizedPrompt(
            original=prompt,
            optimized=optimized,
            quality_score=new_analysis["quality_score"],
            improvements=improvements,
            strategies_applied=strategies_applied,
            estimated_effectiveness=self._estimate_effectiveness(new_analysis)
        )
    
    def _is_well_structured(self, prompt: str) -> bool:
        """Check if prompt has good structure"""
        sections = ["objective", "criteria", "constraints", "verification"]
        found_sections = sum(1 for s in sections if s in prompt.lower())
        return found_sections >= 2
    
    def _restructure_prompt(self, prompt: str) -> str:
        """Restructure prompt for better clarity"""
        lines = prompt.split('\n')
        
        # Try to identify sections
        structured = []
        current_section = []
        
        for line in lines:
            if any(marker in line.lower() for marker in ["objective", "goal", "task"]):
                if current_section:
                    structured.append('\n'.join(current_section))
                structured.append("\n## Objective")
                current_section = [line]
            elif any(marker in line.lower() for marker in ["criteria", "success", "requirements"]):
                if current_section:
                    structured.append('\n'.join(current_section))
                structured.append("\n## Success Criteria")
                current_section = [line]
            elif any(marker in line.lower() for marker in ["constraint", "guideline", "rule"]):
                if current_section:
                    structured.append('\n'.join(current_section))
                structured.append("\n## Constraints")
                current_section = [line]
            else:
                current_section.append(line)
                
        if current_section:
            structured.append('\n'.join(current_section))
            
        return '\n'.join(structured)
    
    def _estimate_effectiveness(self, analysis: Dict[str, Any]) -> float:
        """Estimate prompt effectiveness"""
        base_score = analysis["quality_score"]
        
        # Bonus for having key patterns
        pattern_bonus = len(analysis["patterns_found"]) * 5
        
        # Penalty for being too long
        length_penalty = 0
        if analysis["word_count"] > 500:
            length_penalty = 10
            
        effectiveness = min(100, base_score + pattern_bonus - length_penalty)
        return effectiveness
    
    def create_prompt(self, task_type: str, **kwargs) -> str:
        """Create an optimized prompt from template"""
        template_map = {
            "code_generation": "code_generation_template",
            "qa_review": "qa_review_template",
            "integration": "integration_template"
        }
        
        template_name = template_map.get(task_type, "code_generation_template")
        
        if template_name in self.templates:
            template = self.templates[template_name]
            
            # Replace placeholders
            for key, value in kwargs.items():
                placeholder = f"[{key.upper()}]"
                if placeholder in template:
                    template = template.replace(placeholder, str(value))
                    
            return template
        
        # Fallback to basic structure
        return self._create_basic_prompt(task_type, **kwargs)
    
    def _create_basic_prompt(self, task_type: str, **kwargs) -> str:
        """Create a basic optimized prompt"""
        prompt_parts = []
        
        # Role definition
        prompt_parts.append(
            "You are an expert software engineer with 30+ years of experience."
        )
        
        # Objective
        if "objective" in kwargs:
            prompt_parts.append(f"\n## Objective\n{kwargs['objective']}")
        
        # Success criteria
        prompt_parts.append("\n## Success Criteria")
        if "criteria" in kwargs:
            for criterion in kwargs["criteria"]:
                prompt_parts.append(f"- [ ] {criterion}")
        else:
            prompt_parts.append("- [ ] Task completed successfully")
            prompt_parts.append("- [ ] Quality checks pass")
            
        # Strategy application
        prompt_parts.append(
            "\n## Strategy Application\n"
            "Apply Constitutional AI for quality principles and "
            "Self-Consistency for validation from master_prompt_strategies."
        )
        
        return '\n'.join(prompt_parts)
    
    def batch_optimize(self, prompts: List[str]) -> List[OptimizedPrompt]:
        """Optimize multiple prompts"""
        return [self.optimize_prompt(p) for p in prompts]
    
    def export_analysis(self, output_path: Optional[Path] = None) -> Path:
        """Export analysis results"""
        if not output_path:
            output_path = Path(".claude/prompt_analysis.json")
            
        output_path.parent.mkdir(exist_ok=True)
        
        analysis_data = {
            "patterns": {
                name: {
                    "description": p.description,
                    "effectiveness": p.effectiveness,
                    "when_to_use": p.when_to_use
                }
                for name, p in self.patterns.items()
            },
            "strategies": self.strategies,
            "templates_loaded": list(self.templates.keys())
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)
            
        return output_path

def main():
    """Main entry point for prompt optimization"""
    import sys
    
    optimizer = PromptOptimizer()
    
    if len(sys.argv) < 2:
        print("Prompt Optimizer for Claude Code")
        print("=" * 60)
        print("\nUsage:")
        print("  prompt_optimizer.py analyze <prompt_file>")
        print("  prompt_optimizer.py optimize <prompt_file>")
        print("  prompt_optimizer.py create <task_type>")
        print("\nTask types: code_generation, qa_review, integration")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "analyze" and len(sys.argv) > 2:
        prompt_file = Path(sys.argv[2])
        if prompt_file.exists():
            prompt = prompt_file.read_text()
            analysis = optimizer.analyze_prompt(prompt)
            
            print("\n[PROMPT ANALYSIS]")
            print("=" * 60)
            print(f"Quality Score: {analysis['quality_score']:.1f}/100")
            print(f"Word Count: {analysis['word_count']}")
            print(f"\nPatterns Found: {', '.join(analysis['patterns_found']) or 'None'}")
            print(f"Missing Patterns: {', '.join(analysis['missing_patterns']) or 'None'}")
            
            if analysis['suggestions']:
                print("\nSuggestions:")
                for suggestion in analysis['suggestions']:
                    print(f"  - {suggestion}")
    
    elif command == "optimize" and len(sys.argv) > 2:
        prompt_file = Path(sys.argv[2])
        if prompt_file.exists():
            prompt = prompt_file.read_text()
            result = optimizer.optimize_prompt(prompt)
            
            print("\n[PROMPT OPTIMIZATION]")
            print("=" * 60)
            print(f"Original Quality: {optimizer.analyze_prompt(prompt)['quality_score']:.1f}")
            print(f"Optimized Quality: {result.quality_score:.1f}")
            print(f"Estimated Effectiveness: {result.estimated_effectiveness:.1f}%")
            
            print("\nImprovements Applied:")
            for improvement in result.improvements:
                print(f"  - {improvement}")
            
            print("\nStrategies Applied:")
            for strategy in result.strategies_applied:
                print(f"  - {strategy}")
            
            # Save optimized prompt
            output_path = prompt_file.with_suffix('.optimized.md')
            output_path.write_text(result.optimized)
            print(f"\n[SUCCESS] Optimized prompt saved to: {output_path}")
    
    elif command == "create" and len(sys.argv) > 2:
        task_type = sys.argv[2]
        prompt = optimizer.create_prompt(
            task_type,
            objective="Create a high-quality module",
            criteria=["Runs standalone", "Has examples", "Passes tests"]
        )
        
        print("\n[GENERATED PROMPT]")
        print("=" * 60)
        print(prompt)
        
        # Save to file
        output_path = Path(f".claude/generated_{task_type}_prompt.md")
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(prompt)
        print(f"\n[SUCCESS] Prompt saved to: {output_path}")
    
    else:
        print("[ERROR] Invalid command or arguments")

if __name__ == "__main__":
    main()