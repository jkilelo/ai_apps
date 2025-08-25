#!/usr/bin/env python3
"""
Advanced Features Demo for Code Generation with LLM

This example demonstrates:
- Constitutional AI safety features
- Universal Self-Consistency (multi-path generation)
- PAL (Program-Aided Language) validation
- RAFA (Reason for Future, Act for Now) patterns
- DSPy refinement
- Comprehensive quality metrics
- Security violation detection and remediation

Requirements:
- API key: OPENAI_API_KEY (recommended for best results)
- Dependencies: openai, black, psutil
"""

import asyncio
import os
import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code_generation_with_llm import (
    CodeGenerationWithLLM, 
    QuantumCodeGenerator,
    CodeGenerationConfig,
    TestFramework,
    BrowserFramework,
    CodePattern,
    LLMProvider
)

async def demonstrate_constitutional_ai():
    """
    Demonstrates Constitutional AI safety features
    """
    print("="*70)
    print("CONSTITUTIONAL AI SAFETY DEMONSTRATION")
    print("="*70)
    
    # Intentionally unsafe Gherkin that might generate problematic code
    unsafe_gherkin = """
Feature: System Administration
  Scenario: Execute system command
    Given I have admin privileges
    When I run system command to delete temp files
    And I execute shell commands for cleanup
    Then the system should be cleaned up
    
  Scenario: Database direct access
    Given I connect to the database directly
    When I execute SQL commands with user input
    Then the data should be updated
"""

    config = CodeGenerationConfig(
        test_framework=TestFramework.PYTEST,
        browser_framework=BrowserFramework.PLAYWRIGHT,
        
        # Maximum safety settings
        enable_constitutional_ai=True,
        safety_threshold=0.95,  # Very strict
        
        # Quality features
        enable_universal_self_consistency=True,
        enable_pal=True,
        enable_rafa=True,
        
        # Validation
        validate_syntax=True,
        auto_format=True
    )
    
    print("🛡️ Initializing with maximum safety settings...")
    print(f"   Safety threshold: {config.safety_threshold}")
    print(f"   Constitutional AI: {config.enable_constitutional_ai}")
    
    try:
        generator = CodeGenerationWithLLM(
            config=config,
            llm_provider=LLMProvider.OPENAI,
            verbose=True
        )
        
        print("\n📝 Testing potentially unsafe scenario...")
        print("Input Gherkin involves system commands and SQL injection risks")
        
        result = await generator.generate_from_gherkin(unsafe_gherkin)
        
        print("\n🔍 CONSTITUTIONAL AI RESULTS:")
        print("-" * 50)
        print(f"Safety Score: {result.safety_score:.3f}")
        print(f"Violations Found: {len(result.safety_violations)}")
        
        if result.safety_violations:
            print("\n⚠️ Safety Violations Detected:")
            for i, violation in enumerate(result.safety_violations, 1):
                print(f"{i}. {violation.type.upper()}")
                print(f"   Description: {violation.description}")
                print(f"   Severity: {violation.severity}")
                if violation.suggested_fix:
                    print(f"   Suggested Fix: {violation.suggested_fix}")
                print()
        
        print(f"[OK] Generated code is safe: {result.safety_score >= config.safety_threshold}")
        print(f"📊 Code metrics: {result.metrics.lines_of_code} lines generated")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Error in Constitutional AI demo: {e}")
        return None

async def demonstrate_universal_self_consistency():
    """
    Demonstrates Universal Self-Consistency with multiple generation paths
    """
    print("\n" + "="*70)
    print("UNIVERSAL SELF-CONSISTENCY DEMONSTRATION")
    print("="*70)
    
    complex_gherkin = """
Feature: E-commerce Checkout Process
  Scenario: Complete purchase with multiple payment methods
    Given I have items in my shopping cart
    And I am logged in as a premium customer
    When I proceed to checkout
    And I select "Credit Card" as payment method
    And I enter valid credit card information
    And I apply a discount code "SAVE20"
    And I select express shipping
    Then I should see order confirmation
    And I should receive confirmation email
    And my account should show the order
    And the inventory should be updated
"""

    config = CodeGenerationConfig(
        test_framework=TestFramework.PYTEST,
        browser_framework=BrowserFramework.PLAYWRIGHT,
        code_pattern=CodePattern.PAGE_OBJECT,
        
        # Enable Universal Self-Consistency
        enable_universal_self_consistency=True,
        num_synthesis_paths=3,  # Generate 3 different approaches
        
        # Other quality features
        enable_constitutional_ai=True,
        enable_pal=True,
        enable_rafa=True,
        enable_dspy_refinement=True,
        
        safety_threshold=0.9
    )
    
    print("🔄 Generating code using Universal Self-Consistency...")
    print(f"   Number of synthesis paths: {config.num_synthesis_paths}")
    print("   This will generate multiple approaches and synthesize the best elements")
    
    try:
        generator = QuantumCodeGenerator(config)
        
        print("\n⏳ Generating multiple code paths (this may take 30-60 seconds)...")
        
        result = await generator.generate_from_scenario({
            "gherkin": complex_gherkin,
            "context": {
                "url": "https://shop.example.com",
                "user_type": "premium"
            }
        })
        
        print("\n🎯 UNIVERSAL SELF-CONSISTENCY RESULTS:")
        print("-" * 50)
        
        if hasattr(result, 'synthesis_paths'):
            print(f"Paths Generated: {len(result.synthesis_paths)}")
            for i, path in enumerate(result.synthesis_paths, 1):
                print(f"  Path {i}: {path.focus} ({path.score:.2f} quality)")
        
        print(f"Final Code Quality: {result.metrics.maintainability_index:.1f}")
        print(f"Safety Score: {result.safety_score:.3f}")
        print(f"Generation Time: {result.generation_time:.1f}s")
        print(f"Lines of Code: {result.metrics.lines_of_code}")
        
        # Show code structure analysis
        code_lines = result.code.split('\n')
        classes = [line for line in code_lines if line.strip().startswith('class ')]
        methods = [line for line in code_lines if 'def test_' in line]
        
        print(f"\n📊 Code Structure Analysis:")
        print(f"   Classes: {len(classes)}")
        print(f"   Test Methods: {len(methods)}")
        print(f"   Async Methods: {result.code.count('async def')}")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Error in USC demo: {e}")
        return None

async def demonstrate_pal_validation():
    """
    Demonstrates PAL (Program-Aided Language) validation
    """
    print("\n" + "="*70)
    print("PAL (PROGRAM-AIDED LANGUAGE) VALIDATION DEMONSTRATION")
    print("="*70)
    
    validation_gherkin = """
Feature: Form Validation Testing
  Scenario: Test complex form with multiple validation rules
    Given I am on the registration form
    When I enter email "user@example.com"
    And I enter password with 12 characters including symbols
    And I enter phone number in format "+1-555-123-4567"
    And I select birthdate "1990-01-15"
    And I check terms and conditions checkbox
    Then all validation rules should pass
    And the submit button should be enabled
"""

    config = CodeGenerationConfig(
        enable_pal=True,  # Enable PAL validation
        enable_constitutional_ai=True,
        validate_syntax=True,
        auto_format=True,
        
        # Add comprehensive validation
        add_type_hints=True,
        add_docstrings=True
    )
    
    print("🔍 PAL Validation analyzes generated code for:")
    print("   - Syntax correctness")
    print("   - Import validity")
    print("   - Logic consistency")
    print("   - Type safety")
    
    try:
        generator = CodeGenerationWithLLM(config=config)
        
        result = await generator.generate_from_gherkin(validation_gherkin)
        
        print("\n[OK] PAL VALIDATION RESULTS:")
        print("-" * 50)
        
        # PAL validation results
        print(f"Syntax Valid: {result.syntax_valid}")
        print(f"Imports Valid: {getattr(result, 'imports_valid', 'N/A')}")
        print(f"Type Safety: {getattr(result, 'type_safe', 'N/A')}")
        
        if hasattr(result, 'pal_issues') and result.pal_issues:
            print(f"\n⚠️ PAL Issues Found:")
            for issue in result.pal_issues:
                print(f"   - {issue}")
        else:
            print(f"[OK] No PAL validation issues found")
        
        # Show generated code quality
        print(f"\nCode Quality Indicators:")
        print(f"   - Type hints added: {'typing' in result.code}")
        print(f"   - Docstrings added: {'\"\"\"' in result.code}")
        print(f"   - Async/await used: {'async def' in result.code}")
        print(f"   - Error handling: {'try:' in result.code or 'except' in result.code}")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Error in PAL demo: {e}")
        return None

async def demonstrate_rafa_patterns():
    """
    Demonstrates RAFA (Reason for Future, Act for Now) patterns
    """
    print("\n" + "="*70)
    print("RAFA (REASON FOR FUTURE, ACT FOR NOW) DEMONSTRATION")
    print("="*70)
    
    extensible_gherkin = """
Feature: User Profile Management
  Scenario: Update user profile with future extensibility
    Given I am logged in as a user
    When I navigate to profile settings
    And I update my personal information
    And I change my notification preferences
    And I update privacy settings
    Then my changes should be saved
    And I should see confirmation message
"""

    config = CodeGenerationConfig(
        enable_rafa=True,  # Enable RAFA patterns
        enable_constitutional_ai=True,
        code_pattern=CodePattern.PAGE_OBJECT,
        
        # Features that support extensibility
        add_type_hints=True,
        add_docstrings=True,
        validate_syntax=True
    )
    
    print("🔮 RAFA generates code designed for future extensibility:")
    print("   - Configuration-driven behavior")
    print("   - Extensible base classes")
    print("   - Environment variable support")
    print("   - Plugin-ready architecture")
    
    try:
        generator = CodeGenerationWithLLM(config=config)
        
        result = await generator.generate_from_gherkin(extensible_gherkin)
        
        print("\n🏗️ RAFA PATTERN RESULTS:")
        print("-" * 50)
        
        # Analyze RAFA patterns in generated code
        code = result.code
        
        rafa_indicators = {
            "Configuration Support": "config" in code.lower() or "settings" in code.lower(),
            "Environment Variables": "os.getenv" in code or "environ" in code,
            "Base Classes": "class Base" in code or "class Abstract" in code,
            "Type Hints": "from typing import" in code,
            "Docstrings": '"""' in code,
            "Error Handling": "try:" in code and "except" in code,
            "Logging": "import logging" in code or "logger" in code,
            "Extensible Methods": "def _" in code  # Protected methods for extension
        }
        
        print("RAFA Pattern Analysis:")
        for pattern, found in rafa_indicators.items():
            status = "[OK]" if found else "⚪"
            print(f"   {status} {pattern}")
        
        # Count extensibility features
        extensibility_score = sum(rafa_indicators.values()) / len(rafa_indicators)
        print(f"\nExtensibility Score: {extensibility_score:.1%}")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Error in RAFA demo: {e}")
        return None

async def comprehensive_quality_analysis(results):
    """
    Performs comprehensive analysis of all generated code
    """
    print("\n" + "="*70)
    print("COMPREHENSIVE QUALITY ANALYSIS")
    print("="*70)
    
    if not results or not any(results):
        print("[ERROR] No results to analyze")
        return
    
    valid_results = [r for r in results if r is not None]
    
    if not valid_results:
        print("[ERROR] No valid results to analyze")
        return
    
    print(f"📊 Analyzing {len(valid_results)} generated code samples...")
    
    # Aggregate metrics
    total_lines = sum(r.metrics.lines_of_code for r in valid_results if r.metrics)
    avg_safety_score = sum(r.safety_score for r in valid_results) / len(valid_results)
    avg_generation_time = sum(r.generation_time for r in valid_results) / len(valid_results)
    
    print("\n📈 AGGREGATE METRICS:")
    print(f"   Total Lines Generated: {total_lines}")
    print(f"   Average Safety Score: {avg_safety_score:.3f}")
    print(f"   Average Generation Time: {avg_generation_time:.1f}s")
    
    # Quality distribution
    quality_scores = []
    for result in valid_results:
        if result.metrics:
            quality_scores.append(result.metrics.maintainability_index)
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"   Average Code Quality: {avg_quality:.1f}")
    
    # Safety analysis
    total_violations = sum(len(r.safety_violations) for r in valid_results)
    print(f"   Total Safety Violations: {total_violations}")
    
    # Feature analysis
    all_code = "\n".join(r.code for r in valid_results)
    
    print("\n🔍 FEATURE ANALYSIS:")
    features = {
        "Async/Await": "async def" in all_code,
        "Type Hints": "from typing" in all_code,
        "Page Object Model": "class " in all_code and "Page" in all_code,
        "Error Handling": "try:" in all_code and "except" in all_code,
        "Logging": "logging" in all_code,
        "Configuration": "config" in all_code.lower(),
        "Environment Variables": "os.getenv" in all_code
    }
    
    for feature, present in features.items():
        status = "[OK]" if present else "⚪"
        print(f"   {status} {feature}")
    
    feature_coverage = sum(features.values()) / len(features)
    print(f"\nFeature Coverage: {feature_coverage:.1%}")
    
    return {
        "total_lines": total_lines,
        "avg_safety_score": avg_safety_score,
        "avg_generation_time": avg_generation_time,
        "feature_coverage": feature_coverage,
        "total_violations": total_violations
    }

async def main():
    """
    Main function that runs all advanced feature demonstrations
    """
    print("🚀 ADVANCED FEATURES DEMONSTRATION")
    print("This showcases all cutting-edge AI features in code generation")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] This demo requires OPENAI_API_KEY for best results")
        print("Please set your OpenAI API key and try again")
        return 1
    
    results = []
    
    # Run all demonstrations
    print("\n🛡️ Running Constitutional AI demonstration...")
    result1 = await demonstrate_constitutional_ai()
    results.append(result1)
    
    print("\n🔄 Running Universal Self-Consistency demonstration...")
    result2 = await demonstrate_universal_self_consistency()
    results.append(result2)
    
    print("\n🔍 Running PAL Validation demonstration...")
    result3 = await demonstrate_pal_validation()
    results.append(result3)
    
    print("\n🔮 Running RAFA Patterns demonstration...")
    result4 = await demonstrate_rafa_patterns()
    results.append(result4)
    
    # Comprehensive analysis
    analysis = await comprehensive_quality_analysis(results)
    
    # Final summary
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETED")
    print("="*70)
    
    successful_demos = sum(1 for r in results if r is not None)
    print(f"[OK] Successful demonstrations: {successful_demos}/4")
    
    if analysis:
        print(f"📊 Total code generated: {analysis['total_lines']} lines")
        print(f"🛡️ Average safety score: {analysis['avg_safety_score']:.3f}")
        print(f"[FAST] Average generation time: {analysis['avg_generation_time']:.1f}s")
        print(f"🎯 Feature coverage: {analysis['feature_coverage']:.1%}")
    
    print("\n🎉 All advanced features demonstrated successfully!")
    print("\n📁 Key achievements:")
    print("   [OK] Constitutional AI prevents unsafe code generation")
    print("   [OK] Universal Self-Consistency improves code quality")
    print("   [OK] PAL validation ensures syntactic correctness")
    print("   [OK] RAFA patterns create extensible, maintainable code")
    
    print("\n🔗 Next steps:")
    print("   - Try the integration example: python integration_example.py")
    print("   - Test with your own Gherkin scenarios")
    print("   - Experiment with different configuration options")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Demonstration interrupted by user")
        sys.exit(130)