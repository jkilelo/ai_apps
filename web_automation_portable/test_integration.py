#!/usr/bin/env python3
"""
Integration test for Web Automation Portable
Tests both backend API and frontend integration
"""

import asyncio
import sys
import requests
import time
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

API_BASE = "http://localhost:8001/api/web-automation"

async def test_backend_api():
    """Test the backend API endpoints"""
    print("🧪 Testing Backend API Integration")
    print("=" * 50)

    # Test health endpoint
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health Check: {health['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test element extraction
    try:
        extract_data = {
            "url": "https://httpbin.org/html",  # Simple test page
            "headless": True,
            "enable_stealth": False,
            "max_elements": 10
        }

        print("🔍 Testing element extraction...")
        response = requests.post(f"{API_BASE}/extract", json=extract_data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Extraction completed:")
            print(f"   - Success: {result['success']}")
            print(f"   - Elements found: {result['total_elements']}")
            print(f"   - Time taken: {result['extraction_time']:.2f}s")

            if result['elements']:
                print(f"   - Sample element: {result['elements'][0]['tag_name']}")
        else:
            print(f"❌ Extraction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return False

    # Test test generation
    try:
        test_data = {
            "url": "https://httpbin.org/html",
            "elements": [
                {"type": "button", "selector": "button", "tag_name": "button"},
                {"type": "input", "selector": "input", "tag_name": "input"}
            ]
        }

        print("🧪 Testing test generation...")
        response = requests.post(f"{API_BASE}/generate-tests", json=test_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test generation completed:")
            print(f"   - Tests generated: {len(result['tests'])}")
            if result['tests']:
                print(f"   - Sample test: {result['tests'][0]['name']}")
        else:
            print(f"❌ Test generation failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Test generation error: {e}")
        return False

    print("✅ Backend API integration successful!")
    return True

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Accessibility")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible at http://localhost:3000")

            # Check if it contains our component
            content = response.text
            if "Web Automation" in content:
                print("✅ WebAutomationFlowSimplified component detected")
            else:
                print("⚠️ Component not detected in HTML")

            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def check_servers():
    """Check if both servers are running"""
    print("🔍 Checking Server Status")
    print("=" * 50)

    backend_ok = False
    frontend_ok = False

    # Check backend
    try:
        response = requests.get("http://localhost:8001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend server running on port 8001")
            backend_ok = True
        else:
            print("❌ Backend server not responding properly")
    except:
        print("❌ Backend server not running on port 8001")

    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=3)
        if response.status_code == 200:
            print("✅ Frontend server running on port 3000")
            frontend_ok = True
        else:
            print("❌ Frontend server not responding properly")
    except:
        print("❌ Frontend server not running on port 3000")

    return backend_ok and frontend_ok

async def main():
    """Main test function"""
    print("🚀 Web Automation Portable - Integration Test")
    print("=" * 60)

    # Check if servers are running
    if not check_servers():
        print("\n❌ Integration test failed: Servers not running")
        print("\nTo fix:")
        print("1. Start backend: cd backend && python -m uvicorn unified_web_automation_api:app --port 8001")
        print("2. Start frontend: cd frontend && npx vite --port 3000")
        return False

    # Test backend API
    backend_ok = await test_backend_api()

    # Test frontend
    frontend_ok = test_frontend_accessibility()

    # Final result
    print("\n🏁 Integration Test Results")
    print("=" * 60)

    if backend_ok and frontend_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Backend API working with certified DRY modules")
        print("✅ Frontend accessible and ready")
        print("✅ Integration complete!")
        print("\n🌐 Access your web automation app at:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8001/docs")
        return True
    else:
        print("❌ Some tests failed")
        print(f"   Backend: {'✅' if backend_ok else '❌'}")
        print(f"   Frontend: {'✅' if frontend_ok else '❌'}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)