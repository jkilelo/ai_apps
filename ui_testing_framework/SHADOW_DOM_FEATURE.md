# Shadow DOM Extraction Feature

## Overview
Progressive enhancement pattern implementation for Shadow DOM support in the Ultimate Stealth Browser. This feature enables extraction of elements from within Shadow DOM boundaries while maintaining full backward compatibility.

## Implementation Details

### 1. Configuration (StealthConfig)
Added three new configuration fields to control Shadow DOM extraction:

```python
# Shadow DOM extraction settings
enable_shadow_dom_extraction: bool = Field(
    default=True, 
    description="Enable shadow DOM element extraction"
)
shadow_dom_max_depth: int = Field(
    default=5, 
    description="Maximum shadow DOM traversal depth"
)
shadow_dom_element_limit: int = Field(
    default=100, 
    description="Maximum elements per shadow root"
)
```

### 2. Element Data Enhancement (ElementData)
Added optional Shadow DOM metadata fields that don't break existing code:

```python
# Shadow DOM specific fields (optional for backward compatibility)
is_in_shadow_dom: bool = Field(default=False)
shadow_host_id: Optional[str] = Field(default=None)
shadow_root_mode: Optional[str] = Field(default=None)  # "open" or "closed"
shadow_dom_depth: int = Field(default=0)
shadow_dom_path: List[str] = Field(default_factory=list)
```

### 3. ShadowDOMExtractionStrategy Class
New extraction strategy that:
- Recursively traverses Shadow DOM trees
- Respects depth and element limits
- Extracts interactive elements from shadow roots
- Maintains shadow hierarchy information
- Generates shadow-aware selectors

### 4. Browser Integration
The `UltimateStealthBrowser` class conditionally loads the Shadow DOM strategy:

```python
if self.config.enable_shadow_dom_extraction:
    shadow_strategy = ShadowDOMExtractionStrategy(
        max_depth=self.config.shadow_dom_max_depth,
        element_limit=self.config.shadow_dom_element_limit
    )
    self.extraction_strategies.append(shadow_strategy)
```

## Usage Examples

### Basic Usage (Shadow DOM Enabled by Default)
```python
from browser import UltimateStealthBrowser, StealthConfig

# Shadow DOM extraction is enabled by default
browser = UltimateStealthBrowser()
await browser.initialize()

# Navigate to page with Shadow DOM
await browser.page.goto("https://example.com")

# Extract elements (includes shadow DOM elements)
result = await browser.extract_elements()

# Filter shadow DOM elements
shadow_elements = [e for e in result.elements if e.is_in_shadow_dom]
```

### Disable Shadow DOM Extraction
```python
# Create config with Shadow DOM disabled
config = StealthConfig(enable_shadow_dom_extraction=False)
browser = UltimateStealthBrowser(config)

# Only regular DOM elements will be extracted
```

### Custom Shadow DOM Settings
```python
# Configure shadow DOM extraction parameters
config = StealthConfig(
    enable_shadow_dom_extraction=True,
    shadow_dom_max_depth=10,      # Traverse up to 10 levels deep
    shadow_dom_element_limit=200  # Extract up to 200 elements per shadow root
)
browser = UltimateStealthBrowser(config)
```

### Accessing Shadow DOM Metadata
```python
# Extract elements
result = await browser.extract_elements()

for element in result.elements:
    if element.is_in_shadow_dom:
        print(f"Shadow element: {element.tag_name}")
        print(f"  Host ID: {element.shadow_host_id}")
        print(f"  Mode: {element.shadow_root_mode}")
        print(f"  Depth: {element.shadow_dom_depth}")
        print(f"  Path: {' > '.join(element.shadow_dom_path)}")
```

## Technical Details

### Shadow DOM Traversal Algorithm
1. Start from document.body
2. Detect elements with shadowRoot property
3. Recursively traverse shadow trees
4. Track depth and path for each element
5. Respect configured limits (depth and element count)
6. Extract interactive elements (buttons, inputs, links, etc.)

### Selector Generation
Shadow DOM elements get special selectors:
- **XPath**: Descriptive path showing shadow boundaries
- **CSS**: Uses `>>>` notation for shadow piercing (where supported)

Example:
```
Regular element: #button1
Shadow element: #host >>> #shadow-button
Nested shadow: #host >>> #nested-host >>> button
```

### Performance Considerations
- Extraction is additive (doesn't replace regular DOM extraction)
- Configurable limits prevent excessive traversal
- Async implementation for non-blocking operation
- Efficient JavaScript execution in browser context

## Backward Compatibility

### No Breaking Changes
- All new fields are optional with sensible defaults
- Existing code continues to work without modification
- Shadow DOM extraction can be completely disabled
- No changes to existing extraction logic

### Migration Path
1. **No action required**: Shadow DOM extraction is enabled by default
2. **Opt-out if needed**: Set `enable_shadow_dom_extraction=False`
3. **Gradual adoption**: Use shadow DOM metadata only when needed

## Testing

### Test Coverage
- Configuration defaults validation
- Backward compatibility (disabled state)
- Shadow DOM extraction functionality
- Nested shadow DOM handling
- Metadata field population
- Selector generation

### Running Tests
```bash
python test_shadow_dom.py
```

## Best Practices

### When to Use Shadow DOM Extraction
- Modern web applications using Web Components
- Pages with custom elements
- Complex UI frameworks (Polymer, LitElement, etc.)
- Testing shadow-isolated components

### Configuration Guidelines
- **Default settings** work for most cases
- **Increase depth** for deeply nested components
- **Increase limit** for component-heavy pages
- **Disable** for legacy applications without Shadow DOM

### Performance Optimization
```python
# For pages without Shadow DOM, disable for better performance
config = StealthConfig(enable_shadow_dom_extraction=False)

# For known shallow Shadow DOM, reduce depth
config = StealthConfig(shadow_dom_max_depth=2)

# For minimal extraction, reduce element limit
config = StealthConfig(shadow_dom_element_limit=20)
```

## Limitations

1. **Closed Shadow Roots**: Cannot access elements in closed shadow roots (browser security)
2. **XPath Limitations**: Standard XPath doesn't work across shadow boundaries
3. **CSS Selectors**: Shadow-piercing CSS (>>>) has limited browser support
4. **Performance**: Deep shadow trees may impact extraction time

## Future Enhancements

Potential improvements for future versions:
- Shadow DOM mutation observer for dynamic content
- Custom element detection and metadata
- Shadow DOM event handling
- Slot and slot assignment tracking
- Shadow CSS extraction and analysis

## Troubleshooting

### No Shadow Elements Found
- Verify the page actually uses Shadow DOM
- Check if shadow roots are "closed" (inaccessible)
- Increase `shadow_dom_max_depth` if deeply nested
- Increase `shadow_dom_element_limit` if many elements

### Performance Issues
- Reduce `shadow_dom_max_depth` for shallow trees
- Reduce `shadow_dom_element_limit` to extract fewer elements
- Disable shadow extraction if not needed

### Selector Issues
- Shadow DOM selectors are descriptive, not directly usable
- Use element IDs or classes within shadow roots
- Consider using JavaScript evaluation for shadow element interaction