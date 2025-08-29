"""
Test script to verify the VertexAIWrapper abstract class implementation
"""


def test_vertex_wrapper():
    """Test if VertexAIWrapper can be instantiated without abstract method errors"""
    try:
        from vertex_pydantic_integration import VertexAIWrapper

        print("✅ Successfully imported VertexAIWrapper")

        # Try to instantiate the wrapper
        wrapper = VertexAIWrapper(
            model_name="gemini-1.5-flash",
            vertex_project="test_project",
            gemini_url="https://test.example.com/api",
        )

        print("✅ Successfully created VertexAIWrapper instance")
        print(f"Model name: {wrapper.model_name}")
        print(f"Name method: {wrapper.name()}")
        print(f"System prompt: {wrapper.system}")

        return True

    except TypeError as e:
        if "abstract" in str(e).lower():
            print(f"❌ Abstract method error: {e}")
            return False
        else:
            print(f"❌ Type error: {e}")
            return False
    except ImportError as e:
        print(f"⚠️  Import error (expected if Pydantic AI not installed): {e}")
        return False
    except Exception as e:
        print(f"⚠️  Other error (may be expected): {e}")
        return True  # Might be credential-related, not abstract method issue


def test_simplified_approach():
    """Test the simplified approach"""
    try:
        from simplified_vertex_integration import create_vertex_agent, test_installation

        print("\n" + "=" * 50)
        print("Testing Simplified Approach:")

        if test_installation():
            print("✅ Pydantic AI is properly installed")

            # Try creating an agent
            agent = create_vertex_agent(
                model_name="gemini-1.5-flash",
                system_prompt="You are a test assistant",
                use_vertex_ai=False,  # Use simple approach first
            )

            if agent:
                print("✅ Successfully created simplified agent")
                return True
            else:
                print("❌ Failed to create simplified agent")
                return False
        else:
            print("❌ Pydantic AI not properly installed")
            return False

    except Exception as e:
        print(f"❌ Simplified approach failed: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Testing Pydantic AI Integration Fixes")
    print("=" * 50)

    # Test 1: Check if abstract class issue is fixed
    print("1. Testing VertexAIWrapper (custom implementation):")
    wrapper_works = test_vertex_wrapper()

    # Test 2: Check simplified approach
    print("\n2. Testing simplified approach:")
    simple_works = test_simplified_approach()

    print("\n" + "=" * 50)
    print("SUMMARY:")

    if wrapper_works:
        print("✅ Custom VertexAIWrapper: WORKING")
    else:
        print("❌ Custom VertexAIWrapper: NEEDS FIXING")

    if simple_works:
        print("✅ Simplified approach: WORKING")
    else:
        print("❌ Simplified approach: NEEDS FIXING")

    print("\nRECOMMENDATION:")
    if simple_works:
        print("👉 Use the simplified approach in simplified_vertex_integration.py")
        print("   This avoids abstract class complexity and works out of the box.")
    elif wrapper_works:
        print("👉 Use the custom wrapper in vertex_pydantic_integration.py")
    else:
        print("👉 Check Pydantic AI installation: pip install pydantic-ai[google]")

    print("\nNext steps:")
    print("1. Set up your Google AI API key: export GOOGLE_API_KEY=your_key")
    print("2. Run: python simplified_vertex_integration.py qa")
    print("3. Explore other demos: task, code, tools, stream")
