#!/usr/bin/env python3
"""
Debug localStorage issue
"""

import sys
from pydantic import BaseModel, Field

sys.path.insert(0, '/var/www/ai_apps/playground')
import html_v3


class SimpleRequest(BaseModel):
    name: str


class SimpleResponse(BaseModel):
    status: str


# Create engine
step = html_v3.FormStep(
    id="test",
    title="Test",
    description="Test",
    request_model=SimpleRequest,
    response_model=SimpleResponse,
    is_entry_point=True,
    is_exit_point=True
)

engine = html_v3.FormChainEngine(
    chain_id="test_chain",
    title="Test",
    description="Test",
    steps=[step]
)

print(f"State storage key: {engine.state_storage_key}")

# Generate HTML
html = engine.generate_form_html("test")

# Search for localStorage usage
import re
storage_pattern = r'localStorage\.[gs]etItem\([^)]+\)'
matches = re.findall(storage_pattern, html)

print(f"\nFound {len(matches)} localStorage calls:")
for match in matches:
    print(f"  {match}")

# Check if the key is used
if engine.state_storage_key in html:
    print(f"\nState storage key '{engine.state_storage_key}' found in HTML")
else:
    print(f"\nState storage key '{engine.state_storage_key}' NOT found in HTML")

# Look for the actual key format
key_pattern = r"localStorage\.[gs]etItem\('([^']+)'"
key_matches = re.findall(key_pattern, html)
if key_matches:
    print(f"\nActual localStorage keys used:")
    for key in set(key_matches):
        print(f"  '{key}'")