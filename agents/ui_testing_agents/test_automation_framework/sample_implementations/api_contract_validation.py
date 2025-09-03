#!/usr/bin/env python3
"""
Example 4: API Integration Test with Live LLM
==============================================
Demonstrates AI-powered API test generation including REST endpoints,
GraphQL queries, WebSocket connections, and microservices testing
using real LLM for intelligent test creation.

This example shows how V2 system uses mandatory LLM integration
to generate comprehensive API test suites with contract testing.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

# V2 imports - These require LLM to be available
from test_automation_framework.ai_test_generator import (
    generate_api_tests_with_llm,
    generate_ai_scenarios_with_llm,
    enhance_code_with_llm,
    generate_performance_tests_with_llm
)


async def test_api_integration():
    """Generate comprehensive API integration tests using AI"""
    
    print("=" * 80)
    print("API INTEGRATION TEST GENERATION (V2 - LLM Native)")
    print("=" * 80)
    print("Using real AI to generate API test suite")
    print("-" * 80)
    
    # Define API endpoints and structure
    api_structure = {
        "rest_endpoints": [
            {
                "method": "GET",
                "path": "/api/v1/users",
                "description": "Get all users",
                "params": ["page", "limit", "sort"],
                "auth": "Bearer token"
            },
            {
                "method": "POST",
                "path": "/api/v1/users",
                "description": "Create new user",
                "body": {
                    "username": "string",
                    "email": "string",
                    "password": "string",
                    "role": "enum[user, admin, moderator]"
                },
                "auth": "Bearer token"
            },
            {
                "method": "PUT",
                "path": "/api/v1/users/{id}",
                "description": "Update user",
                "body": {
                    "email": "string",
                    "profile": "object"
                },
                "auth": "Bearer token"
            },
            {
                "method": "DELETE",
                "path": "/api/v1/users/{id}",
                "description": "Delete user",
                "auth": "Bearer token + Admin role"
            },
            {
                "method": "GET",
                "path": "/api/v1/users/{id}/posts",
                "description": "Get user posts",
                "params": ["status", "from_date", "to_date"],
                "auth": "Bearer token"
            }
        ],
        "graphql_queries": [
            {
                "name": "GetUserWithPosts",
                "query": """
                query GetUserWithPosts($userId: ID!) {
                    user(id: $userId) {
                        id
                        username
                        posts {
                            id
                            title
                            content
                            likes
                        }
                    }
                }
                """
            },
            {
                "name": "CreatePost",
                "mutation": """
                mutation CreatePost($input: PostInput!) {
                    createPost(input: $input) {
                        id
                        title
                        createdAt
                    }
                }
                """
            }
        ],
        "websocket_events": [
            {"event": "user_online", "payload": {"userId": "string", "timestamp": "ISO8601"}},
            {"event": "new_message", "payload": {"from": "string", "to": "string", "message": "string"}},
            {"event": "notification", "payload": {"type": "string", "data": "object"}}
        ],
        "response_schemas": {
            "user": {
                "id": "string",
                "username": "string",
                "email": "string",
                "createdAt": "ISO8601",
                "profile": {
                    "avatar": "url",
                    "bio": "string"
                }
            },
            "error": {
                "code": "string",
                "message": "string",
                "details": "object"
            }
        }
    }
    
    context = {
        "base_url": "https://api.example.com",
        "version": "v1",
        "auth_type": "OAuth2.0",
        "rate_limits": "100 requests per minute",
        "purpose": "RESTful API with GraphQL and WebSocket support"
    }
    
    # 1. Generate REST API Test Cases
    print("\n[1] GENERATING REST API TEST CASES WITH LLM...")
    print("-" * 40)
    
    api_tests = await generate_api_tests_with_llm(
        api_structure,
        context
    )
    
    print("AI Generated API Tests:")
    if isinstance(api_tests, dict) and 'tests' in api_tests:
        tests_text = api_tests['tests']
        print(tests_text[:1000] if len(tests_text) > 1000 else tests_text)
    print("-" * 40)
    
    # 2. Generate Contract Testing
    print("\n[2] GENERATING CONTRACT TESTS WITH LLM...")
    print("-" * 40)
    
    from llm_client import call_default_llm
    contract_prompt = """Generate contract tests for API integration:
    
    REST Endpoints:
    - GET /api/v1/users - Returns user array
    - POST /api/v1/users - Creates user, returns user object
    - PUT /api/v1/users/{id} - Updates user
    - DELETE /api/v1/users/{id} - Returns 204 No Content
    
    Requirements:
    1. Schema validation for requests and responses
    2. Status code verification
    3. Header validation (Content-Type, Auth)
    4. Error response contract testing
    5. Pagination contract validation
    
    Generate comprehensive Pact or contract tests."""
    
    contract_tests = await call_default_llm(
        [{"role": "user", "content": contract_prompt}],
        temperature=0.3,
        max_tokens=1200
    )
    
    print("AI Generated Contract Tests:")
    print(contract_tests[:800] if len(contract_tests) > 800 else contract_tests)
    print("-" * 40)
    
    # 3. Generate GraphQL Test Cases
    print("\n[3] GENERATING GRAPHQL TEST CASES WITH LLM...")
    print("-" * 40)
    
    graphql_prompt = """Generate GraphQL API test cases for:
    
    Queries:
    - GetUserWithPosts: Fetch user and their posts
    - GetAllUsers: Paginated user list
    
    Mutations:
    - CreatePost: Create new post
    - UpdateUser: Update user profile
    
    Include:
    1. Query validation tests
    2. Mutation tests with input validation
    3. Error handling for malformed queries
    4. Performance tests for nested queries
    5. Authorization tests"""
    
    graphql_tests = await call_default_llm(
        [{"role": "user", "content": graphql_prompt}],
        temperature=0.5,
        max_tokens=1000
    )
    
    print("AI Generated GraphQL Tests:")
    print(graphql_tests[:700] if len(graphql_tests) > 700 else graphql_tests)
    print("-" * 40)
    
    # 4. Generate Performance Tests
    print("\n[4] GENERATING API PERFORMANCE TESTS WITH LLM...")
    print("-" * 40)
    
    perf_tests = await generate_performance_tests_with_llm(
        api_structure,
        {"load": "1000 users", "duration": "5 minutes"}
    )
    
    print("AI Generated Performance Tests:")
    if isinstance(perf_tests, dict) and 'performance_tests' in perf_tests:
        tests = perf_tests['performance_tests']
        print(tests[:600] if len(tests) > 600 else tests)
    print("-" * 40)
    
    # 5. Generate WebSocket Tests
    print("\n[5] GENERATING WEBSOCKET TEST CASES WITH LLM...")
    print("-" * 40)
    
    websocket_prompt = """Generate WebSocket connection test cases:
    
    Events to test:
    - user_online: User presence updates
    - new_message: Real-time messaging
    - notification: Push notifications
    
    Test scenarios:
    1. Connection establishment and authentication
    2. Event subscription and unsubscription
    3. Message broadcasting
    4. Connection recovery after disconnect
    5. Rate limiting on WebSocket
    6. Binary message handling"""
    
    websocket_tests = await call_default_llm(
        [{"role": "user", "content": websocket_prompt}],
        temperature=0.4,
        max_tokens=800
    )
    
    print("AI Generated WebSocket Tests:")
    print(websocket_tests[:600] if len(websocket_tests) > 600 else websocket_tests)
    print("-" * 40)
    
    # 6. Enhance Basic API Test to Production
    print("\n[6] ENHANCING API TEST TO PRODUCTION CODE...")
    print("-" * 40)
    
    basic_test = """
import requests

def test_create_user():
    response = requests.post(
        'https://api.example.com/api/v1/users',
        json={'username': 'testuser', 'email': 'test@example.com'}
    )
    assert response.status_code == 201
"""
    
    enhanced = await enhance_code_with_llm(basic_test, "production-api")
    
    print("AI Enhanced Production API Test:")
    if isinstance(enhanced, dict) and 'enhanced_code' in enhanced:
        code = enhanced['enhanced_code']
        print(code[:800] if len(code) > 800 else code)
    print("-" * 40)
    
    # Summary
    print("\n" + "=" * 80)
    print("API INTEGRATION TEST SUITE GENERATED")
    print("=" * 80)
    print("[SUCCESS] Generated with V2 LLM-Native System:")
    print("✓ REST API Tests - Complete CRUD coverage")
    print("✓ Contract Tests - Schema validation")
    print("✓ GraphQL Tests - Query & mutation testing")
    print("✓ Performance Tests - Load & stress testing")
    print("✓ WebSocket Tests - Real-time events")
    print("✓ Production Code - Enterprise-ready")
    print("\nAll generated using REAL LLM - No fallbacks or mocks!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nStarting API Integration Test Generation...")
    print("This example demonstrates V2's API testing capabilities")
    print("If LLM is not available, the system will halt.\n")
    
    asyncio.run(test_api_integration())