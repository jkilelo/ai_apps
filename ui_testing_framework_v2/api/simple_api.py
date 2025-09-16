"""
Simple, user-friendly API for the extraction framework
One-liner usage with smart defaults
"""

import asyncio
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from ..core.extractor import IntelligentExtractor
from ..core.models import Element, ExtractionResult
from ..core.profile_manager import ProfileManager
from ..storage.sqlite_storage import SQLiteStorage
from ..cache.memory_cache import MemoryCache


# Global instances for convenience
_extractor: Optional[IntelligentExtractor] = None
_storage: Optional[SQLiteStorage] = None
_cache: Optional[MemoryCache] = None
_profile_manager: Optional[ProfileManager] = None


def _ensure_initialized():
    """Ensure global instances are initialized"""
    global _extractor, _storage, _cache, _profile_manager
    
    if _profile_manager is None:
        _profile_manager = ProfileManager()
    
    if _storage is None:
        _storage = SQLiteStorage()
    
    if _cache is None:
        _cache = MemoryCache()
    
    if _extractor is None:
        _extractor = IntelligentExtractor(
            profile_manager=_profile_manager,
            storage=_storage,
            cache=_cache
        )


def extract(url: str, 
           profile: Optional[str] = None,
           cache: bool = True,
           auto_profile: bool = True,
           interactive_only: bool = False) -> List[Element]:
    """
    Simple extraction function - the main API
    
    Args:
        url: URL to extract from
        profile: Profile name (auto-detected if not provided)
        cache: Use caching for performance
        auto_profile: Auto-select best profile
        interactive_only: Return only interactive elements
    
    Returns:
        List of extracted elements
    
    Examples:
        # Simple usage
        elements = extract("https://example.com")
        
        # With specific profile
        elements = extract("https://example.com", profile="qa")
        
        # Interactive elements only
        buttons = extract("https://example.com", interactive_only=True)
    """
    _ensure_initialized()
    
    # Run async extraction
    result = asyncio.run(_async_extract(
        url=url,
        profile=profile,
        use_cache=cache,
        auto_profile=auto_profile
    ))
    
    elements = result.elements
    
    # Filter interactive only if requested
    if interactive_only:
        elements = [e for e in elements if e.is_interactive]
    
    return elements


async def _async_extract(url: str, 
                        profile: Optional[str],
                        use_cache: bool,
                        auto_profile: bool) -> ExtractionResult:
    """Async extraction helper"""
    async with _extractor:
        return await _extractor.extract(
            url=url,
            profile=profile,
            use_cache=use_cache,
            auto_profile=auto_profile
        )


def extract_batch(urls: List[str], 
                 profile: Optional[str] = None,
                 parallel: bool = True,
                 max_workers: int = 5) -> Dict[str, List[Element]]:
    """
    Extract from multiple URLs
    
    Args:
        urls: List of URLs to extract from
        profile: Profile to use for all URLs
        parallel: Process URLs in parallel
        max_workers: Max parallel workers
    
    Returns:
        Dictionary mapping URL to elements
    
    Example:
        results = extract_batch([
            "https://example.com",
            "https://google.com"
        ])
    """
    _ensure_initialized()
    
    if parallel:
        return asyncio.run(_async_extract_batch(urls, profile, max_workers))
    else:
        results = {}
        for url in urls:
            results[url] = extract(url, profile=profile)
        return results


async def _async_extract_batch(urls: List[str], 
                              profile: Optional[str],
                              max_workers: int) -> Dict[str, List[Element]]:
    """Async batch extraction"""
    semaphore = asyncio.Semaphore(max_workers)
    
    async def extract_with_limit(url: str):
        async with semaphore:
            result = await _async_extract(url, profile, use_cache=True, auto_profile=True)
            return url, result.elements
    
    tasks = [extract_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    return dict(results)


def query(url: Optional[str] = None,
         profile: Optional[str] = None,
         element_type: Optional[str] = None,
         min_score: Optional[float] = None,
         limit: int = 100) -> List[Dict[str, Any]]:
    """
    Query historical extraction data
    
    Args:
        url: Filter by URL
        profile: Filter by profile
        element_type: Filter by element type
        min_score: Minimum interaction score
        limit: Max results to return
    
    Returns:
        List of matching elements with metadata
    
    Example:
        # Get all buttons from Google
        buttons = query(url="https://google.com", element_type="button")
        
        # Get highly interactive elements
        interactive = query(min_score=0.8)
    """
    _ensure_initialized()
    
    if element_type or min_score is not None:
        return _storage.query_elements(
            element_type=element_type,
            min_interaction_score=min_score,
            limit=limit
        )
    else:
        return _storage.query_extractions(
            url=url,
            profile=profile,
            limit=limit
        )


def stats() -> Dict[str, Any]:
    """
    Get system statistics
    
    Returns:
        Dictionary with storage and cache stats
    
    Example:
        info = stats()
        print(f"Total extractions: {info['storage']['total_extractions']}")
        print(f"Cache hit rate: {info['cache']['hit_rate']}")
    """
    _ensure_initialized()
    
    return {
        "storage": _storage.get_stats(),
        "cache": _cache.stats(),
        "profiles": _profile_manager.list_profiles()
    }


def profiles() -> List[str]:
    """
    List available profiles
    
    Returns:
        List of profile names
    
    Example:
        available = profiles()
        # ['qa', 'interactive', 'general', 'accessibility', 'performance']
    """
    _ensure_initialized()
    return _profile_manager.list_profiles()


def compare(url: str, 
           profile1: str = "general",
           profile2: str = "interactive") -> Dict[str, Any]:
    """
    Compare extraction results between two profiles
    
    Args:
        url: URL to extract from
        profile1: First profile
        profile2: Second profile
    
    Returns:
        Comparison results
    
    Example:
        diff = compare("https://example.com", "general", "qa")
        print(f"General found {diff['profile1_count']} elements")
        print(f"QA found {diff['profile2_count']} elements")
    """
    elements1 = extract(url, profile=profile1, cache=False)
    elements2 = extract(url, profile=profile2, cache=False)
    
    # Find unique elements
    hashes1 = {e.hash() for e in elements1}
    hashes2 = {e.hash() for e in elements2}
    
    return {
        "url": url,
        "profile1": profile1,
        "profile1_count": len(elements1),
        "profile2": profile2,
        "profile2_count": len(elements2),
        "common": len(hashes1 & hashes2),
        "unique_to_profile1": len(hashes1 - hashes2),
        "unique_to_profile2": len(hashes2 - hashes1)
    }


def cleanup(days: int = 30):
    """
    Clean up old data
    
    Args:
        days: Remove data older than this many days
    
    Example:
        cleanup(7)  # Remove data older than 7 days
    """
    _ensure_initialized()
    _storage.cleanup_old_data(days)
    _cache.clear()


def export(url: str, 
          profile: Optional[str] = None,
          output_path: Optional[Path] = None) -> Path:
    """
    Export extraction to JSON file
    
    Args:
        url: URL that was extracted
        profile: Profile that was used
        output_path: Where to save (auto-generated if not provided)
    
    Returns:
        Path to exported file
    
    Example:
        path = export("https://example.com", profile="qa")
        print(f"Exported to {path}")
    """
    _ensure_initialized()
    
    # Get latest extraction
    result = _storage.get_latest(url, profile or "general")
    
    if not result:
        raise ValueError(f"No extraction found for {url} with profile {profile}")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = Path(f"export_{result.profile}_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.json")
    
    # Export
    _storage.export_to_json(result.id, output_path)
    
    return output_path


# Convenience aliases
get = extract  # Alias for extract
find = query   # Alias for query
info = stats   # Alias for stats