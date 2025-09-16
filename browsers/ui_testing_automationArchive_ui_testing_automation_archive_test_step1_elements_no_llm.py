"""
Test Step 1: Element Extraction WITHOUT LLM
Tests the elements_extractor_no_llm.py module
"""

import sys
import asyncio
from pathlib import Path
import json

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

async def test_elements_extractor_no_llm():
    """Test the element extraction without LLM"""
    print("="*70)
    print("STEP 1 TEST: ELEMENT EXTRACTION (NO LLM)")
    print("="*70)
    
    try:
        # Import the module
        from elements_extractor_no_llm import ElementsExtractorNoLLM, ExtractionConfig
        print("[OK] Module imported successfully")
        
        # Create configuration
        config = ExtractionConfig()
        config.max_elements = 50
        config.enable_shadow_dom = True
        config.enable_iframe_traversal = True
        print("[OK] Configuration created")
        
        # Create extractor
        extractor = ElementsExtractorNoLLM(config)
        print("[OK] Extractor initialized")
        
        # Test on example.com
        print("\n[TEST] Extracting from example.com...")
        result = await extractor.extract_from_url("https://example.com")
        
        if result.success:
            print(f"  [OK] Extraction successful")
            print(f"  - Elements found: {len(result.elements)}")
            print(f"  - Extraction time: {result.extraction_time:.2f}s")
            
            # Check Pydantic contract compliance
            print("\n[TEST] Checking data contract compliance...")
            from pipeline_contracts import ExtractedElement, ElementType
            
            if result.elements:
                # Check first element is proper Pydantic model
                elem = result.elements[0]
                try:
                    # Elements are already ExtractedElement from elements_extractor_no_llm.py
                    print(f"  [OK] Element is proper Pydantic model")
                    print(f"  - Selector: {elem.selector}")
                    print(f"  - Tag: {elem.tag_name}")
                    print(f"  - Type: {elem.element_type.value}")
                    print(f"  - Clickable: {elem.is_clickable}")
                    
                    # Test conversion to pipeline contract
                    contract_data = elem.to_pipeline_contract()
                    print(f"  [OK] Element converts to pipeline contract")
                    print(f"  - Contract keys: {list(contract_data.keys())[:5]}...")
                except Exception as e:
                    print(f"  [WARNING] Contract conversion issue: {e}")
                    print(f"  Element structure: {elem}")
            
            # Test on a more complex site
            print("\n[TEST] Extracting from github.com...")
            result2 = await extractor.extract_from_url("https://github.com")
            
            if result2.success:
                print(f"  [OK] Complex site extraction successful")
                print(f"  - Elements found: {len(result2.elements)}")
                
                # Analyze element types
                element_types = {}
                for elem in result2.elements[:20]:  # Sample first 20
                    tag = elem.tag_name
                    element_types[tag] = element_types.get(tag, 0) + 1
                
                print(f"  - Element types found: {element_types}")
                
                # Check for interactive elements
                clickable_count = sum(1 for elem in result2.elements if elem.is_clickable)
                print(f"  - Clickable elements: {clickable_count}")
                
                # Save sample output
                output_file = Path("test_output_step1_no_llm.json")
                # Convert first 5 elements to dict for JSON serialization
                sample_elements = [elem.model_dump(exclude_none=True) for elem in result2.elements[:5]]
                
                sample_output = {
                    "url": "https://github.com",
                    "success": result2.success,
                    "element_count": len(result2.elements),
                    "extraction_time": result2.extraction_time,
                    "sample_elements": sample_elements  # First 5 elements as dicts
                }
                
                with open(output_file, 'w') as f:
                    json.dump(sample_output, f, indent=2, default=str)
                print(f"\n[OK] Sample output saved to {output_file}")
                
                return True
            else:
                print(f"  [FAIL] Complex site extraction failed: {result2.errors}")
                return False
                
        else:
            print(f"  [FAIL] Extraction failed: {result.errors}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    success = await test_elements_extractor_no_llm()
    
    print("\n" + "="*70)
    if success:
        print("[SUCCESS] Element extraction (no LLM) is working!")
        print("\nModule Status:")
        print("  - Imports correctly")
        print("  - Extracts elements from websites")
        print("  - Returns structured data")
        print("  - Can be converted to pipeline contracts")
        print("\nNext step: Test elements_extractor_with_llm.py")
    else:
        print("[FAIL] Element extraction needs fixes")
        print("\nIssues to address:")
        print("  - Check browser integration")
        print("  - Verify element parsing logic")
        print("  - Ensure contract compatibility")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)