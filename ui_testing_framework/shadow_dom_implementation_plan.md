# Shadow DOM Implementation Plan for browser.py

## Executive Summary
This document outlines multiple approaches to add comprehensive shadow DOM support to the browser.py module in the UI Testing Framework.

## Current State Analysis

### Limitations in browser.py
- **DOMExtractionStrategy** (line 1819): Uses `document.querySelectorAll()` which cannot cross shadow boundaries
- No shadow root detection or traversal
- No handling of web components
- Missing shadow-piercing selectors

### Existing Assets to Leverage
- Working implementation in `ui_testing_v2/components/element_extraction/strategies/shadow_dom_strategy.py`
- ElementData model already supports position and attributes
- Extraction strategy framework in place

## Implementation Approaches

### Approach 1: Enhanced DOMExtractionStrategy (Minimal Changes)
**Modify existing DOMExtractionStrategy to include shadow DOM traversal**

```python
async def extract(self, page: 'Page') -> List[ElementData]:
    """Extract elements using DOM inspection with shadow DOM support"""
    elements = []
    
    try:
        # Enhanced JavaScript with shadow DOM traversal
        raw_elements = await page.evaluate("""
            () => {
                const elements = [];
                const interactiveSelectors = [
                    'button', 'a', 'input', 'select', 'textarea',
                    '[role="button"]', '[onclick]', '[href]',
                    'label', 'form', '[type="submit"]'
                ];
                
                // Recursive function to traverse shadow DOM
                function traverseDOM(root, isShadow = false, shadowPath = []) {
                    // Query both light and shadow DOM
                    for (const selector of interactiveSelectors) {
                        const nodes = root.querySelectorAll(selector);
                        for (const node of nodes) {
                            const rect = node.getBoundingClientRect();
                            const computed = window.getComputedStyle(node);
                            
                            elements.push({
                                tag_name: node.tagName.toLowerCase(),
                                text_content: node.textContent?.trim() || '',
                                // ... existing properties ...
                                is_shadow_element: isShadow,
                                shadow_path: shadowPath.slice(),
                                shadow_host_tag: isShadow ? shadowPath[0]?.tag : null
                            });
                        }
                    }
                    
                    // Recursively check all elements for shadow roots
                    const allElements = root.querySelectorAll('*');
                    for (const element of allElements) {
                        if (element.shadowRoot) {
                            const hostInfo = {
                                tag: element.tagName.toLowerCase(),
                                id: element.id || null
                            };
                            traverseDOM(
                                element.shadowRoot, 
                                true, 
                                [...shadowPath, hostInfo]
                            );
                        }
                    }
                }
                
                // Start traversal from document
                traverseDOM(document);
                
                return elements;
            }
        """)
```

### Approach 2: Dedicated ShadowDOMExtractionStrategy (New Class)
**Add a new extraction strategy specifically for shadow DOM**

```python
class ShadowDOMExtractionStrategy(ExtractionStrategyBase):
    """Specialized shadow DOM extraction strategy"""
    
    async def extract(self, page: 'Page') -> List[ElementData]:
        """Extract elements from shadow DOM trees"""
        elements = []
        
        # Step 1: Find all shadow hosts
        shadow_hosts = await self._find_shadow_hosts(page)
        
        # Step 2: Process each shadow host
        for host in shadow_hosts:
            shadow_elements = await self._extract_from_shadow(page, host)
            elements.extend(shadow_elements)
        
        # Step 3: Handle nested shadow DOMs
        nested_elements = await self._handle_nested_shadows(page)
        elements.extend(nested_elements)
        
        return elements
    
    async def _find_shadow_hosts(self, page: 'Page') -> List[Dict]:
        """Detect all elements with shadow roots"""
        return await page.evaluate("""
            () => {
                const hosts = [];
                const all = document.querySelectorAll('*');
                
                for (const el of all) {
                    // Check for shadow root
                    if (el.shadowRoot) {
                        hosts.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            className: el.className,
                            hasOpenMode: el.shadowRoot.mode === 'open'
                        });
                    }
                    
                    // Check for custom elements (potential shadow hosts)
                    if (el.tagName.includes('-')) {
                        hosts.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            isCustomElement: true
                        });
                    }
                }
                
                return hosts;
            }
        """)
```

### Approach 3: Hybrid Playwright-JavaScript Solution
**Leverage Playwright's built-in shadow piercing with custom JavaScript**

```python
class HybridShadowExtractor:
    """Combines Playwright's shadow piercing with custom logic"""
    
    async def extract_with_shadow_piercing(self, page: 'Page') -> List[ElementData]:
        """Use Playwright's >>> operator for shadow piercing"""
        elements = []
        
        # Use Playwright's shadow-piercing selectors
        shadow_selectors = [
            '>>> button',
            '>>> a',
            '>>> input',
            '>>> [role="button"]'
        ]
        
        for selector in shadow_selectors:
            try:
                nodes = await page.query_selector_all(selector)
                for node in nodes:
                    element_data = await self._extract_node_data(node)
                    elements.append(element_data)
            except Exception as e:
                logger.debug(f"Shadow selector {selector} failed: {e}")
        
        return elements
    
    async def _extract_node_data(self, node) -> ElementData:
        """Extract data from a node handle"""
        return await node.evaluate("""
            (node) => {
                const rect = node.getBoundingClientRect();
                const shadowRoot = node.getRootNode();
                const isShadow = shadowRoot instanceof ShadowRoot;
                
                return {
                    tag_name: node.tagName.toLowerCase(),
                    text_content: node.textContent?.trim() || '',
                    is_shadow: isShadow,
                    shadow_host: isShadow ? shadowRoot.host.tagName : null,
                    // ... other properties
                };
            }
        """)
```

### Approach 4: Progressive Enhancement Pattern
**Add shadow DOM support without breaking existing functionality**

```python
class EnhancedDOMExtractor:
    """Progressive enhancement of DOM extraction"""
    
    def __init__(self):
        self.shadow_dom_enabled = True
        self.max_shadow_depth = 5
        self.shadow_element_limit = 100
    
    async def extract(self, page: 'Page') -> List[ElementData]:
        """Extract with optional shadow DOM support"""
        # First, get regular DOM elements (existing logic)
        regular_elements = await self._extract_light_dom(page)
        
        # Then, if enabled, add shadow DOM elements
        if self.shadow_dom_enabled:
            shadow_elements = await self._extract_shadow_dom(page)
            
            # Merge and deduplicate
            all_elements = self._merge_elements(regular_elements, shadow_elements)
        else:
            all_elements = regular_elements
        
        return all_elements
    
    async def _extract_shadow_dom(self, page: 'Page') -> List[ElementData]:
        """Progressive shadow DOM extraction"""
        return await page.evaluate(f"""
            () => {{
                const elements = [];
                const maxDepth = {self.max_shadow_depth};
                const maxElements = {self.shadow_element_limit};
                let elementCount = 0;
                
                function exploreShhadowDOM(root, depth = 0, path = []) {{
                    if (depth > maxDepth || elementCount > maxElements) return;
                    
                    // Find interactive elements in this root
                    const interactive = root.querySelectorAll(
                        'button, a, input, select, textarea, [role="button"]'
                    );
                    
                    for (const el of interactive) {{
                        if (elementCount++ > maxElements) break;
                        
                        elements.push({{
                            ...extractElementData(el),
                            shadow_depth: depth,
                            shadow_path: path.map(h => ({{
                                tag: h.tagName,
                                id: h.id
                            }}))
                        }});
                    }}
                    
                    // Recursively explore shadow roots
                    const withShadow = root.querySelectorAll('*');
                    for (const el of withShadow) {{
                        if (el.shadowRoot) {{
                            exploreShadowDOM(
                                el.shadowRoot,
                                depth + 1,
                                [...path, el]
                            );
                        }}
                    }}
                }}
                
                function extractElementData(el) {{
                    const rect = el.getBoundingClientRect();
                    return {{
                        tag_name: el.tagName.toLowerCase(),
                        text_content: el.textContent?.trim() || '',
                        id: el.id || null,
                        class_names: Array.from(el.classList || []),
                        is_visible: rect.width > 0 && rect.height > 0,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    }};
                }}
                
                // Start exploration
                exploreShadowDOM(document);
                
                return elements;
            }}
        """)
```

## Integration Strategy

### Phase 1: Add Shadow DOM Detection (Non-Breaking)
1. Add `is_shadow_element` field to ElementData
2. Implement shadow host detection in existing extraction
3. Log shadow DOM presence for metrics

### Phase 2: Implement Traversal (Experimental Flag)
1. Add `enable_shadow_dom` configuration option
2. Implement basic shadow DOM traversal when enabled
3. Test with known shadow DOM sites

### Phase 3: Full Integration (Default Enabled)
1. Make shadow DOM extraction default behavior
2. Add shadow-specific selector generation
3. Implement caching for performance

## Selector Generation for Shadow Elements

### Shadow-Piercing Selectors
```python
def generate_shadow_selector(element_path: List[Dict]) -> str:
    """Generate shadow-piercing selector"""
    parts = []
    
    for i, node in enumerate(element_path):
        if i == 0:
            # Root host
            if node.get('id'):
                parts.append(f"#{node['id']}")
            else:
                parts.append(node['tag'])
        else:
            # Shadow boundary
            parts.append(">>>")
            parts.append(node['tag'])
    
    return " ".join(parts)
```

### JavaScript Path Selectors
```python
def generate_js_selector(shadow_path: List[Dict]) -> str:
    """Generate JavaScript evaluation path"""
    js_parts = ["document"]
    
    for i, host in enumerate(shadow_path[:-1]):
        if host.get('id'):
            js_parts = [f"document.getElementById('{host['id']}')"]
        else:
            js_parts.append(f".querySelector('{host['tag']}')")
        js_parts.append(".shadowRoot")
    
    # Final element
    final = shadow_path[-1]
    if final.get('id'):
        js_parts.append(f".getElementById('{final['id']}')")
    else:
        js_parts.append(f".querySelector('{final['tag']}')")
    
    return "".join(js_parts)
```

## Testing Strategy

### Test Sites with Shadow DOM
1. YouTube (video player controls)
2. Chrome DevTools (extensive shadow DOM)
3. Polymer demos
4. Vaadin components
5. Salesforce Lightning components

### Unit Tests
```python
async def test_shadow_dom_extraction():
    """Test shadow DOM element extraction"""
    html = """
    <div id="host">Light DOM</div>
    <script>
        const host = document.getElementById('host');
        const shadow = host.attachShadow({mode: 'open'});
        shadow.innerHTML = '<button>Shadow Button</button>';
    </script>
    """
    
    # Extract elements
    elements = await extractor.extract_from_html(html)
    
    # Verify shadow element found
    shadow_buttons = [e for e in elements if e.is_shadow_element and e.tag_name == 'button']
    assert len(shadow_buttons) == 1
    assert shadow_buttons[0].text_content == 'Shadow Button'
```

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading**: Only traverse shadow DOM when needed
2. **Depth Limiting**: Max shadow nesting depth (default: 5)
3. **Element Limiting**: Max elements per shadow root (default: 50)
4. **Caching**: Cache shadow host detection results
5. **Parallel Processing**: Process multiple shadow roots concurrently

### Benchmarking
```python
class ShadowDOMBenchmark:
    async def benchmark_extraction(self, url: str):
        times = {
            'without_shadow': 0,
            'with_shadow': 0,
            'shadow_only': 0
        }
        
        # Measure without shadow DOM
        start = time.time()
        await extract_without_shadow(url)
        times['without_shadow'] = time.time() - start
        
        # Measure with shadow DOM
        start = time.time()
        await extract_with_shadow(url)
        times['with_shadow'] = time.time() - start
        
        # Calculate overhead
        times['shadow_overhead'] = times['with_shadow'] - times['without_shadow']
        
        return times
```

## Implementation Priority

### High Priority
1. Basic shadow root detection
2. Single-level shadow DOM traversal
3. Shadow element flagging

### Medium Priority
1. Nested shadow DOM support
2. Shadow-piercing selectors
3. Performance optimization

### Low Priority
1. Closed shadow root handling (limited by browser security)
2. Shadow DOM mutation observation
3. Advanced web component detection

## Backwards Compatibility

### Ensure No Breaking Changes
1. All new fields are optional
2. Shadow DOM extraction is additive
3. Existing extraction logic unchanged
4. Configuration flags for new features

## Recommended Implementation: Approach 4
**Progressive Enhancement Pattern** is recommended because:
1. No breaking changes to existing code
2. Can be enabled/disabled via configuration
3. Easy to test and rollback
4. Allows gradual rollout
5. Maintains performance for non-shadow DOM sites

## Next Steps
1. Implement shadow host detection
2. Add configuration flags
3. Create unit tests
4. Test on real sites
5. Performance benchmarking
6. Documentation update