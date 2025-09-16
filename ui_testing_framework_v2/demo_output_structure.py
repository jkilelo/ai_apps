"""
Demonstrate the complete output structure of v2 extraction
Shows real examples of what downstream systems will receive
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_testing_framework_v2 import extract, query, stats

def show_complete_output_structure():
    """Extract and show the complete output structure"""
    
    print("=" * 80)
    print("UI TESTING FRAMEWORK V2 - OUTPUT STRUCTURE DEMONSTRATION")
    print("=" * 80)
    
    # 1. EXTRACTION OUTPUT
    print("\n1. EXTRACTION OUTPUT STRUCTURE")
    print("-" * 40)
    
    # Perform extraction
    url = "https://www.google.com"
    print(f"Extracting from: {url}")
    elements = extract(url, profile="qa")
    
    print(f"\nExtracted {len(elements)} elements")
    
    # Show the structure of an Element object
    if elements:
        first_element = elements[0]
        print("\n--- SINGLE ELEMENT STRUCTURE ---")
        print(f"Type: {type(first_element)}")
        print(f"Available attributes: {[attr for attr in dir(first_element) if not attr.startswith('_')]}")
        
        # Show actual element data
        print("\n--- EXAMPLE ELEMENT DATA ---")
        for i, element in enumerate(elements[:3], 1):
            print(f"\nElement {i}:")
            print(f"  selector: {element.selector}")
            print(f"  tag_name: {element.tag_name}")
            print(f"  element_type: {element.element_type}")
            print(f"  text: {element.text[:50] if element.text else None}")
            print(f"  is_visible: {element.is_visible}")
            print(f"  is_interactive: {element.is_interactive}")
            print(f"  interaction_score: {element.interaction_score}")
            print(f"  attributes: {json.dumps(element.attributes, indent=4)}")
            if element.bounding_box:
                print(f"  bounding_box: {json.dumps(element.bounding_box, indent=4)}")
    
    # 2. QUERY OUTPUT
    print("\n\n2. QUERY OUTPUT STRUCTURE")
    print("-" * 40)
    
    # Query for buttons
    button_results = query(element_type="button", limit=3)
    print(f"\nQuery results for buttons: {len(button_results)} records")
    
    if button_results:
        print("\n--- QUERY RESULT STRUCTURE ---")
        first_result = button_results[0]
        print(f"Type: {type(first_result)}")
        print(f"Keys: {list(first_result.keys())}")
        
        print("\n--- EXAMPLE QUERY RESULT ---")
        print(json.dumps(first_result, indent=2, default=str))
    
    # 3. EXTRACTION RESULT METADATA
    print("\n\n3. FULL EXTRACTION RESULT (from storage)")
    print("-" * 40)
    
    # Query latest extraction to see full metadata
    latest_extractions = query(url=url, limit=1)
    if latest_extractions:
        print("\n--- EXTRACTION METADATA ---")
        extraction = latest_extractions[0]
        print(json.dumps({
            "id": extraction.get("id"),
            "url": extraction.get("url"),
            "profile": extraction.get("profile"),
            "timestamp": str(extraction.get("timestamp")),
            "duration": extraction.get("duration"),
            "element_count": extraction.get("element_count"),
            "content_hash": extraction.get("content_hash")
        }, indent=2))
    
    # 4. STATISTICS OUTPUT
    print("\n\n4. STATISTICS OUTPUT STRUCTURE")
    print("-" * 40)
    
    system_stats = stats()
    print("\n--- SYSTEM STATISTICS ---")
    print(json.dumps(system_stats, indent=2))
    
    # 5. EXPORT TO JSON
    print("\n\n5. JSON EXPORT FORMAT")
    print("-" * 40)
    
    # Create a complete export structure
    export_data = {
        "metadata": {
            "framework_version": "2.0.0",
            "export_timestamp": datetime.now().isoformat(),
            "url": url,
            "profile": "qa",
            "element_count": len(elements)
        },
        "elements": [
            {
                "selector": elem.selector,
                "tag_name": elem.tag_name,
                "element_type": str(elem.element_type),
                "text": elem.text,
                "is_visible": elem.is_visible,
                "is_interactive": elem.is_interactive,
                "interaction_score": elem.interaction_score,
                "attributes": elem.attributes,
                "bounding_box": elem.bounding_box
            }
            for elem in elements[:5]  # First 5 for demo
        ]
    }
    
    # Save to file for inspection
    output_file = Path("v2_output_example.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\nComplete JSON structure saved to: {output_file}")
    print("\n--- JSON EXPORT PREVIEW ---")
    print(json.dumps(export_data, indent=2, default=str)[:2000] + "...")
    
    return elements, export_data

if __name__ == "__main__":
    elements, export_data = show_complete_output_structure()
    
    print("\n" + "=" * 80)
    print("OUTPUT SUMMARY FOR DOWNSTREAM SYSTEMS")
    print("=" * 80)
    print(f"""
The v2 framework provides the following output formats:

1. ELEMENT OBJECTS (Python):
   - Direct access to Element dataclass instances
   - Contains: selector, tag_name, element_type, text, attributes, 
     is_visible, is_interactive, interaction_score, bounding_box
   
2. JSON EXPORT:
   - Fully serializable JSON structure
   - Includes metadata and element details
   - Ready for API transmission or file storage
   
3. QUERY RESULTS:
   - Dictionary format from database
   - Includes historical data and timestamps
   - Filterable by element_type, URL, profile, score
   
4. STATISTICS:
   - System-wide metrics
   - Storage and cache statistics
   - Profile usage data

Total elements available: {len(elements)}
Export file created: v2_output_example.json
""")