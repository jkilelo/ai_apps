# LLM Strategy Cookbook for QA Engineers

## Strategy Quick Reference Card

### Decision Tree for Strategy Selection
```
Start Here
    |
    Is it exploratory?
    ├─ Yes → Socratic Method
    └─ No → Continue
            |
            Need multiple solutions?
            ├─ Yes → Self-Consistency / Tree of Thoughts
            └─ No → Continue
                    |
                    Is it security-related?
                    ├─ Yes → Constitutional AI
                    └─ No → Continue
                            |
                            Need step-by-step reasoning?
                            ├─ Yes → Chain of Thought
                            └─ No → Continue
                                    |
                                    Complex API/Integration?
                                    ├─ Yes → Decomposed
                                    └─ No → Default (Chain of Thought)
```

## 21 Strategies with Real QA Examples

### 1. Chain of Thought (CoT)
**When to Use**: Need detailed step-by-step test cases with clear reasoning

```python
# Example: Testing a multi-step checkout process
from llm import query_llm, StrategyType

def test_checkout_flow():
    prompt = """
    Create detailed test steps for an e-commerce checkout:
    1. Add items to cart
    2. Apply discount code
    3. Enter shipping details
    4. Select payment method
    5. Complete order
    
    Think through each step systematically.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT)
    return response.content

# Output includes reasoning like:
# "First, I'll test adding items to cart because..."
# "Next, I need to verify discount calculations because..."
```

### 2. Tree of Thoughts (ToT)
**When to Use**: Finding all possible test paths and edge cases

```python
# Example: Testing all paths in a user registration flow
def find_registration_paths():
    prompt = """
    Map all possible paths through user registration:
    - Email vs Social login
    - Required vs optional fields
    - Validation errors
    - Success paths
    
    Explore each branch thoroughly.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.TREE_OF_THOUGHTS)
    return response.content

# Output explores multiple paths:
# Path 1: Email → Valid → Success
# Path 2: Email → Invalid → Error → Retry
# Path 3: Social → Facebook → Permissions → Success
```

### 3. Graph of Thoughts (GoT)
**When to Use**: Complex interconnected test scenarios

```python
# Example: Testing microservices interactions
def test_microservice_graph():
    prompt = """
    Test interactions between:
    - User Service
    - Order Service
    - Payment Service
    - Notification Service
    
    Consider all connections and dependencies.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.GRAPH_OF_THOUGHTS)
    return response.content

# Output shows relationships:
# User → Order (authentication)
# Order → Payment (transaction)
# Payment → Notification (confirmation)
# Order ← → Inventory (stock check)
```

### 4. Least to Most
**When to Use**: Building test complexity gradually

```python
# Example: Testing from basic to advanced search features
def progressive_search_tests():
    prompt = """
    Generate search tests starting simple:
    1. Single keyword
    2. Multiple keywords
    3. Filters
    4. Advanced operators
    5. Combined complex queries
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.LEAST_TO_MOST)
    return response.content

# Output builds complexity:
# Level 1: Test "shoes" returns products
# Level 2: Test "red shoes" filters correctly
# Level 3: Test price filter 50-100
# Level 4: Test "shoes" AND (red OR blue) NOT suede
```

### 5. Step Back
**When to Use**: Understanding the bigger testing picture

```python
# Example: Identifying core testing principles
def identify_test_categories():
    prompt = """
    User reported: "App crashes when uploading large photos"
    
    Step back - what categories of testing should we consider?
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.STEP_BACK)
    return response.content

# Output identifies broader categories:
# - Performance Testing (file size limits)
# - Memory Management Testing
# - Error Handling Testing
# - UI Responsiveness Testing
```

### 6. Decomposed
**When to Use**: Breaking down complex test scenarios

```python
# Example: API integration testing
def decompose_api_tests():
    prompt = """
    Test complete API flow:
    POST /user → GET /user/{id} → PUT /user/{id} → DELETE /user/{id}
    
    Break down into testable components.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.DECOMPOSED)
    return response.content

# Output decomposes into:
# Component 1: Authentication tests
# Component 2: Input validation tests
# Component 3: Status code tests
# Component 4: Response format tests
# Component 5: Error handling tests
```

### 7. Retrieval Augmented Generation (RAG)
**When to Use**: Testing with domain knowledge

```python
# Example: Testing with compliance requirements
def compliance_tests(regulations):
    prompt = "Generate GDPR compliance tests for user data handling"
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(
        messages, 
        strategy=StrategyType.RETRIEVAL_AUGMENTED,
        knowledge=regulations  # External GDPR documentation
    )
    return response.content

# Output includes specific regulations:
# Test: Right to erasure (Article 17)
# Test: Data portability (Article 20)
# Test: Consent withdrawal (Article 7)
```

### 8. Generated Knowledge
**When to Use**: Creating test context and background

```python
# Example: Generating test personas
def generate_test_personas():
    prompt = """
    Generate user personas for accessibility testing:
    - Vision impaired users
    - Motor impaired users
    - Cognitive impairments
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.GENERATED_KNOWLEDGE)
    return response.content

# Output creates detailed personas:
# Persona 1: John, 67, macular degeneration, uses screen reader
# Persona 2: Maria, 45, arthritis, uses keyboard navigation
# Persona 3: Sam, 28, dyslexia, needs clear fonts
```

### 9. Knowledge Graph
**When to Use**: Mapping test relationships and dependencies

```python
# Example: Test dependency mapping
def map_test_dependencies():
    prompt = """
    Map test dependencies for e-commerce platform:
    - User tests
    - Product tests
    - Cart tests
    - Payment tests
    - Order tests
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.KNOWLEDGE_GRAPH)
    return response.content

# Output shows relationships:
# User(login) → Cart(add) → Payment(process) → Order(confirm)
# Product(search) → Product(view) → Cart(add)
# User(profile) → Order(history)
```

### 10. Self-Consistency
**When to Use**: Generating multiple valid test datasets

```python
# Example: Creating diverse test data
def generate_test_datasets():
    prompt = """
    Generate 5 different valid test datasets for user registration:
    - Different age groups
    - Different locations
    - Different email providers
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.SELF_CONSISTENCY)
    return response.content

# Output provides variations:
# Dataset 1: john25@gmail.com, 25, USA
# Dataset 2: maria.garcia@yahoo.es, 45, Spain
# Dataset 3: sakura.tanaka@docomo.jp, 33, Japan
# All valid but diverse
```

### 11. Self-Refine
**When to Use**: Improving test cases iteratively

```python
# Example: Refining test automation code
def refine_test_code(initial_code):
    prompt = f"""
    Improve this Playwright test:
    {initial_code}
    
    Make it more robust and maintainable.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.SELF_REFINE)
    return response.content

# Output iteratively improves:
# Iteration 1: Add proper waits
# Iteration 2: Add error handling
# Iteration 3: Add logging
# Iteration 4: Add retry logic
```

### 12. Self-Verification
**When to Use**: Validating test correctness

```python
# Example: Verifying test coverage
def verify_test_coverage(test_cases, requirements):
    prompt = f"""
    Verify these test cases cover all requirements:
    
    Requirements: {requirements}
    Test Cases: {test_cases}
    
    Check for gaps and validate coverage.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.SELF_VERIFICATION)
    return response.content

# Output verifies:
# Requirement 1: ✓ Covered by Test 1, 2, 3
# Requirement 2: ✗ Missing negative test
# Requirement 3: ✓ Fully covered
# Coverage: 85%
```

### 13. ReAct
**When to Use**: Systematic bug reproduction

```python
# Example: Debugging test failures
def debug_test_failure(error_log):
    prompt = f"""
    Debug this test failure:
    {error_log}
    
    Think, then act, then observe results.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.REACT)
    return response.content

# Output follows pattern:
# Thought: Element not found suggests timing issue
# Action: Add explicit wait for element
# Observation: Element appears after 2 seconds
# Thought: Need to increase timeout
# Action: Set timeout to 5 seconds
# Result: Test passes
```

### 14. Reflexion
**When to Use**: Learning from test failures

```python
# Example: Improving test strategy from failures
def learn_from_failures(test_history):
    prompt = f"""
    Previous test failures:
    {test_history}
    
    Reflect and improve test approach.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.REFLEXION)
    return response.content

# Output reflects and learns:
# Attempt 1: Failed - timing issues
# Reflection: Need better synchronization
# Attempt 2: Failed - data dependencies
# Reflection: Need test data isolation
# Improved Approach: Use fixtures and proper waits
```

### 15. Chain of Verification
**When to Use**: Ensuring test accuracy

```python
# Example: Validating security test results
def verify_security_tests(test_results):
    prompt = f"""
    Verify these security test results are accurate:
    {test_results}
    
    Check each claim step by step.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_VERIFICATION)
    return response.content

# Output verifies each step:
# Claim: SQL injection blocked
# Verification Step 1: Check input sanitization
# Verification Step 2: Check parameterized queries
# Verification Step 3: Check error messages
# Verified: TRUE with evidence
```

### 16. Hypothetical Document
**When to Use**: Creating ideal test documentation

```python
# Example: Generating test plan template
def create_test_plan():
    prompt = """
    Create the perfect test plan document for a mobile banking app.
    What would this document contain?
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.HYPOTHETICAL_DOCUMENT)
    return response.content

# Output creates ideal document:
# 1. Executive Summary
# 2. Test Objectives
# 3. Scope and Features
# 4. Test Strategy
# 5. Risk Assessment
# 6. Test Schedule
# [Complete structure]
```

### 17. Analogical Reasoning
**When to Use**: Applying known patterns to new scenarios

```python
# Example: Testing new feature based on similar ones
def test_by_analogy(new_feature, similar_feature):
    prompt = f"""
    New feature: {new_feature}
    Similar to: {similar_feature}
    
    Apply test patterns from similar feature.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.ANALOGICAL_REASONING)
    return response.content

# Output applies patterns:
# Instagram Stories → WhatsApp Status
# Test patterns to apply:
# - 24-hour expiration
# - Privacy settings
# - Media upload limits
# - View tracking
```

### 18. Socratic Method
**When to Use**: Exploratory testing through questions

```python
# Example: Exploring feature behavior
def exploratory_testing(feature):
    prompt = f"""
    Explore {feature} by asking questions:
    What if...? Why does...? How would...?
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.SOCRATIC_METHOD)
    return response.content

# Output asks probing questions:
# What if user has no internet during upload?
# Why does the button remain clickable after submission?
# How would system handle 1000 concurrent uploads?
# What happens if user closes app mid-upload?
```

### 19. Meta-Prompting
**When to Use**: Optimizing test generation approach

```python
# Example: Finding best test strategy
def optimize_test_approach(testing_goal):
    prompt = f"""
    Goal: {testing_goal}
    
    What's the best way to approach testing this?
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.META_PROMPTING)
    return response.content

# Output optimizes approach:
# Analyzing goal: Performance testing for Black Friday
# Best approach:
# 1. Use production-like data
# 2. Simulate gradual load increase
# 3. Focus on checkout funnel
# 4. Monitor specific metrics
```

### 20. Prompt Optimization
**When to Use**: Improving test generation quality

```python
# Example: Refining test generation prompts
def optimize_prompt(initial_prompt):
    prompt = f"""
    Improve this test generation prompt:
    {initial_prompt}
    
    Make it clearer and more specific.
    """
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(messages, strategy=StrategyType.PROMPT_OPTIMIZATION)
    return response.content

# Output improves prompt:
# Original: "Test login"
# Optimized: "Generate 10 test cases for login functionality including:
# - Valid credentials
# - Invalid credentials
# - SQL injection attempts
# - Rate limiting
# - Session management
# Format as: Test ID | Description | Steps | Expected Result"
```

### 21. Constitutional AI
**When to Use**: Ethical and compliant testing

```python
# Example: Security testing with constraints
def ethical_security_tests():
    prompt = "Generate penetration test cases for production system"
    
    principles = [
        "Never cause permanent damage",
        "Only test authorized systems",
        "Avoid disrupting real users",
        "Report findings responsibly"
    ]
    
    messages = [{"role": "user", "content": prompt}]
    response = query_llm(
        messages,
        strategy=StrategyType.CONSTITUTIONAL_AI,
        principles=principles
    )
    return response.content

# Output follows principles:
# Test 1: Check for XSS (read-only, no data modification)
# Test 2: Verify auth tokens (own session only)
# Test 3: Test rate limits (stay within threshold)
# All tests comply with ethical guidelines
```

## Strategy Combinations

### Power Combos for Complex Testing

#### Combo 1: Complete Test Suite Generation
```python
def generate_complete_suite(feature):
    # Step 1: Understand the big picture
    context = query_llm(
        [{"role": "user", "content": f"Understand {feature}"}],
        strategy=StrategyType.STEP_BACK
    )
    
    # Step 2: Generate test scenarios
    scenarios = query_llm(
        [{"role": "user", "content": f"Test scenarios for {context.content}"}],
        strategy=StrategyType.TREE_OF_THOUGHTS
    )
    
    # Step 3: Create detailed test cases
    test_cases = query_llm(
        [{"role": "user", "content": f"Detail tests for {scenarios.content}"}],
        strategy=StrategyType.CHAIN_OF_THOUGHT
    )
    
    # Step 4: Verify coverage
    verification = query_llm(
        [{"role": "user", "content": f"Verify {test_cases.content}"}],
        strategy=StrategyType.SELF_VERIFICATION
    )
    
    return {
        'context': context.content,
        'scenarios': scenarios.content,
        'test_cases': test_cases.content,
        'verification': verification.content
    }
```

#### Combo 2: Bug Analysis Pipeline
```python
def analyze_bug_completely(bug_report):
    # Step 1: Systematic reproduction
    reproduction = query_llm(
        [{"role": "user", "content": f"Reproduce: {bug_report}"}],
        strategy=StrategyType.REACT
    )
    
    # Step 2: Root cause analysis
    root_cause = query_llm(
        [{"role": "user", "content": f"Find root cause: {reproduction.content}"}],
        strategy=StrategyType.DECOMPOSED
    )
    
    # Step 3: Learn from failure
    learning = query_llm(
        [{"role": "user", "content": f"Learn from: {root_cause.content}"}],
        strategy=StrategyType.REFLEXION
    )
    
    return {
        'reproduction_steps': reproduction.content,
        'root_cause': root_cause.content,
        'prevention': learning.content
    }
```

## Performance Benchmarks

### Strategy Performance Comparison

| Strategy | Speed | Quality | Best For |
|----------|-------|---------|----------|
| Chain of Thought | Medium (3-4s) | High | Detailed test steps |
| Tree of Thoughts | Slow (4-5s) | Very High | Edge case discovery |
| Self-Consistency | Slow (4-5s) | High | Test data generation |
| Constitutional AI | Fast (1-2s) | High | Security testing |
| ReAct | Medium (3-4s) | High | Bug reproduction |
| Socratic Method | Medium (3-4s) | High | Exploratory testing |
| Meta-Prompting | Medium (3-4s) | High | Strategy optimization |

## Quick Start Templates

### Template 1: Functional Test Generation
```python
template_functional = """
Generate functional test cases for: {feature}

Include:
- Positive test cases
- Negative test cases  
- Boundary value tests
- Error handling tests

Format:
Test ID: TC-XXX
Description: [What is being tested]
Preconditions: [Setup required]
Steps:
1. [Step 1]
2. [Step 2]
Expected Result: [What should happen]
"""
```

### Template 2: Security Test Generation
```python
template_security = """
Generate security test cases for: {feature}

Cover OWASP Top 10:
- Injection attacks
- Authentication tests
- Authorization tests
- Data exposure tests
- XSS attempts

Include safe payloads only.
"""
```

### Template 3: Performance Test Generation
```python
template_performance = """
Generate performance test scenarios for: {feature}

Include:
- Load testing (expected load)
- Stress testing (breaking point)
- Spike testing (sudden increase)
- Endurance testing (sustained load)

Specify:
- User count
- Request rate
- Duration
- Success criteria
"""
```

## Tips and Tricks

### 1. Temperature Tuning
```python
# Lower temperature for consistency
test_steps = query_llm(messages, temperature=0.2)  # Deterministic

# Higher temperature for creativity
edge_cases = query_llm(messages, temperature=0.8)  # Creative
```

### 2. Token Management
```python
# Estimate tokens needed
def estimate_tokens(test_complexity):
    return {
        'simple': 500,
        'medium': 1500,
        'complex': 3000,
        'comprehensive': 4000
    }[test_complexity]
```

### 3. Prompt Engineering Tips
- Be specific about format requirements
- Include examples when possible
- Ask for reasoning when needed
- Request structured output (JSON, tables)
- Set clear boundaries and constraints

## Common Pitfalls to Avoid

1. **Wrong Strategy Selection**
   - Don't use Tree of Thoughts for simple yes/no questions
   - Don't use Constitutional AI for non-ethical concerns

2. **Over-Engineering**
   - Start simple with Chain of Thought
   - Add complexity only when needed

3. **Ignoring Temperature**
   - Too high: Inconsistent results
   - Too low: Lack of creativity

4. **Token Waste**
   - Be concise in prompts
   - Request only what you need
   - Use streaming for long responses

5. **Missing Context**
   - Always provide sufficient background
   - Include relevant constraints
   - Specify output format

---
*Remember: The right strategy can improve test quality by 10x. Choose wisely!*