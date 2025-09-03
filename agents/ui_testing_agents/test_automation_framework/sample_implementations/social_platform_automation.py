#!/usr/bin/env python3
"""
Example 3: Social Media Platform Test with Live LLM
====================================================
Demonstrates AI-powered test generation for social media features
using real LLM to create user interaction tests, content validation,
and engagement metrics testing.

This example shows how V2 system uses mandatory LLM integration
to generate intelligent tests for complex social interactions.
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
    generate_gherkin_with_llm,
    generate_ai_scenarios_with_llm,
    generate_visual_tests_with_llm,
    enhance_code_with_llm
)


async def test_social_media_platform():
    """Generate comprehensive social media platform tests using AI"""
    
    print("=" * 80)
    print("SOCIAL MEDIA PLATFORM TEST GENERATION (V2 - LLM Native)")
    print("=" * 80)
    print("Using real AI to generate social interaction test suite")
    print("-" * 80)
    
    # Define social media page elements (feed, post creation, interactions)
    social_elements = {
        "form_elements": [
            {"type": "textarea", "name": "postContent", "label": "What's on your mind?", "maxlength": 280},
            {"type": "file", "name": "mediaUpload", "label": "Add Photo/Video", "accept": "image/*,video/*"},
            {"type": "text", "name": "searchQuery", "label": "Search", "placeholder": "Search posts, people..."},
            {"type": "textarea", "name": "commentText", "label": "Write a comment...", "maxlength": 500},
            {"type": "select", "name": "privacy", "label": "Privacy", "options": ["Public", "Friends", "Only Me"]},
            {"type": "text", "name": "hashtags", "label": "Add hashtags", "placeholder": "#trending"}
        ],
        "clickable_elements": [
            {"type": "button", "text": "Post", "id": "submitPost", "data-testid": "post-button"},
            {"type": "button", "text": "Like", "class": "like-btn", "data-testid": "like-button"},
            {"type": "button", "text": "Comment", "class": "comment-btn", "data-testid": "comment-button"},
            {"type": "button", "text": "Share", "class": "share-btn", "data-testid": "share-button"},
            {"type": "button", "text": "Follow", "class": "follow-btn", "data-testid": "follow-button"},
            {"type": "link", "text": "View Profile", "href": "/profile"},
            {"type": "button", "text": "Report", "class": "report-btn"},
            {"type": "button", "text": "Block User", "class": "block-btn"},
            {"type": "button", "text": "Load More", "id": "loadMore"}
        ],
        "interactive_elements": [
            {"type": "feed", "selector": ".post-feed", "purpose": "infinite-scroll"},
            {"type": "modal", "selector": ".share-modal", "purpose": "share-options"},
            {"type": "dropdown", "selector": ".notifications", "purpose": "notification-center"},
            {"type": "chat", "selector": ".messenger", "purpose": "direct-messaging"},
            {"type": "stories", "selector": ".stories-container", "purpose": "ephemeral-content"}
        ],
        "validation_elements": [
            {"selector": ".post-counter", "type": "counter", "purpose": "character-count"},
            {"selector": ".like-count", "type": "metric", "purpose": "engagement"},
            {"selector": ".comment-count", "type": "metric", "purpose": "engagement"},
            {"selector": ".share-count", "type": "metric", "purpose": "virality"},
            {"selector": ".online-status", "type": "indicator", "purpose": "presence"}
        ]
    }
    
    context = {
        "url": "https://social.example.com/feed",
        "title": "Social Feed",
        "purpose": "social media interactions and content sharing",
        "features": ["real-time updates", "infinite scroll", "push notifications", "live streaming"]
    }
    
    # 1. Generate User Interaction Test Scenarios
    print("\n[1] GENERATING USER INTERACTION SCENARIOS WITH LLM...")
    print("-" * 40)
    
    interaction_scenarios = await generate_ai_scenarios_with_llm(
        social_elements,
        context,
        max_scenarios=6
    )
    
    print("AI Generated Interaction Scenarios:")
    if isinstance(interaction_scenarios, dict) and 'scenarios' in interaction_scenarios:
        scenarios_text = interaction_scenarios['scenarios']
        # Show first 1000 chars
        print(scenarios_text[:1000] if len(scenarios_text) > 1000 else scenarios_text)
    print("-" * 40)
    
    # 2. Generate Gherkin for Social Features
    print("\n[2] GENERATING GHERKIN FOR SOCIAL FEATURES WITH LLM...")
    print("-" * 40)
    
    gherkin = await generate_gherkin_with_llm(
        social_elements,
        "social-media"
    )
    
    print("AI Generated Gherkin:")
    print(gherkin[:800] if len(gherkin) > 800 else gherkin)
    print("-" * 40)
    
    # 3. Generate Visual Regression Tests
    print("\n[3] GENERATING VISUAL REGRESSION TESTS WITH LLM...")
    print("-" * 40)
    
    visual_tests = await generate_visual_tests_with_llm(
        social_elements,
        {"screenshots": ["feed", "profile", "stories", "chat"]}
    )
    
    print("AI Generated Visual Tests:")
    if isinstance(visual_tests, dict) and 'visual_tests' in visual_tests:
        tests = visual_tests['visual_tests']
        print(tests[:600] if len(tests) > 600 else tests)
    print("-" * 40)
    
    # 4. Generate Real-Time Update Tests
    print("\n[4] GENERATING REAL-TIME UPDATE TESTS WITH LLM...")
    print("-" * 40)
    
    from llm_client import call_default_llm
    realtime_prompt = """Generate test cases for real-time social media features:
    1. Live feed updates (new posts appearing without refresh)
    2. Real-time like/comment counters
    3. Online status indicators
    4. Push notification testing
    5. Live streaming functionality
    6. Typing indicators in chat
    
    Include WebSocket testing and event-driven scenarios."""
    
    realtime_tests = await call_default_llm(
        [{"role": "user", "content": realtime_prompt}],
        temperature=0.6,
        max_tokens=1000
    )
    
    print("AI Generated Real-Time Tests:")
    print(realtime_tests[:700] if len(realtime_tests) > 700 else realtime_tests)
    print("-" * 40)
    
    # 5. Generate Content Moderation Tests
    print("\n[5] GENERATING CONTENT MODERATION TESTS WITH LLM...")
    print("-" * 40)
    
    moderation_prompt = """Generate test cases for social media content moderation:
    1. Inappropriate content detection
    2. Spam detection and prevention
    3. Hashtag abuse prevention
    4. Report functionality testing
    5. User blocking mechanisms
    6. Community guidelines enforcement
    
    Focus on both automated and manual moderation flows."""
    
    moderation_tests = await call_default_llm(
        [{"role": "user", "content": moderation_prompt}],
        temperature=0.4,
        max_tokens=800
    )
    
    print("AI Generated Moderation Tests:")
    print(moderation_tests[:600] if len(moderation_tests) > 600 else moderation_tests)
    print("-" * 40)
    
    # 6. Enhance Basic Test to Production Code
    print("\n[6] ENHANCING SOCIAL INTERACTION TEST TO PRODUCTION CODE...")
    print("-" * 40)
    
    basic_test = """
async def test_post_creation():
    # Create a post
    await page.fill('#postContent', 'Check out this amazing sunset! #beautiful')
    await page.click('#submitPost')
    
    # Verify post appears
    post = await page.locator('.post-feed .post:first-child')
    assert await post.is_visible()
"""
    
    enhanced = await enhance_code_with_llm(basic_test, "production-social")
    
    print("AI Enhanced Production Code:")
    if isinstance(enhanced, dict) and 'enhanced_code' in enhanced:
        code = enhanced['enhanced_code']
        print(code[:800] if len(code) > 800 else code)
    print("-" * 40)
    
    # Summary
    print("\n" + "=" * 80)
    print("SOCIAL MEDIA PLATFORM TEST SUITE GENERATED")
    print("=" * 80)
    print("[SUCCESS] Generated with V2 LLM-Native System:")
    print("✓ User Interaction Scenarios - Complex social flows")
    print("✓ Gherkin Test Cases - BDD format")
    print("✓ Visual Regression Tests - UI consistency")
    print("✓ Real-Time Update Tests - WebSocket & events")
    print("✓ Content Moderation Tests - Safety & compliance")
    print("✓ Production Code - Enterprise-ready")
    print("\nAll generated using REAL LLM - No fallbacks or mocks!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nStarting Social Media Platform Test Generation...")
    print("This example demonstrates V2's social interaction testing")
    print("If LLM is not available, the system will halt.\n")
    
    asyncio.run(test_social_media_platform())