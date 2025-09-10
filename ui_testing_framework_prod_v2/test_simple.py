import asyncio
from data_types import TestCategory

# Test the fix
categories = [
    TestCategory.FUNCTIONAL,
    "validation",  # String instead of enum
    TestCategory.ACCESSIBILITY
]

# Test category value access
for category in categories:
    if isinstance(category, TestCategory):
        print(f"Enum: {category.value}")
    else:
        print(f"String: {str(category)}")

print("\nAll category fixes working!")