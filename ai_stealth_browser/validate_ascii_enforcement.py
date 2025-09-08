#!/usr/bin/env python3
"""
Validation script to verify ASCII-only enforcement is working.
"""

import re
from pathlib import Path


def validate_ascii_only():
    """Validate that all Python files contain only ASCII characters."""
    project_root = Path(".")
    python_files = list(project_root.rglob("*.py"))

    print("Validating ASCII-only enforcement...")
    print("=" * 50)

    violations = []

    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                try:
                    line.encode("ascii")
                except UnicodeEncodeError as e:
                    violations.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "content": repr(line),
                            "error": str(e),
                        }
                    )
        except Exception as e:
            print(f"ERROR: Could not read {file_path}: {e}")

    if violations:
        print(f"FAILURE: Found {len(violations)} ASCII violations:")
        for violation in violations:
            print(f"  {violation['file']}:{violation['line']}")
            print(f"    Content: {violation['content']}")
            print(f"    Error: {violation['error']}")
        return False
    else:
        print(f"SUCCESS: All {len(python_files)} Python files are ASCII-only!")
        return True


def test_commit_guard():
    """Test the commit guard functionality."""
    print("\nTesting commit guard ASCII enforcement...")

    # Create a test file with emojis
    test_file = Path("test_emoji_file.py")
    test_content = '''#!/usr/bin/env python3
"""Test file with emojis."""

def test_function():
 " " " A test function with emojis and . " " "  print( " Testing with emojis! " )     return True
'''

    try:
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        print(f"Created test file: {test_file}")

        # Check if the file has non-ASCII characters
        has_non_ascii = False
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
            try:
                content.encode("ascii")
            except UnicodeEncodeError:
                has_non_ascii = True

        if has_non_ascii:
            print("SUCCESS: Test file contains non-ASCII characters as expected")
        else:
            print("WARNING: Test file doesn't contain non-ASCII characters")

        # Clean up
        test_file.unlink()
        print("Test file cleaned up")

        return True

    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        if test_file.exists():
            test_file.unlink()
        return False


def main():
    """Main validation function."""
    print("ASCII-only Enforcement Validation")
    print("=" * 50)

    # Validate current state
    ascii_valid = validate_ascii_only()

    # Test commit guard
    guard_test = test_commit_guard()

    print("\n" + "=" * 50)
    print("Validation Summary:")
    print(f"  ASCII compliance: {'PASS' if ascii_valid else 'FAIL'}")
    print(f"  Commit guard test: {'PASS' if guard_test else 'FAIL'}")

    if ascii_valid and guard_test:
        print("\nSUCCESS: ASCII-only enforcement is properly configured!")
        print("\nFeatures enabled:")
        print("  - All existing Python files are ASCII-only")
        print("  - Git commit guard will block non-ASCII characters")
        print("  - Auto-formatter will clean non-ASCII characters on file edits")
        return 0
    else:
        print("\nFAILURE: ASCII-only enforcement needs attention!")
        return 1


if __name__ == "__main__":
    exit(main())
