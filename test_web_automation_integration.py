"""
Test Web Automation Integration
"""

import requests
import json

def test_backend_api():
    """Test the backend API directly"""
    
    # Test health check
    print("Testing health check...")
    response = requests.get("http://localhost:5175/")
    print(f"Health check: {response.json()}")
    
    # Test element extraction with example.com
    print("\nTesting element extraction...")
    payload = {
        "url": "https://example.com",
        "headless": True,
        "analyze_with_llm": False  # Set to False for faster testing
    }
    
    response = requests.post(
        "http://localhost:5175/api/extract-elements",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Extracted {data.get('total_elements', 0)} elements")
        
        # Show categories
        if 'elements_by_category' in data:
            print("\nElements by category:")
            for category, items in data['elements_by_category'].items():
                print(f"  {category}: {len(items)} elements")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_backend_api()