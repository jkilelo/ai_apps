"""
Test script to identify the exact abstract methods needed for Pydantic AI Model class
"""

try:
    from pydantic_ai.models import Model
    import inspect

    print("Checking abstract methods in pydantic_ai.models.Model:")
    print("=" * 60)

    # Get all abstract methods
    abstract_methods = getattr(Model, "__abstractmethods__", set())

    if abstract_methods:
        print("Required abstract methods:")
        for method in abstract_methods:
            print(f"  - {method}")

        print(f"\nTotal abstract methods: {len(abstract_methods)}")
    else:
        print("No abstract methods found (or Model is not abstract)")

    # Check the Model class signature
    print(f"\nModel class: {Model}")
    print(f"Model MRO: {Model.__mro__}")

    # Get all methods
    all_methods = [method for method in dir(Model) if not method.startswith("_")]
    print(f"\nAll public methods: {all_methods}")

    # Check which methods are abstract
    for method_name in all_methods:
        method = getattr(Model, method_name)
        if hasattr(method, "__isabstractmethod__") and method.__isabstractmethod__:
            print(f"Abstract method found: {method_name}")
            # Get method signature
            try:
                sig = inspect.signature(method)
                print(f"  Signature: {method_name}{sig}")
            except (ValueError, TypeError):
                print(f"  Could not get signature for {method_name}")

except ImportError as e:
    print(f"Pydantic AI not installed: {e}")
    print("Install with: pip install pydantic-ai[google]")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
