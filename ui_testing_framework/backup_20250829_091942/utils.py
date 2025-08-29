#!/usr/bin/env python3
"""
Utility functions for the UI Testing Framework
"""

import re
from typing import Any, Dict
import json
from pathlib import Path


def format_url_for_filename(url: str) -> str:
    """
    Format URL for use in filename according to running_steps.txt:
    - Replace all non-alphanumeric characters with underscores
    - Keep first 30 characters
    
    Args:
        url: URL to format
        
    Returns:
        Formatted string safe for filename use
    """
    # Remove protocol if present
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    
    # Replace non-alphanumeric with underscores
    formatted = re.sub(r'[^a-zA-Z0-9]', '_', url)
    
    # Remove consecutive underscores
    formatted = re.sub(r'_+', '_', formatted)
    
    # Trim to 30 characters
    formatted = formatted[:30]
    
    # Remove trailing underscore if present
    formatted = formatted.rstrip('_')
    
    return formatted


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save data as JSON with proper formatting"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load JSON data from file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_pydantic_output(model_instance, filepath: Path) -> bool:
    """
    Validate that a Pydantic model instance can be saved and loaded correctly
    
    Args:
        model_instance: Pydantic model instance
        filepath: Path to save to
        
    Returns:
        True if validation passes
    """
    try:
        # Save using model's dump
        data = model_instance.model_dump() if hasattr(model_instance, 'model_dump') else model_instance.dict()
        save_json(data, filepath)
        
        # Try to load it back
        loaded_data = load_json(filepath)
        
        # Try to reconstruct the model
        model_class = type(model_instance)
        reconstructed = model_class(**loaded_data)
        
        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False