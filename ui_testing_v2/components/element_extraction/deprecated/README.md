# Deprecated Element Extraction Components

This folder contains deprecated element extraction components that have been replaced by the unified extraction system.

## Deprecated Files

### Core Extractors (Replaced by `unified_extractor.py`)
- **element_extractor.py** - Original element extractor with AI integration
- **stealth_element_extractor.py** - Stealth-capable extractor (features merged into unified system)
- **dom_extractor.py** - DOM extraction logic (merged into `unified_dom_strategy.py`)
- **visual_extractor.py** - Visual detection logic (merged into `unified_visual_strategy.py`)

### Strategies (Replaced by unified strategies)
- **dom_strategy.py** - Original DOM strategy (replaced by `unified_dom_strategy.py`)
- **visual_strategy.py** - Original visual strategy (replaced by `unified_visual_strategy.py`)

## Migration Guide

### For `element_extractor.py`:
```python
# Old way
from element_extractor import ElementExtractor
extractor = ElementExtractor(browser_manager, ai_service)
elements = await extractor.extract_elements(url)

# New way
from element_extraction.unified_extractor import UnifiedElementExtractor
config = UnifiedExtractionConfig(mode=ExtractionMode.BALANCED)
extractor = UnifiedElementExtractor(config, ai_service=ai_service)
elements = await extractor.extract_playwright(page, url)
```

### For `stealth_element_extractor.py`:
```python
# Old way
from stealth_element_extractor import StealthElementExtractor
extractor = StealthElementExtractor()
elements = await extractor.extract_with_stealth(page)

# New way
from element_extraction.unified_extractor import UnifiedElementExtractor
config = UnifiedExtractionConfig(enable_stealth=True)
extractor = UnifiedElementExtractor(config)
elements = await extractor.extract_playwright(page)
```

### For `dom_extractor.py`:
```python
# Old way
from dom_extractor import DOMExtractor
extractor = DOMExtractor()
elements = extractor.extract_dom_elements(driver)

# New way
from element_extraction.strategies.unified_dom_strategy import UnifiedDOMStrategy
strategy = UnifiedDOMStrategy()
elements = strategy.extract_selenium(driver)
```

### For `visual_extractor.py`:
```python
# Old way
from visual_extractor import VisualExtractor
extractor = VisualExtractor()
elements = extractor.extract_visual_elements(screenshot)

# New way
from element_extraction.strategies.unified_visual_strategy import UnifiedVisualStrategy
strategy = UnifiedVisualStrategy()
elements = await strategy.extract_playwright(page)
```

## Why These Files Were Deprecated

1. **Code Duplication**: Multiple files contained identical or near-identical implementations
2. **Maintenance Burden**: Changes needed to be replicated across multiple files
3. **Inconsistent APIs**: Different extractors had different interfaces
4. **Limited Flexibility**: Hard-coded configurations and strategies
5. **Poor Separation of Concerns**: Business logic mixed with infrastructure code

## Benefits of the New System

1. **Single Source of Truth**: Core algorithms in one place
2. **Strategy Pattern**: Clean separation of extraction strategies
3. **Configurable**: Flexible configuration options
4. **Better Performance**: Parallel execution and caching
5. **Unified API**: Consistent interface across all strategies
6. **Extensible**: Easy to add new strategies

## Removal Timeline

These files are kept for reference and emergency rollback purposes. They will be permanently removed in the next major version release after confirming all functionality has been successfully migrated and tested.

## Note

If you're still using these deprecated components, please migrate to the unified system as soon as possible. The deprecated files are no longer maintained and may have compatibility issues with future updates.