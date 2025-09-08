#!/usr/bin/env python3
"""
ASCII-only enforcer script.
Removes all emojis and non-ASCII characters from Python files in the project.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in the project."""
    python_files = []
    root_path = Path(root_dir)

    for file_path in root_path.rglob("*.py"):
        python_files.append(file_path)

    return python_files


def check_and_clean_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Check a file for non-ASCII characters and clean them."""
    issues = []
    was_modified = False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = []
        for line_num, line in enumerate(lines, 1):
            original_line = line

            # Check for non-ASCII characters
            try:
                line.encode("ascii")
                cleaned_lines.append(line)
            except UnicodeEncodeError:
                # Remove or replace common emojis and symbols
                cleaned_line = clean_non_ascii(line)

                if cleaned_line != original_line:
                    issues.append(f"Line {line_num}: Removed non-ASCII characters")
                    was_modified = True

                cleaned_lines.append(cleaned_line)

        # Write back if modified
        if was_modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(cleaned_lines)

        return was_modified, issues

    except Exception as e:
        issues.append(f"Error processing file: {e}")
        return False, issues


def clean_non_ascii(text: str) -> str:
    """Clean non-ASCII characters from text."""
    # Common emoji replacements
    replacements = {
        # Status indicators
 " " : " " ,  " SUCCESS: " : " SUCCESS: " ,  " ERROR: " : " ERROR: " ,  " WARNING: " : " WARNING: " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,  " " : " " ,         # Unicode tree characters
 " |- " : " |- " ,  " \- " : " \\- " ,  " | " : " | " ,  " - " : " - " ,         # Other symbols
 " - " : " - " ,  " -- " : " -- " ,         '"': '"',
        '"': '"',
        """: "'",
        """: "'",
    }

    result = text
    for emoji, replacement in replacements.items():
        if replacement:
            result = result.replace(emoji, f" {replacement} ")
        else:
            result = result.replace(emoji, "")

    # Remove any remaining non-ASCII characters
    result = re.sub(r"[^\x00-\x7F]+", "", result)

    # Clean up extra spaces
    result = re.sub(r"\s+", " ", result)

    return result


def main():
    """Main function to clean all Python files."""
    project_root = "."

    print("ASCII-only enforcer starting...")
    print("=" * 50)

    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files to check")

    total_modified = 0
    total_issues = 0

    for file_path in python_files:
        print(f"\nChecking: {file_path}")

        was_modified, issues = check_and_clean_file(file_path)

        if was_modified:
            total_modified += 1
            print(f"  CLEANED: {len(issues)} issues fixed")
            for issue in issues:
                print(f"    - {issue}")
        else:
            if issues:
                print(f"  ERROR: {issues[0]}")
            else:
                print("  OK: File is ASCII-only")

        total_issues += len(issues)

    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  Files checked: {len(python_files)}")
    print(f"  Files modified: {total_modified}")
    print(f"  Total issues fixed: {total_issues}")

    if total_modified > 0:
        print("\nSUCCESS: All Python files are now ASCII-only!")
    else:
        print("\nINFO: All files were already ASCII-only")

    return 0


if __name__ == "__main__":
    exit(main())
