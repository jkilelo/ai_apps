# Perception Layer Documentation

## Overview

The Perception Layer is responsible for capturing and processing the current state of web pages. It transforms complex DOM structures and visual information into simplified, structured representations that the Cognition Layer can reason about.

**Layer Position**: Layer 2 of 5 in the AI-First Smart Browser architecture

**Core Responsibility**: Multi-modal state capture ONLY (no action execution, no AI reasoning)

## Architecture Compliance

### ✅ What This Layer CAN Do:
- Import from Execution Layer (e.g., use Page objects)
- Process and simplify DOM structures
- Capture screenshots and apply visual annotations
- Extract page metadata and accessibility information
- Create structured data representations
- Prepare context for LLM processing

### ❌ What This Layer CANNOT Do:
- Execute browser actions (that's Execution's job)
- Make LLM/AI calls (that's Cognition's job)
- Store persistent data (that's Memory's job)
- Import from Cognition or Memory layers
- Modify page state in any way

## Components

### 1. DOMProcessor (`dom_processor.py`)

Processes raw HTML into simplified, structured representations.

**Key Features:**
- Removes non-content tags (scripts, styles, etc.)
- Extracts interactive elements with unique IDs
- Converts HTML to simplified markdown format
- Identifies forms, tables, links, and images
- Creates element mapping for action execution

**Usage Example:**
```python
processor = DOMProcessor()
dom_structure = processor.process_html(raw_html)
interactive_elements = processor.get_interactive_elements()
element_map = processor.get_element_map()
```

### 2. VisualAnnotator (`visual_annotator.py`)

Implements the Set-of-Marks (SoM) visual annotation system.

**Key Features:**
- Applies numbered labels to interactive elements
- Color-codes elements by type (per CLAUDE.md specs):
  - Buttons: `#FF6B6B` (red)
  - Links: `#4ECDC4` (cyan)
  - Inputs: `#95E77E` (green)
  - Selects: `#FFE66D` (yellow)
- Captures both clean and annotated screenshots
- Creates mapping between visual marks and selectors

**Usage Example:**
```python
annotator = VisualAnnotator()
result = await annotator.capture_clean_and_annotated(page, full_page=False)
# result contains screenshot, annotated_screenshot, element_map, etc.
```

### 3. StateObserver (`state_observer.py`)

Orchestrates all perception components to capture complete page state.

**Key Features:**
- Coordinates DOM processing and visual annotation
- Extracts comprehensive page metadata
- Captures accessibility information
- Detects page characteristics (errors, auth required, captcha)
- Compares states to identify changes
- Returns structured WebPageState objects

**Usage Example:**
```python
observer = StateObserver()
result = await observer.observe(
    page,
    capture_screenshot=True,
    annotate_visuals=True,
    extract_accessibility=False
)
if result.success:
    state = result.state  # WebPageState object
```

## Data Models (`models.py`)

### Core Models:

#### WebPageState
Complete representation of a web page at a point in time.
- `metadata`: Page URL, title, viewport, etc.
- `dom_structure`: Simplified DOM content
- `interactive_elements`: List of clickable/interactive elements
- `screenshot`: Raw screenshot bytes
- `annotated_screenshot`: Screenshot with SoM annotations
- `element_map`: Mapping from annotation IDs to selectors
- `accessibility`: Accessibility tree information

#### InteractiveElement
Represents a single interactive element on the page.
- `id`: Unique numerical identifier
- `selector`: CSS selector to locate element
- `type`: Element type (button, link, input, etc.)
- `text`: Visible text content
- `attributes`: Element attributes
- `bounding_box`: Position and size

#### DOMStructure
Simplified representation of page content.
- `distilled_content`: Markdown-formatted content
- `text_content`: Plain text extraction
- `headings`: Heading hierarchy
- `forms`: Form structures
- `tables`: Table data
- `links`: Link information

## Set-of-Marks (SoM) Implementation

The visual annotation system follows these specifications:

1. **Numbering**: Sequential integers starting from 1
2. **Positioning**: Top-left corner of element bounds
3. **Styling**: 14px bold white text on semi-transparent black background
4. **Color Coding**: Border color indicates element type
5. **Z-Index**: 10000 (above all page content)
6. **Cleanup**: Annotations are removed after screenshot capture

## Integration with Other Layers

### From Execution Layer (Layer 1):
- Receives Playwright Page objects
- Uses browser state without modifying it

### To Cognition Layer (Layer 3):
- Provides WebPageState objects
- Supplies element mappings for action planning
- Offers simplified context for LLM processing

## Performance Considerations

1. **DOM Processing**: Limited to 10,000 characters of text content
2. **Screenshot Capture**: Configurable full-page vs viewport
3. **Element Detection**: Only visible, interactive elements
4. **Caching**: StateObserver maintains last_state for comparison

## Testing

Comprehensive unit tests are provided in `tests/unit/test_perception_layer.py`:

- DOMProcessor: 6 tests covering HTML processing, element extraction
- VisualAnnotator: 4 tests for annotation and screenshot capture
- StateObserver: 6 tests for state observation and metadata extraction
- Layer Compliance: 2 tests ensuring no forbidden imports

Run tests:
```bash
pytest tests/unit/test_perception_layer.py -v
```

## Best Practices

1. **Always check element visibility** before annotation
2. **Limit text extraction** to prevent token overflow
3. **Handle malformed HTML** gracefully
4. **Preserve element attributes** needed for interaction
5. **Clean up annotations** after screenshot capture
6. **Use structured models** for all data exchange
7. **Log operations** for debugging (using loguru)
8. **Never execute actions** - only observe and report

## Common Issues and Solutions

### Issue: Elements not being detected
**Solution**: Check if elements are visible in viewport and not hidden by CSS

### Issue: Screenshots missing annotations
**Solution**: Ensure JavaScript injection completes before capture

### Issue: DOM processing too slow
**Solution**: Limit content extraction, remove unnecessary processing

### Issue: Memory usage high
**Solution**: Don't store raw HTML, use distilled representations

## Future Enhancements

- [ ] Implement visual diff detection between states
- [ ] Add OCR capabilities for image text extraction
- [ ] Enhance accessibility tree processing
- [ ] Support for Shadow DOM elements
- [ ] Implement element similarity scoring
- [ ] Add multi-language content detection

---

*Last Updated: 2025-01-05 | Layer: Perception (2/5) | Status: Production Ready*