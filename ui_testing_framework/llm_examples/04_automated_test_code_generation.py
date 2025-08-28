#!/usr/bin/env python3
"""
Automated Test Code Generation Examples
======================================

This example demonstrates generating executable test code for different frameworks:
- Playwright (Python)
- Selenium WebDriver (Python)
- Cypress (JavaScript)
- REST API tests (Python with requests)
- Load testing scripts (Python with locust)

Run directly: python 04_automated_test_code_generation.py
"""

import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm, StrategyType
import json
from datetime import datetime


def generate_playwright_tests():
    """Generate complete Playwright test code."""
    print("🎭 PLAYWRIGHT TEST CODE GENERATION")
    print("=" * 40)
    
    messages = [{
        "role": "system",
        "content": """You are an expert test automation engineer. Generate complete, 
        executable Playwright test code in Python that follows best practices."""
    }, {
        "role": "user", 
        "content": """
        Generate a complete Playwright test suite for an e-commerce login flow:
        
        Test scenarios:
        1. Successful login with valid credentials
        2. Failed login with invalid email
        3. Failed login with invalid password
        4. Failed login with empty fields
        5. Password visibility toggle
        6. Remember me functionality
        7. Forgot password link navigation
        
        Requirements:
        - Use Page Object Model pattern
        - Include proper assertions
        - Add test data management
        - Include setup and teardown
        - Add comments for maintainability
        - Handle loading states and timeouts
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.SELF_REFINE)
    print(response.content)
    
    # Save the generated code to file
    code_file = Path(__file__).parent / "generated_code" / "playwright_login_tests.py"
    code_file.parent.mkdir(exist_ok=True)
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write("# Generated Playwright Test Code\n")
        f.write("# Generated at: " + datetime.now().isoformat() + "\n\n")
        f.write(response.content)
    
    print(f"💾 Generated code saved to: {code_file}")
    print("\n" + "=" * 40 + "\n")
    
    return response.content


def generate_selenium_tests():
    """Generate complete Selenium WebDriver test code."""
    print("🌐 SELENIUM WEBDRIVER TEST CODE GENERATION")
    print("=" * 45)
    
    messages = [{
        "role": "system",
        "content": """You are an expert Selenium test automation engineer. Generate complete, 
        executable Selenium WebDriver test code in Python using pytest and modern best practices."""
    }, {
        "role": "user",
        "content": """
        Generate a complete Selenium test suite for product search functionality:
        
        Test scenarios:
        1. Search with valid product name - verify results
        2. Search with partial product name - verify suggestions
        3. Search with no results - verify "no results" message
        4. Search filters (category, price range, brand)
        5. Search result sorting (price, rating, newest)
        6. Search result pagination
        7. Search autocomplete functionality
        
        Requirements:
        - Use pytest framework
        - WebDriverWait for dynamic content
        - Page Object Model with clear separation
        - Parameterized tests for test data
        - Screenshots on failure
        - Cross-browser compatibility setup
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.DECOMPOSED)
    print(response.content)
    
    # Save the generated code to file
    code_file = Path(__file__).parent / "generated_code" / "selenium_search_tests.py"
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write("# Generated Selenium Test Code\n")
        f.write("# Generated at: " + datetime.now().isoformat() + "\n\n")
        f.write(response.content)
    
    print(f"💾 Generated code saved to: {code_file}")
    print("\n" + "=" * 45 + "\n")
    
    return response.content


def generate_api_tests():
    """Generate REST API test code."""
    print("🔌 REST API TEST CODE GENERATION")
    print("=" * 35)
    
    messages = [{
        "role": "system",
        "content": """You are an expert API test automation engineer. Generate complete, 
        executable REST API test code in Python using requests and pytest."""
    }, {
        "role": "user",
        "content": """
        Generate a complete API test suite for a user management system:
        
        API Endpoints:
        POST /api/v1/users - Create user (email, password, name)
        GET /api/v1/users/{id} - Get user details
        PUT /api/v1/users/{id} - Update user (email, name)  
        DELETE /api/v1/users/{id} - Delete user
        POST /api/v1/auth/login - Authenticate user
        GET /api/v1/users/{id}/profile - Get user profile
        
        Test scenarios:
        1. User CRUD operations (Create, Read, Update, Delete)
        2. Authentication and authorization
        3. Input validation and error handling
        4. Rate limiting and throttling
        5. Data format validation (JSON schema)
        6. Edge cases and boundary conditions
        7. Concurrent operations
        
        Requirements:
        - Use requests library with proper session management
        - JSON schema validation
        - Environment configuration (dev/staging/prod)
        - Test data fixtures and cleanup
        - Retry logic for flaky network conditions
        - Performance timing assertions
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT)
    print(response.content)
    
    # Save the generated code to file
    code_file = Path(__file__).parent / "generated_code" / "api_user_management_tests.py"
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write("# Generated API Test Code\n")
        f.write("# Generated at: " + datetime.now().isoformat() + "\n\n")
        f.write(response.content)
    
    print(f"💾 Generated code saved to: {code_file}")
    print("\n" + "=" * 35 + "\n")
    
    return response.content


def generate_cypress_tests():
    """Generate Cypress test code in JavaScript."""
    print("🌲 CYPRESS TEST CODE GENERATION (JavaScript)")
    print("=" * 50)
    
    messages = [{
        "role": "system", 
        "content": """You are an expert Cypress test automation engineer. Generate complete, 
        executable Cypress test code in JavaScript following Cypress best practices."""
    }, {
        "role": "user",
        "content": """
        Generate a complete Cypress test suite for shopping cart functionality:
        
        Test scenarios:
        1. Add single item to cart
        2. Add multiple items to cart
        3. Remove item from cart
        4. Update item quantity in cart
        5. Clear entire cart
        6. Apply discount code
        7. Calculate total with tax and shipping
        8. Proceed to checkout
        
        Requirements:
        - Use Cypress commands and best practices
        - Custom commands for common actions
        - Test data fixtures in JSON format  
        - Page Object Model approach
        - Proper assertions and waits
        - Screenshots and video on failure
        - Environment configuration
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.SELF_REFINE)
    print(response.content)
    
    # Save the generated code to file
    code_file = Path(__file__).parent / "generated_code" / "cypress_shopping_cart.spec.js"
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write("// Generated Cypress Test Code\n")
        f.write("// Generated at: " + datetime.now().isoformat() + "\n\n")
        f.write(response.content)
    
    print(f"💾 Generated code saved to: {code_file}")
    print("\n" + "=" * 50 + "\n")
    
    return response.content


def generate_performance_tests():
    """Generate load testing code with Locust."""
    print("⚡ PERFORMANCE/LOAD TEST CODE GENERATION")
    print("=" * 45)
    
    messages = [{
        "role": "system",
        "content": """You are an expert performance testing engineer. Generate complete, 
        executable load testing code using Python and Locust framework."""
    }, {
        "role": "user",
        "content": """
        Generate a complete load testing suite for an e-commerce API:
        
        Load test scenarios:
        1. User registration load test
        2. User login performance test
        3. Product search under load
        4. Shopping cart operations stress test
        5. Checkout process performance
        6. Concurrent user simulation
        7. Database connection stress test
        
        Requirements:
        - Use Locust framework
        - Realistic user behavior simulation
        - Different load patterns (ramp-up, spike, steady)
        - Performance metrics collection
        - Custom performance assertions
        - Test data generation for realistic load
        - Error rate monitoring
        - Response time percentile tracking
        
        Load targets:
        - 100 concurrent users for normal load
        - 500 users for stress testing
        - 1000 users for spike testing
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.TREE_OF_THOUGHTS)
    print(response.content)
    
    # Save the generated code to file
    code_file = Path(__file__).parent / "generated_code" / "locust_performance_tests.py"
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write("# Generated Performance Test Code\n")
        f.write("# Generated at: " + datetime.now().isoformat() + "\n\n")
        f.write(response.content)
    
    print(f"💾 Generated code saved to: {code_file}")
    print("\n" + "=" * 45 + "\n")
    
    return response.content


def generate_mobile_app_tests():
    """Generate mobile app test code with Appium."""
    print("📱 MOBILE APP TEST CODE GENERATION")
    print("=" * 37)
    
    messages = [{
        "role": "system",
        "content": """You are an expert mobile test automation engineer. Generate complete, 
        executable mobile app test code using Python and Appium framework."""
    }, {
        "role": "user",
        "content": """
        Generate a complete mobile test suite for a banking app:
        
        Test scenarios:
        1. App launch and splash screen
        2. User login with biometric authentication
        3. Account balance verification
        4. Money transfer between accounts
        5. Bill payment functionality
        6. Transaction history review
        7. Push notification handling
        8. App background/foreground behavior
        9. Network connectivity changes
        10. Device orientation changes
        
        Requirements:
        - Use Appium with Python
        - Support both iOS and Android
        - Page Object Model for mobile screens
        - Wait strategies for mobile elements
        - Screenshot capture on failure
        - Device capability management
        - Test data management for banking scenarios
        - Gestures and touch interactions
        - Handle native and hybrid app elements
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.GENERATED_KNOWLEDGE)
    print(response.content)
    
    # Save the generated code to file
    code_file = Path(__file__).parent / "generated_code" / "appium_banking_tests.py"
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write("# Generated Mobile App Test Code\n")
        f.write("# Generated at: " + datetime.now().isoformat() + "\n\n")
        f.write(response.content)
    
    print(f"💾 Generated code saved to: {code_file}")
    print("\n" + "=" * 37 + "\n")
    
    return response.content


def generate_test_utilities():
    """Generate utility functions and helper classes."""
    print("🔧 TEST UTILITY CODE GENERATION")
    print("=" * 35)
    
    messages = [{
        "role": "system",
        "content": """You are an expert test automation architect. Generate reusable utility 
        code that can be used across different test frameworks and projects."""
    }, {
        "role": "user",
        "content": """
        Generate a comprehensive test utilities module with:
        
        Utility classes and functions:
        1. Test data generator (fake data creation)
        2. Database helper (setup, cleanup, verification)
        3. API client wrapper (requests with retry logic)
        4. Screenshot and video capture utilities
        5. Email testing utilities (temp email, verification)
        6. File upload/download testing helpers
        7. Browser management utilities
        8. Test report generation helpers
        9. Environment configuration manager
        10. Test execution timer and profiler
        
        Requirements:
        - Clean, reusable code with proper documentation
        - Error handling and logging
        - Configuration through environment variables
        - Type hints and proper Python conventions
        - Unit tests for utility functions
        - Support for multiple environments (dev/staging/prod)
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.SELF_REFINE)
    print(response.content)
    
    # Save the generated code to file
    code_file = Path(__file__).parent / "generated_code" / "test_utilities.py"
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write("# Generated Test Utilities Code\n")
        f.write("# Generated at: " + datetime.now().isoformat() + "\n\n")
        f.write(response.content)
    
    print(f"💾 Generated code saved to: {code_file}")
    print("\n" + "=" * 35 + "\n")
    
    return response.content


def save_generation_results(results, filename):
    """Save code generation results to file."""
    output_file = Path(__file__).parent / filename
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_test_suites": len(results),
        "frameworks_covered": list(results.keys()),
        "generated_files": [
            "generated_code/playwright_login_tests.py",
            "generated_code/selenium_search_tests.py", 
            "generated_code/api_user_management_tests.py",
            "generated_code/cypress_shopping_cart.spec.js",
            "generated_code/locust_performance_tests.py",
            "generated_code/appium_banking_tests.py",
            "generated_code/test_utilities.py"
        ],
        "results": results,
        "usage": "Complete executable test code for multiple frameworks"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Generation results saved to: {output_file}")


def main():
    """Generate all automated test code examples."""
    print("🤖 AUTOMATED TEST CODE GENERATION EXAMPLES")
    print("=========================================")
    print("Generating executable test code for multiple frameworks...")
    print()
    
    results = {}
    
    try:
        # Generate test code for different frameworks
        results["playwright"] = generate_playwright_tests()
        results["selenium"] = generate_selenium_tests()
        results["api_tests"] = generate_api_tests()
        results["cypress"] = generate_cypress_tests()
        results["performance"] = generate_performance_tests()
        results["mobile_app"] = generate_mobile_app_tests()
        results["utilities"] = generate_test_utilities()
        
        # Save results
        save_generation_results(results, "automated_test_generation_results.json")
        
        print("✅ SUCCESS: All test code generated successfully!")
        print(f"🎯 Generated code for {len(results)} frameworks/areas")
        print("📁 Check generated_code/ folder for all executable test files")
        print()
        print("Generated Test Suites:")
        print("  🎭 Playwright - E-commerce login flow")
        print("  🌐 Selenium - Product search functionality")  
        print("  🔌 API Tests - User management system")
        print("  🌲 Cypress - Shopping cart functionality")
        print("  ⚡ Performance - Load testing with Locust")
        print("  📱 Mobile - Banking app with Appium")
        print("  🔧 Utilities - Reusable test helper functions")
        print()
        print("💡 All generated code is production-ready and follows best practices!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()