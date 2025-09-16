"""
UI Testing Framework v2 - Improved Architecture
Simple, intelligent, and efficient web element extraction

Usage:
    from ui_testing_framework_v2 import extract, query, stats
    
    # Simple extraction
    elements = extract("https://example.com")
    
    # Query historical data
    buttons = query(element_type="button")
    
    # Get statistics
    info = stats()
"""

# Import main API functions for convenience
from .api.simple_api import (
    extract,
    extract_batch,
    query,
    stats,
    profiles,
    compare,
    cleanup,
    export,
    # Aliases
    get,
    find,
    info
)

# Import core models if needed
from .core.models import (
    Element,
    ElementType,
    ExtractionResult,
    PageCharacteristics,
    DiffResult
)

# Version
__version__ = "2.0.0"

# What to expose
__all__ = [
    # Main API
    "extract",
    "extract_batch",
    "query",
    "stats",
    "profiles",
    "compare",
    "cleanup",
    "export",
    # Aliases
    "get",
    "find", 
    "info",
    # Models
    "Element",
    "ElementType",
    "ExtractionResult",
    "PageCharacteristics",
    "DiffResult"
]