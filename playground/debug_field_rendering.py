#!/usr/bin/env python3
"""
Debug field rendering issue
"""

import sys
from pydantic import BaseModel, Field
from enum import Enum

sys.path.insert(0, '/var/www/ai_apps/playground')
import html_v3


class ContactRequest(BaseModel):
    message: str = Field(..., description="Your message")


class ContactResponse(BaseModel):
    status: str


# Create engine
step = html_v3.FormStep(
    id="test",
    title="Test",
    description="Test",
    request_model=ContactRequest,
    response_model=ContactResponse,
    is_entry_point=True,
    is_exit_point=True
)

engine = html_v3.FormChainEngine(
    chain_id="test",
    title="Test",
    description="Test",
    steps=[step]
)

# Get field specs
fields = engine.model_to_field_specs(ContactRequest)
print("Field specs:")
for field in fields:
    print(f"  {field.name}: type={field.field_type}, label={field.label}")

# Generate HTML
html = engine.generate_form_html("test")

# Find the message field
import re
msg_pattern = r'<[^>]*name="message"[^>]*>'
matches = re.findall(msg_pattern, html)
print(f"\nFound {len(matches)} matches for message field:")
for match in matches:
    print(f"  {match}")

# Check if textarea exists at all
if '<textarea' in html:
    print("\nTextarea elements found in HTML")
    textarea_pattern = r'<textarea[^>]*>.*?</textarea>'
    textareas = re.findall(textarea_pattern, html, re.DOTALL)
    print(f"Found {len(textareas)} textarea elements")
else:
    print("\nNo textarea elements found in HTML")

# Check what type the message field got
print(f"\nMessage field type: {fields[0].field_type}")
print(f"Expected: {html_v3.FieldType.TEXTAREA}")