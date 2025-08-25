"""
Direct test of the Generate Code API endpoint
"""

import requests
import json

def test_code_generation_direct():
    """Test the code generation API directly"""
    
    print("TESTING GENERATE CODE API DIRECTLY")
    print("=" * 40)
    
    # Mock data that would come from previous steps
    mock_extraction_data = {
        "url": "https://example.com",
        "elements": [
            {
                "selector": "h1",
                "tag_name": "h1", 
                "category": "heading",
                "description": "Main heading of the page"
            },
            {
                "selector": "a[href='/more-info']",
                "tag_name": "a",
                "category": "navigation", 
                "description": "Link to more information"
            }
        ]
    }
    
    mock_test_data = {
        "features": {
            "functional": {
                "title": "Functional Tests",
                "scenarios": [
                    {
                        "title": "Verify page loads correctly",
                        "steps": ["Given I navigate to the page", "Then I should see the main heading"],
                        "tags": ["smoke"]
                    }
                ]
            },
            "validation": {
                "title": "Validation Tests", 
                "scenarios": [
                    {
                        "title": "Verify navigation links work",
                        "steps": ["Given I am on the page", "When I click the more info link", "Then I should navigate to the correct page"],
                        "tags": ["navigation"]
                    }
                ]
            }
        }
    }
    
    # Test the API endpoint
    print("1. Testing /api/generate-code endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:5175/api/generate-code",
            json={
                "extraction_data": mock_extraction_data,
                "test_data": mock_test_data,
                "code_type": "pytest",
                "language": "python"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   [SUCCESS] API call successful!")
            
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   URL: {data.get('url', 'N/A')}")
            
            generated_files = data.get('generated_files', {})
            print(f"   Generated Files: {len(generated_files)}")
            
            for filename, content in generated_files.items():
                print(f"     - {filename} ({len(content)} characters)")
                
                # Show first few lines of each file
                lines = content.split('\n')[:5]
                print(f"       Preview: {lines[0][:60]}...")
            
            # Check statistics
            stats = data.get('statistics', {})
            if stats:
                print(f"   Statistics:")
                print(f"     - Total files: {stats.get('total_files', 0)}")
                print(f"     - Test files: {stats.get('test_files', 0)}")
                print(f"     - Total lines: {stats.get('total_lines', 0)}")
                print(f"     - Features: {stats.get('features_count', 0)}")
                print(f"     - Elements: {stats.get('elements_count', 0)}")
            
            # Save response for inspection
            with open('generated_code_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print("   [SUCCESS] Generated code saved to 'generated_code_response.json'")
            
        else:
            print(f"   [FAILED] API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   [ERROR] Request failed: {e}")
    
    print("\nDirect API test completed!")

if __name__ == "__main__":
    test_code_generation_direct()