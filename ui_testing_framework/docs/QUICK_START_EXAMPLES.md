# Quick Start Examples - LLM for QA Engineers

## 1-Minute Setup

```python
# Import the essentials
from llm import query_llm, StrategyType

# Your first test generation
messages = [{
    "role": "user",
    "content": "Generate 5 test cases for a login form"
}]

response = query_llm(messages)
print(response.content)
```

That's it! You're now using AI for test generation.

## Copy-Paste Examples

### Example 1: Generate Test Cases in 5 Lines
```python
from llm import query_llm, StrategyType

response = query_llm([{
    "role": "user", 
    "content": "Generate test cases for password reset with email verification"
}], strategy=StrategyType.CHAIN_OF_THOUGHT)

print(response.content)
```

### Example 2: Find Edge Cases Instantly
```python
from llm import query_llm, StrategyType

response = query_llm([{
    "role": "user",
    "content": "Find edge cases for date picker (birth date, 13-120 years old)"
}], strategy=StrategyType.TREE_OF_THOUGHTS)

print(response.content)
```

### Example 3: Generate Test Data
```python
from llm import query_llm, StrategyType

response = query_llm([{
    "role": "user",
    "content": "Generate 10 valid and 10 invalid email addresses for testing"
}], strategy=StrategyType.SELF_CONSISTENCY)

print(response.content)
```

### Example 4: Security Test Cases
```python
from llm import query_llm, StrategyType

response = query_llm([{
    "role": "user",
    "content": "Generate SQL injection test cases for login form (safe payloads only)"
}], strategy=StrategyType.CONSTITUTIONAL_AI, 
principles=["Only safe test payloads", "No actual exploitation"])

print(response.content)
```

### Example 5: API Test Generation
```python
from llm import query_llm, StrategyType

response = query_llm([{
    "role": "user",
    "content": """
    Generate test cases for REST API:
    POST /api/users - Create user
    Request: {email, password, name}
    Response: {id, email, created_at}
    """
}], strategy=StrategyType.DECOMPOSED)

print(response.content)
```

## Real-World Scenarios

### Scenario 1: Morning Standup - Quick Test Coverage Check
```python
from llm import query_llm, StrategyType

def quick_coverage_check(feature_description):
    """Generate test coverage checklist for standup"""
    
    response = query_llm([{
        "role": "user",
        "content": f"""
        Feature: {feature_description}
        
        Create quick test coverage checklist:
        - What's tested
        - What's not tested
        - Risk areas
        
        Keep it brief for standup discussion.
        """
    }], strategy=StrategyType.CHAIN_OF_THOUGHT, max_tokens=500)
    
    return response.content

# Usage
coverage = quick_coverage_check("New checkout flow with Apple Pay")
print(coverage)
```

### Scenario 2: Bug Triage - Rapid Analysis
```python
from llm import query_llm, StrategyType

def rapid_bug_analysis(bug_description):
    """Quick bug analysis for triage meeting"""
    
    response = query_llm([{
        "role": "user",
        "content": f"""
        Bug: {bug_description}
        
        Provide:
        1. Severity (Critical/High/Medium/Low)
        2. Likely cause
        3. Impact on users
        4. Quick test to verify
        
        Be concise - 2-3 sentences each.
        """
    }], strategy=StrategyType.REACT, max_tokens=300)
    
    return response.content

# Usage
analysis = rapid_bug_analysis("Cart total shows $0 after applying 100% discount code")
print(analysis)
```

### Scenario 3: Sprint Planning - Test Estimation
```python
from llm import query_llm, StrategyType

def estimate_testing_effort(user_stories):
    """Estimate testing effort for sprint planning"""
    
    response = query_llm([{
        "role": "user",
        "content": f"""
        User Stories:
        {user_stories}
        
        Estimate testing effort:
        - Number of test cases needed
        - Testing complexity (Simple/Medium/Complex)
        - Estimated hours
        - Risk factors
        
        Format as table.
        """
    }], strategy=StrategyType.LEAST_TO_MOST)
    
    return response.content

# Usage
stories = """
1. As a user, I want to filter products by price
2. As a user, I want to save items to wishlist
3. As an admin, I want to export user data
"""
estimate = estimate_testing_effort(stories)
print(estimate)
```

### Scenario 4: Production Issue - Emergency Test Plan
```python
from llm import query_llm, StrategyType

def emergency_test_plan(incident_description):
    """Generate emergency test plan for production issue"""
    
    response = query_llm([{
        "role": "user",
        "content": f"""
        Production Incident: {incident_description}
        
        Create emergency test plan:
        1. Immediate smoke tests (5 min)
        2. Critical path tests (15 min)
        3. Regression tests (30 min)
        
        Focus on preventing customer impact.
        """
    }], strategy=StrategyType.CHAIN_OF_THOUGHT, temperature=0.1)
    
    return response.content

# Usage
incident = "Payment gateway returning 500 errors intermittently"
plan = emergency_test_plan(incident)
print(plan)
```

### Scenario 5: Code Review - Test Coverage Gaps
```python
from llm import query_llm, StrategyType

def find_test_gaps(code_changes):
    """Identify test coverage gaps in code review"""
    
    response = query_llm([{
        "role": "user",
        "content": f"""
        Code changes:
        {code_changes}
        
        Identify:
        - Untested scenarios
        - Edge cases to cover
        - Integration points needing tests
        
        Priority order by risk.
        """
    }], strategy=StrategyType.TREE_OF_THOUGHTS)
    
    return response.content

# Usage
changes = """
- Added retry logic to payment processing
- Increased timeout from 30s to 60s
- Added fallback payment gateway
"""
gaps = find_test_gaps(changes)
print(gaps)
```

## Common QA Tasks - One-Liners

### Generate Test Cases
```python
tests = query_llm([{"role": "user", "content": "Test cases for forgot password"}]).content
```

### Find Edge Cases
```python
edges = query_llm([{"role": "user", "content": "Edge cases for file upload (max 10MB)"}], strategy=StrategyType.TREE_OF_THOUGHTS).content
```

### Create Test Data
```python
data = query_llm([{"role": "user", "content": "10 test credit card numbers (valid format, not real)"}]).content
```

### Write Bug Report
```python
report = query_llm([{"role": "user", "content": f"Write bug report: {issue_description}"}]).content
```

### Generate Assertions
```python
asserts = query_llm([{"role": "user", "content": f"Playwright assertions for {element}"}]).content
```

## Test Automation Code Generation

### Playwright Test Generation
```python
from llm import query_llm, StrategyType

def generate_playwright_test(test_case):
    response = query_llm([{
        "role": "system",
        "content": "Generate Playwright test code in Python"
    }, {
        "role": "user",
        "content": f"Convert to Playwright: {test_case}"
    }], strategy=StrategyType.SELF_REFINE)
    
    return response.content

# Usage
test = "Login with valid credentials and verify dashboard loads"
code = generate_playwright_test(test)
print(code)

# Output:
# async def test_valid_login(page):
#     await page.goto('https://example.com/login')
#     await page.fill('#email', 'test@example.com')
#     await page.fill('#password', 'Test123!')
#     await page.click('#login-button')
#     await expect(page).toHaveURL('/dashboard')
#     await expect(page.locator('.dashboard-header')).toBeVisible()
```

### Selenium Test Generation
```python
def generate_selenium_test(test_case):
    response = query_llm([{
        "role": "system",
        "content": "Generate Selenium WebDriver test code in Python"
    }, {
        "role": "user",
        "content": f"Convert to Selenium: {test_case}"
    }])
    
    return response.content
```

### Cypress Test Generation
```python
def generate_cypress_test(test_case):
    response = query_llm([{
        "role": "system",
        "content": "Generate Cypress test code in JavaScript"
    }, {
        "role": "user",
        "content": f"Convert to Cypress: {test_case}"
    }])
    
    return response.content
```

## Batch Processing Examples

### Process Multiple Features at Once
```python
from llm import query_llm, StrategyType

features = [
    "User registration",
    "Password reset",
    "Profile update",
    "Account deletion"
]

def batch_generate_tests(features):
    all_tests = {}
    
    for feature in features:
        response = query_llm([{
            "role": "user",
            "content": f"Generate 5 key test cases for {feature}"
        }], max_tokens=500)
        
        all_tests[feature] = response.content
    
    return all_tests

# Generate tests for all features
test_suite = batch_generate_tests(features)
for feature, tests in test_suite.items():
    print(f"\n{feature}:\n{tests}")
```

### Parallel Test Generation (Async)
```python
import asyncio
from llm import aquery_llm, StrategyType

async def generate_tests_parallel(features):
    async def gen_test(feature):
        response = await aquery_llm([{
            "role": "user",
            "content": f"Test cases for {feature}"
        }])
        return feature, response.content
    
    tasks = [gen_test(f) for f in features]
    results = await asyncio.gather(*tasks)
    return dict(results)

# Run in parallel
features = ["Login", "Logout", "Register"]
tests = asyncio.run(generate_tests_parallel(features))
```

## Interactive Testing Assistant

### Build Your Testing Chatbot
```python
from llm import query_llm, StrategyType

class TestingAssistant:
    def __init__(self):
        self.context = []
    
    def ask(self, question):
        self.context.append({"role": "user", "content": question})
        
        # Keep last 5 exchanges for context
        messages = [
            {"role": "system", "content": "You are a Senior QA Engineer assistant."}
        ] + self.context[-10:]
        
        response = query_llm(messages)
        self.context.append({"role": "assistant", "content": response.content})
        
        return response.content
    
    def reset(self):
        self.context = []

# Usage
qa = TestingAssistant()

print(qa.ask("What should I test for a shopping cart?"))
print(qa.ask("What about edge cases?"))
print(qa.ask("Generate specific test data for that"))
```

## Environment-Specific Examples

### Development Environment Testing
```python
def dev_smoke_tests(feature_branch):
    return query_llm([{
        "role": "user",
        "content": f"""
        Feature branch: {feature_branch}
        Generate quick smoke tests for dev environment.
        Focus on new functionality only.
        """
    }], max_tokens=500).content
```

### Staging Environment Testing
```python
def staging_regression_tests(release_version):
    return query_llm([{
        "role": "user",
        "content": f"""
        Release: {release_version}
        Generate regression test checklist for staging.
        Include integration points and data migration.
        """
    }], strategy=StrategyType.CHAIN_OF_VERIFICATION).content
```

### Production Verification
```python
def prod_verification_tests(deployment):
    return query_llm([{
        "role": "user",
        "content": f"""
        Deployment: {deployment}
        Generate production verification tests.
        Non-destructive, read-only tests only.
        """
    }], strategy=StrategyType.CONSTITUTIONAL_AI,
    principles=["No data modification", "No load generation"]).content
```

## Troubleshooting Common Issues

### Issue 1: Response Too Long
```python
# Solution: Limit tokens
response = query_llm(messages, max_tokens=500)
```

### Issue 2: Response Too Generic
```python
# Solution: Be more specific
messages = [{
    "role": "user",
    "content": """
    Generate 5 test cases for login form.
    Include: email field, password field, remember me checkbox.
    Test both valid and invalid scenarios.
    Format: Given-When-Then
    """
}]
```

### Issue 3: Need Consistent Format
```python
# Solution: Lower temperature + format instruction
response = query_llm(
    messages, 
    temperature=0.2,  # More deterministic
)
```

### Issue 4: API Key Not Working
```python
# Check your .env file
# GOOGLE_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Test with default provider
response = query_llm([{"role": "user", "content": "test"}])
```

## Performance Tips

### Tip 1: Cache Common Responses
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_test_template(test_type):
    return query_llm([{
        "role": "user",
        "content": f"Template for {test_type} testing"
    }]).content
```

### Tip 2: Use Streaming for Long Responses
```python
from llm import stream_llm

for chunk in stream_llm(messages):
    print(chunk.content, end="", flush=True)
    if chunk.is_final:
        break
```

### Tip 3: Batch Similar Requests
```python
# Instead of 10 separate calls
# Make 1 call with all 10 items
all_features = "\n".join(features)
response = query_llm([{
    "role": "user",
    "content": f"Generate tests for each:\n{all_features}"
}])
```

## Cheat Sheet

### Strategy Selection
- **Default**: Chain of Thought
- **Edge Cases**: Tree of Thoughts
- **Test Data**: Self-Consistency
- **Security**: Constitutional AI
- **Bug Analysis**: ReAct
- **API Tests**: Decomposed

### Temperature Settings
- **0.1-0.3**: Deterministic (test steps, code)
- **0.4-0.6**: Balanced (general testing)
- **0.7-0.9**: Creative (edge cases, test data)

### Token Guidelines
- **Quick answer**: 200-500
- **Detailed tests**: 1000-1500
- **Comprehensive suite**: 2000-4000

## Ready-to-Run Test Generators

Save these as `.py` files and run directly:

### test_generator.py
```python
#!/usr/bin/env python3
import sys
from llm import query_llm, StrategyType

if len(sys.argv) < 2:
    print("Usage: python test_generator.py 'feature description'")
    sys.exit(1)

feature = sys.argv[1]
response = query_llm([{
    "role": "user",
    "content": f"Generate comprehensive test cases for: {feature}"
}], strategy=StrategyType.CHAIN_OF_THOUGHT)

print(response.content)
```

### edge_finder.py
```python
#!/usr/bin/env python3
import sys
from llm import query_llm, StrategyType

if len(sys.argv) < 2:
    print("Usage: python edge_finder.py 'feature description'")
    sys.exit(1)

feature = sys.argv[1]
response = query_llm([{
    "role": "user",
    "content": f"Find all edge cases for: {feature}"
}], strategy=StrategyType.TREE_OF_THOUGHTS)

print(response.content)
```

Run them:
```bash
python test_generator.py "shopping cart checkout"
python edge_finder.py "date picker for birth date"
```

---

## Remember:
- Start simple, add complexity as needed
- Most tasks work great with default settings
- Temperature 0.3 for consistency, 0.7 for creativity
- Chain of Thought is your Swiss Army knife

*Happy Testing! 🚀*