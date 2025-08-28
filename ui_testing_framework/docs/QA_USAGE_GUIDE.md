# QA Engineer's Guide to LLM-Powered Test Generation

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Strategy Selection Guide](#strategy-selection-guide)
4. [Real-World QA Use Cases](#real-world-qa-use-cases)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)
7. [Performance Optimization](#performance-optimization)

## Overview

This guide demonstrates how QA Engineers can leverage 21 research-backed prompt strategies to generate comprehensive test cases, analyze applications, and automate testing workflows using the unified LLM module.

### Why Use LLM for Test Generation?
- **Coverage**: AI can identify edge cases humans might miss
- **Speed**: Generate hundreds of test cases in minutes
- **Consistency**: Uniform test structure and quality
- **Intelligence**: Context-aware test generation based on application behavior

## Quick Start

### Basic Setup
```python
from llm import query_llm, StrategyType
from pathlib import Path

# Simple test case generation
messages = [{
    "role": "user",
    "content": "Generate test cases for a login form with email and password fields"
}]

# Using Chain of Thought for detailed test steps
response = query_llm(
    messages,
    strategy=StrategyType.CHAIN_OF_THOUGHT
)
print(response.content)
```

### Loading Environment
```python
# API keys are auto-loaded from .env file
# Ensure .env contains:
# GOOGLE_API_KEY=your_key
# OPENAI_API_KEY=your_key
# ANTHROPIC_API_KEY=your_key
```

## Strategy Selection Guide

### Decision Matrix for QA Tasks

| QA Task | Best Strategy | Why Use It | Example Output |
|---------|--------------|------------|----------------|
| **Test Case Generation** | Chain of Thought | Step-by-step reasoning | Detailed test steps with rationale |
| **Edge Case Discovery** | Tree of Thoughts | Explores multiple paths | Comprehensive edge cases |
| **Test Data Generation** | Self-Consistency | Multiple valid datasets | Diverse test data sets |
| **Bug Reproduction** | ReAct | Thought-Action-Observation | Systematic reproduction steps |
| **Test Prioritization** | Least to Most | Builds complexity gradually | Risk-based test ordering |
| **Security Testing** | Constitutional AI | Applies security principles | Ethical security test cases |
| **API Testing** | Decomposed | Breaks down complex flows | Modular API test scenarios |
| **Performance Testing** | Meta-Prompting | Optimizes test approach | Performance test strategies |
| **Regression Testing** | Self-Verification | Validates test accuracy | Self-checking test suites |
| **Exploratory Testing** | Socratic Method | Question-driven exploration | Investigative test paths |

## Real-World QA Use Cases

### 1. Comprehensive Test Suite Generation

#### Use Case: E-commerce Checkout Flow
```python
from llm import query_llm, StrategyType

def generate_ecommerce_test_suite():
    """Generate comprehensive test suite for checkout flow"""
    
    messages = [{
        "role": "system",
        "content": "You are a Senior QA Engineer with 20+ years experience in e-commerce testing."
    }, {
        "role": "user",
        "content": """Generate comprehensive test cases for an e-commerce checkout flow with:
        - Cart management
        - Guest and registered checkout
        - Multiple payment methods (credit card, PayPal, Apple Pay)
        - Shipping options
        - Promo codes
        - Order confirmation
        
        Include positive, negative, edge cases, and security tests."""
    }]
    
    # Use Tree of Thoughts to explore all test paths
    response = query_llm(
        messages,
        strategy=StrategyType.TREE_OF_THOUGHTS,
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.content

# Execute
test_suite = generate_ecommerce_test_suite()
print(test_suite)
```

### 2. Intelligent Bug Analysis

#### Use Case: Analyzing Production Bug Reports
```python
def analyze_bug_report(bug_description, logs):
    """Analyze bug report and generate reproduction steps"""
    
    messages = [{
        "role": "system",
        "content": "You are a QA expert specializing in bug analysis and reproduction."
    }, {
        "role": "user",
        "content": f"""Analyze this bug report and provide:
        1. Root cause analysis
        2. Step-by-step reproduction steps
        3. Expected vs actual behavior
        4. Test cases to prevent regression
        
        Bug Description: {bug_description}
        
        Error Logs:
        {logs}
        """
    }]
    
    # Use ReAct for systematic analysis
    response = query_llm(
        messages,
        strategy=StrategyType.REACT,
        temperature=0.3  # Lower temperature for accuracy
    )
    
    return response.content

# Example usage
bug = "Users report checkout fails when applying promo code after adding items from wishlist"
logs = "TypeError: Cannot read property 'discount' of undefined at CheckoutService.applyPromo()"
analysis = analyze_bug_report(bug, logs)
```

### 3. Test Data Generation with Validation

#### Use Case: Generating Realistic Test Data
```python
def generate_test_data(data_requirements):
    """Generate diverse test data sets with validation rules"""
    
    messages = [{
        "role": "user",
        "content": f"""Generate comprehensive test data for:
        {data_requirements}
        
        Include:
        - Valid boundary values
        - Invalid boundary values
        - Edge cases
        - SQL injection attempts
        - XSS payloads
        - Unicode and special characters
        - Null and empty values
        
        Format as JSON with 'category' and 'test_data' fields."""
    }]
    
    # Use Self-Consistency for multiple valid datasets
    response = query_llm(
        messages,
        strategy=StrategyType.SELF_CONSISTENCY,
        temperature=0.9  # Higher for diversity
    )
    
    return response.content

# Example
requirements = """
- Email field (max 255 chars)
- Password field (8-50 chars, must include uppercase, lowercase, number, special char)
- Age field (13-120)
- Phone number (international formats)
"""
test_data = generate_test_data(requirements)
```

### 4. API Test Scenario Generation

#### Use Case: REST API Testing
```python
def generate_api_tests(api_spec):
    """Generate API test scenarios from OpenAPI/Swagger spec"""
    
    messages = [{
        "role": "system",
        "content": "You are an API testing expert. Generate thorough test scenarios."
    }, {
        "role": "user",
        "content": f"""Generate API test cases for this endpoint:
        {api_spec}
        
        Include tests for:
        - All HTTP methods
        - Status codes (2xx, 4xx, 5xx)
        - Request/response validation
        - Authentication/authorization
        - Rate limiting
        - Pagination
        - Filtering and sorting
        - Concurrent requests
        - Large payloads
        - Malformed requests
        """
    }]
    
    # Use Decomposed strategy for complex API flows
    response = query_llm(
        messages,
        strategy=StrategyType.DECOMPOSED,
        max_tokens=3000
    )
    
    return response.content

# Example
api_spec = """
POST /api/v1/users
Creates a new user account
Body: { email, password, firstName, lastName, role }
Auth: Bearer token required
Returns: { userId, email, createdAt }
"""
api_tests = generate_api_tests(api_spec)
```

### 5. Security Test Case Generation

#### Use Case: OWASP Top 10 Testing
```python
def generate_security_tests(application_type, tech_stack):
    """Generate security test cases based on OWASP guidelines"""
    
    messages = [{
        "role": "system",
        "content": "You are a security testing expert. Follow OWASP testing guide."
    }, {
        "role": "user",
        "content": f"""Generate security test cases for:
        Application Type: {application_type}
        Tech Stack: {tech_stack}
        
        Cover OWASP Top 10:
        1. Injection
        2. Broken Authentication
        3. Sensitive Data Exposure
        4. XML External Entities (XXE)
        5. Broken Access Control
        6. Security Misconfiguration
        7. Cross-Site Scripting (XSS)
        8. Insecure Deserialization
        9. Using Components with Known Vulnerabilities
        10. Insufficient Logging & Monitoring
        
        Provide specific test cases with payloads."""
    }]
    
    # Use Constitutional AI for ethical security testing
    principles = [
        "Test only in authorized environments",
        "Do not cause permanent damage",
        "Report findings responsibly"
    ]
    
    response = query_llm(
        messages,
        strategy=StrategyType.CONSTITUTIONAL_AI,
        principles=principles
    )
    
    return response.content

# Example
security_tests = generate_security_tests(
    application_type="E-commerce Web App",
    tech_stack="React, Node.js, MongoDB"
)
```

### 6. Performance Test Scenario Design

#### Use Case: Load Testing Strategy
```python
def design_performance_tests(system_architecture, expected_load):
    """Design comprehensive performance test scenarios"""
    
    messages = [{
        "role": "user",
        "content": f"""Design performance test scenarios for:
        
        System Architecture: {system_architecture}
        Expected Load: {expected_load}
        
        Include:
        1. Load testing scenarios
        2. Stress testing thresholds
        3. Spike testing patterns
        4. Endurance testing duration
        5. Volume testing data sizes
        6. Scalability testing approach
        7. Key performance metrics to monitor
        8. Success criteria
        """
    }]
    
    # Use Meta-Prompting to optimize test approach
    response = query_llm(
        messages,
        strategy=StrategyType.META_PROMPTING
    )
    
    return response.content

# Example
perf_tests = design_performance_tests(
    system_architecture="Microservices with API Gateway, 3 services, Redis cache, PostgreSQL",
    expected_load="10,000 concurrent users, 100 requests/second peak"
)
```

### 7. Accessibility Testing Checklist

#### Use Case: WCAG Compliance Testing
```python
def generate_accessibility_tests(ui_components):
    """Generate accessibility test cases for WCAG compliance"""
    
    messages = [{
        "role": "user",
        "content": f"""Generate accessibility test cases for these UI components:
        {ui_components}
        
        Cover WCAG 2.1 Level AA requirements:
        - Keyboard navigation
        - Screen reader compatibility
        - Color contrast ratios
        - Focus indicators
        - ARIA labels and roles
        - Alt text for images
        - Form field labels
        - Error identification
        - Time limits
        - Responsive design
        
        Provide specific test steps and expected results."""
    }]
    
    # Use Step Back for comprehensive coverage
    response = query_llm(
        messages,
        strategy=StrategyType.STEP_BACK
    )
    
    return response.content

# Example
components = """
- Login form
- Navigation menu
- Data table with sorting
- Modal dialogs
- Image carousel
- Search with autocomplete
"""
accessibility_tests = generate_accessibility_tests(components)
```

### 8. Mobile App Testing Scenarios

#### Use Case: Cross-Platform Mobile Testing
```python
def generate_mobile_tests(app_features, platforms):
    """Generate mobile app test scenarios"""
    
    messages = [{
        "role": "user",
        "content": f"""Generate mobile app test cases for:
        
        Features: {app_features}
        Platforms: {platforms}
        
        Include tests for:
        - Different screen sizes and resolutions
        - Portrait/landscape orientation
        - Network conditions (WiFi, 4G, 3G, offline)
        - Battery consumption
        - Memory usage
        - App permissions
        - Push notifications
        - Background/foreground transitions
        - Gestures (swipe, pinch, long press)
        - Device-specific features (camera, GPS, biometrics)
        - App installation/update/uninstallation
        - Interruptions (calls, messages)
        """
    }]
    
    # Use Graph of Thoughts for complex mobile scenarios
    response = query_llm(
        messages,
        strategy=StrategyType.GRAPH_OF_THOUGHTS
    )
    
    return response.content

# Example
mobile_tests = generate_mobile_tests(
    app_features="Social media app with photo sharing, messaging, live streaming",
    platforms="iOS 14+, Android 10+"
)
```

### 9. Regression Test Prioritization

#### Use Case: Risk-Based Test Selection
```python
def prioritize_regression_tests(changed_modules, test_history):
    """Prioritize regression tests based on risk and impact"""
    
    messages = [{
        "role": "user",
        "content": f"""Prioritize regression tests based on:
        
        Changed Modules: {changed_modules}
        Test History: {test_history}
        
        Provide:
        1. Critical path tests (P0)
        2. High-risk area tests (P1)
        3. Integration tests (P2)
        4. Edge case tests (P3)
        
        For each priority level, explain the risk and impact.
        Suggest optimal execution order and parallelization strategy."""
    }]
    
    # Use Least to Most for gradual complexity
    response = query_llm(
        messages,
        strategy=StrategyType.LEAST_TO_MOST
    )
    
    return response.content

# Example
priorities = prioritize_regression_tests(
    changed_modules="Payment gateway integration, User authentication, Email service",
    test_history="Last release: 5 critical bugs in payment, 2 in auth, 0 in email"
)
```

### 10. Exploratory Testing Charter

#### Use Case: Guided Exploratory Testing
```python
def create_exploratory_charter(feature, time_box):
    """Create exploratory testing charter with focus areas"""
    
    messages = [{
        "role": "user",
        "content": f"""Create an exploratory testing charter for:
        
        Feature: {feature}
        Time Box: {time_box}
        
        Include:
        - Mission statement
        - Areas of focus
        - Test ideas to explore
        - Risks to investigate
        - Questions to answer
        - Heuristics to apply (SFDIPOT, CRUSSPIC STMPL)
        - Notes template
        - Bug reporting guidelines
        """
    }]
    
    # Use Socratic Method for investigative approach
    response = query_llm(
        messages,
        strategy=StrategyType.SOCRATIC_METHOD
    )
    
    return response.content

# Example
charter = create_exploratory_charter(
    feature="New AI-powered product recommendation engine",
    time_box="2 hours"
)
```

## Code Examples

### Complete Test Generation Pipeline
```python
import json
from datetime import datetime
from llm import query_llm, stream_llm, StrategyType

class TestCaseGenerator:
    """Comprehensive test case generator using LLM strategies"""
    
    def __init__(self):
        self.strategies = {
            'functional': StrategyType.CHAIN_OF_THOUGHT,
            'edge_cases': StrategyType.TREE_OF_THOUGHTS,
            'security': StrategyType.CONSTITUTIONAL_AI,
            'performance': StrategyType.META_PROMPTING,
            'exploratory': StrategyType.SOCRATIC_METHOD,
        }
    
    def generate_test_suite(self, requirements, test_types=['functional']):
        """Generate complete test suite from requirements"""
        
        test_suite = {
            'generated_at': datetime.now().isoformat(),
            'requirements': requirements,
            'test_cases': {}
        }
        
        for test_type in test_types:
            strategy = self.strategies.get(test_type, StrategyType.CHAIN_OF_THOUGHT)
            
            messages = [{
                "role": "system",
                "content": f"You are a Senior QA Engineer generating {test_type} tests."
            }, {
                "role": "user",
                "content": f"Generate {test_type} test cases for: {requirements}"
            }]
            
            response = query_llm(messages, strategy=strategy)
            test_suite['test_cases'][test_type] = response.content
        
        return test_suite
    
    def generate_test_data(self, test_case):
        """Generate test data for specific test case"""
        
        messages = [{
            "role": "user",
            "content": f"Generate test data for: {test_case}"
        }]
        
        response = query_llm(
            messages,
            strategy=StrategyType.SELF_CONSISTENCY,
            temperature=0.9
        )
        
        return response.content
    
    def generate_automation_code(self, test_case, framework='playwright'):
        """Generate automation code for test case"""
        
        messages = [{
            "role": "system",
            "content": f"Generate {framework} test automation code."
        }, {
            "role": "user",
            "content": f"Convert to {framework} code: {test_case}"
        }]
        
        response = query_llm(
            messages,
            strategy=StrategyType.SELF_REFINE
        )
        
        return response.content

# Usage example
generator = TestCaseGenerator()

# Generate comprehensive test suite
requirements = """
User Registration Form:
- Email (required, must be valid)
- Password (min 8 chars, must include uppercase, lowercase, number, special char)
- Confirm Password (must match)
- Terms acceptance checkbox
- Optional newsletter subscription
- CAPTCHA validation
"""

test_suite = generator.generate_test_suite(
    requirements,
    test_types=['functional', 'edge_cases', 'security']
)

print(json.dumps(test_suite, indent=2))
```

### Streaming Test Generation for Real-Time Feedback
```python
def stream_test_generation(requirements):
    """Stream test case generation for real-time display"""
    
    messages = [{
        "role": "user",
        "content": f"Generate detailed test cases for: {requirements}"
    }]
    
    print("Generating test cases...")
    full_response = ""
    
    for chunk in stream_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT):
        if chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
        
        if chunk.is_final:
            print("\n[Generation Complete]")
            break
    
    return full_response

# Example with streaming
requirements = "Shopping cart with quantity updates, removal, and save for later"
streamed_tests = stream_test_generation(requirements)
```

### Async Parallel Test Generation
```python
import asyncio
from llm import aquery_llm, StrategyType

async def generate_parallel_tests(features):
    """Generate tests for multiple features in parallel"""
    
    async def generate_for_feature(feature):
        messages = [{
            "role": "user",
            "content": f"Generate test cases for: {feature}"
        }]
        
        response = await aquery_llm(
            messages,
            strategy=StrategyType.CHAIN_OF_THOUGHT
        )
        
        return {
            'feature': feature,
            'test_cases': response.content
        }
    
    # Generate tests for all features in parallel
    tasks = [generate_for_feature(f) for f in features]
    results = await asyncio.gather(*tasks)
    
    return results

# Example
features = [
    "Login with social media",
    "Password reset flow",
    "Two-factor authentication",
    "Session management"
]

# Run async generation
results = asyncio.run(generate_parallel_tests(features))
for result in results:
    print(f"\nFeature: {result['feature']}")
    print(f"Tests: {result['test_cases'][:200]}...")
```

### Image-Based Test Generation
```python
import base64
from pathlib import Path

def generate_tests_from_screenshot(image_path):
    """Generate test cases from UI screenshot"""
    
    # Load and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    messages = [{
        "role": "user",
        "content": "Analyze this UI screenshot and generate comprehensive test cases for all visible elements"
    }]
    
    response = query_llm(
        messages,
        images=[image_data],
        strategy=StrategyType.TREE_OF_THOUGHTS
    )
    
    return response.content

# Example
screenshot_path = Path("screenshots/checkout_page.png")
if screenshot_path.exists():
    visual_tests = generate_tests_from_screenshot(screenshot_path)
    print(visual_tests)
```

## Best Practices

### 1. Strategy Selection Guidelines
```python
def select_optimal_strategy(test_objective):
    """Select best strategy based on testing objective"""
    
    strategy_map = {
        'detailed_steps': StrategyType.CHAIN_OF_THOUGHT,
        'find_edge_cases': StrategyType.TREE_OF_THOUGHTS,
        'api_testing': StrategyType.DECOMPOSED,
        'security_testing': StrategyType.CONSTITUTIONAL_AI,
        'bug_analysis': StrategyType.REACT,
        'test_prioritization': StrategyType.LEAST_TO_MOST,
        'exploratory': StrategyType.SOCRATIC_METHOD,
        'performance': StrategyType.META_PROMPTING,
        'data_generation': StrategyType.SELF_CONSISTENCY,
        'code_generation': StrategyType.SELF_REFINE,
        'validation': StrategyType.SELF_VERIFICATION,
    }
    
    return strategy_map.get(test_objective, StrategyType.CHAIN_OF_THOUGHT)
```

### 2. Temperature Settings for QA Tasks
```python
# Temperature guidelines for different QA tasks
TEMPERATURE_SETTINGS = {
    'test_steps': 0.3,      # Low - Precise, deterministic steps
    'test_data': 0.9,       # High - Diverse, creative data
    'bug_analysis': 0.2,    # Very low - Accurate analysis
    'edge_cases': 0.7,      # Medium-high - Creative scenarios
    'automation_code': 0.1,  # Very low - Syntactically correct code
    'exploratory': 0.8,     # High - Creative exploration
}
```

### 3. Token Optimization
```python
def optimize_tokens(test_complexity):
    """Optimize token usage based on test complexity"""
    
    token_map = {
        'simple': 500,      # Basic test cases
        'medium': 1000,     # Standard test suites
        'complex': 2000,    # Comprehensive testing
        'extensive': 4000,  # Full coverage with examples
    }
    
    return token_map.get(test_complexity, 1000)
```

### 4. Error Handling Pattern
```python
def safe_test_generation(requirements, max_retries=3):
    """Generate tests with error handling and retries"""
    
    for attempt in range(max_retries):
        try:
            messages = [{
                "role": "user",
                "content": f"Generate test cases for: {requirements}"
            }]
            
            response = query_llm(
                messages,
                strategy=StrategyType.CHAIN_OF_THOUGHT,
                timeout=30
            )
            
            if response and response.content:
                return response.content
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

## Performance Optimization

### Caching Test Templates
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_test_template(test_type, complexity):
    """Cache common test templates for reuse"""
    
    messages = [{
        "role": "user",
        "content": f"Generate {test_type} test template for {complexity} scenarios"
    }]
    
    response = query_llm(messages)
    return response.content
```

### Batch Processing
```python
def batch_generate_tests(test_requirements_list, batch_size=5):
    """Process multiple test requirements in batches"""
    
    results = []
    
    for i in range(0, len(test_requirements_list), batch_size):
        batch = test_requirements_list[i:i + batch_size]
        
        # Combine batch into single request
        combined = "\n---\n".join([f"Feature {j+1}: {req}" 
                                   for j, req in enumerate(batch)])
        
        messages = [{
            "role": "user",
            "content": f"Generate test cases for each feature:\n{combined}"
        }]
        
        response = query_llm(
            messages,
            strategy=StrategyType.DECOMPOSED,
            max_tokens=4000
        )
        
        results.append(response.content)
    
    return results
```

## Conclusion

This guide provides QA Engineers with powerful AI-driven test generation capabilities using 21 research-backed strategies. By selecting the appropriate strategy for each testing scenario, QA teams can:

- Generate comprehensive test coverage faster
- Discover edge cases systematically
- Create realistic test data
- Automate test case creation
- Improve test quality and consistency

Remember: The LLM is a tool to augment, not replace, QA expertise. Always review and validate generated test cases before implementation.

---
*Last Updated: 2025-08-27*  
*Version: 1.0.0*  
*For questions or contributions, please refer to the main README*