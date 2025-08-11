"""
Relationship Mapping Strategy - Advanced graph-based analysis of element relationships
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict
from playwright.async_api import ElementHandle, Page

from ..advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class RelationshipMappingStrategy(ExtractionStrategyBase):
    """
    Map element relationships using graph algorithms to identify
    interactive elements based on their connections and context
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Relationship types to analyze
        self.relationship_types = {
            'parent_child': ['contains', 'nested_in'],
            'sibling': ['adjacent_to', 'grouped_with'],
            'label_target': ['labels', 'described_by'],
            'control': ['controls', 'toggles', 'expands'],
            'navigation': ['links_to', 'navigates_to'],
            'data': ['displays', 'updates', 'filters']
        }
        
        # Patterns that indicate relationships
        self.relationship_patterns = {
            'form_group': {
                'container': ['form', 'fieldset', '[role="group"]'],
                'elements': ['input', 'select', 'textarea', 'button'],
                'relationship': 'form_association'
            },
            'navigation_group': {
                'container': ['nav', '[role="navigation"]', 'ul.nav', 'ul.menu'],
                'elements': ['a', 'button', '[role="link"]'],
                'relationship': 'navigation_cluster'
            },
            'action_group': {
                'container': ['.actions', '.toolbar', '.button-group', '[role="toolbar"]'],
                'elements': ['button', 'a.button', '[role="button"]'],
                'relationship': 'action_cluster'
            },
            'list_item': {
                'container': ['ul', 'ol', '[role="list"]'],
                'elements': ['li', '[role="listitem"]'],
                'relationship': 'list_association'
            },
            'table_cell': {
                'container': ['table', '[role="table"]'],
                'elements': ['td button', 'td a', 'td input'],
                'relationship': 'table_action'
            }
        }
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements based on relationship analysis"""
        candidates = []
        
        try:
            # 1. Build element graph
            element_graph = await self._build_element_graph(context.page)
            logger.info(f"Relationship Strategy: Built graph with {len(element_graph)} nodes")
            
            # 2. Identify relationship clusters
            clusters = await self._identify_clusters(context.page)
            logger.info(f"Relationship Strategy: Found {len(clusters)} relationship clusters")
            
            # 3. Analyze form relationships
            form_elements = await self._analyze_form_relationships(context.page)
            logger.info(f"Relationship Strategy: Found {len(form_elements)} form-related elements")
            
            # 4. Analyze navigation relationships
            nav_elements = await self._analyze_navigation_relationships(context.page)
            logger.info(f"Relationship Strategy: Found {len(nav_elements)} navigation elements")
            
            # 5. Analyze control relationships
            control_elements = await self._analyze_control_relationships(context.page)
            logger.info(f"Relationship Strategy: Found {len(control_elements)} control elements")
            
            # 6. Analyze proximity relationships
            proximity_elements = await self._analyze_proximity_relationships(context.page)
            logger.info(f"Relationship Strategy: Found {len(proximity_elements)} proximity-related elements")
            
            # Combine all elements
            all_elements = []
            seen_elements = set()
            
            # Add elements with their relationship metadata
            for element_list in [clusters, form_elements, nav_elements, 
                               control_elements, proximity_elements]:
                for element_data in element_list:
                    element, metadata = element_data
                    try:
                        # Use element handle as unique identifier
                        element_id = await element.evaluate('el => el.outerHTML.substring(0, 100)')
                        if element_id not in seen_elements:
                            seen_elements.add(element_id)
                            
                            # Merge with graph data if available
                            if element in element_graph:
                                metadata['graph_data'] = element_graph[element]
                            
                            all_elements.append((element, metadata))
                    except:
                        all_elements.append((element, metadata))
            
            logger.info(f"Relationship Strategy: Analyzing {len(all_elements)} unique elements")
            
            # Create candidates with relationship scoring
            for element, metadata in all_elements:
                try:
                    candidate = await self._create_relationship_candidate(
                        element, metadata, context
                    )
                    if candidate:
                        candidates.append(candidate)
                except Exception as e:
                    logger.debug(f"Failed to create candidate: {e}")
                    continue
            
            # Sort by relationship strength
            candidates.sort(key=lambda c: c.confidence, reverse=True)
            
            logger.info(f"Relationship Strategy: Created {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Relationship mapping failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Relationship analysis provides moderate confidence boost"""
        return 0.15
    
    async def _build_element_graph(self, page: Page) -> Dict[ElementHandle, Dict]:
        """Build a graph of element relationships"""
        graph = {}
        
        try:
            # Get all potentially interactive elements
            elements = await page.query_selector_all('''
                button, a, input, select, textarea,
                [role="button"], [role="link"], [role="textbox"],
                [onclick], [tabindex]:not([tabindex="-1"]),
                .clickable, .btn, .button, .link
            ''')
            
            # Analyze relationships for each element
            for element in elements[:100]:  # Limit for performance
                try:
                    relationships = await element.evaluate('''el => {
                        const relationships = {
                            parents: [],
                            siblings: [],
                            children: [],
                            labels: [],
                            controls: [],
                            describedBy: []
                        };
                        
                        // Parent relationships
                        let parent = el.parentElement;
                        while (parent && parent !== document.body) {
                            if (parent.id || parent.className) {
                                relationships.parents.push({
                                    tag: parent.tagName.toLowerCase(),
                                    id: parent.id,
                                    classes: parent.className
                                });
                            }
                            parent = parent.parentElement;
                        }
                        
                        // Sibling relationships
                        const siblings = Array.from(el.parentElement?.children || []);
                        for (let sibling of siblings) {
                            if (sibling !== el && (sibling.tagName === 'BUTTON' || 
                                sibling.tagName === 'A' || sibling.tagName === 'INPUT')) {
                                relationships.siblings.push({
                                    tag: sibling.tagName.toLowerCase(),
                                    text: sibling.textContent?.trim().substring(0, 30)
                                });
                            }
                        }
                        
                        // Label relationships
                        const id = el.id;
                        if (id) {
                            const label = document.querySelector(`label[for="${id}"]`);
                            if (label) {
                                relationships.labels.push(label.textContent.trim());
                            }
                        }
                        
                        // ARIA relationships
                        const controls = el.getAttribute('aria-controls');
                        if (controls) {
                            const controlled = document.getElementById(controls);
                            if (controlled) {
                                relationships.controls.push({
                                    id: controls,
                                    tag: controlled.tagName.toLowerCase()
                                });
                            }
                        }
                        
                        const describedBy = el.getAttribute('aria-describedby');
                        if (describedBy) {
                            const descriptor = document.getElementById(describedBy);
                            if (descriptor) {
                                relationships.describedBy.push(descriptor.textContent.trim());
                            }
                        }
                        
                        return relationships;
                    }''')
                    
                    graph[element] = relationships
                    
                except Exception as e:
                    logger.debug(f"Failed to analyze element relationships: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to build element graph: {e}")
        
        return graph
    
    async def _identify_clusters(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Identify clusters of related elements"""
        clusters = []
        
        try:
            for pattern_name, pattern in self.relationship_patterns.items():
                # Find containers
                for container_selector in pattern['container']:
                    containers = await page.query_selector_all(container_selector)
                    
                    for container in containers[:5]:  # Limit per type
                        try:
                            # Find elements within container
                            element_selectors = ', '.join(pattern['elements'])
                            elements = await container.query_selector_all(element_selectors)
                            
                            if elements:
                                # Analyze cluster
                                cluster_data = await container.evaluate('''(cont, patternName) => {
                                    const rect = cont.getBoundingClientRect();
                                    return {
                                        pattern: patternName,
                                        elementCount: cont.querySelectorAll('button, a, input, select').length,
                                        hasLabel: !!cont.querySelector('label, legend, [role="heading"]'),
                                        isVisible: rect.width > 0 && rect.height > 0,
                                        containerTag: cont.tagName.toLowerCase(),
                                        containerRole: cont.getAttribute('role')
                                    };
                                }''', pattern_name)
                                
                                # Add elements from cluster
                                for element in elements:
                                    metadata = {
                                        'source': 'relationship_cluster',
                                        'cluster_type': pattern_name,
                                        'cluster_data': cluster_data,
                                        'relationship': pattern['relationship'],
                                        'cluster_size': len(elements)
                                    }
                                    clusters.append((element, metadata))
                                    
                        except Exception as e:
                            logger.debug(f"Failed to analyze cluster: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Failed to identify clusters: {e}")
        
        return clusters
    
    async def _analyze_form_relationships(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Analyze form-related element relationships"""
        form_elements = []
        
        try:
            # Find all forms
            forms = await page.query_selector_all('form, [role="form"]')
            
            for form in forms[:10]:  # Limit
                try:
                    # Get form metadata
                    form_data = await form.evaluate('''form => ({
                        id: form.id,
                        name: form.name,
                        action: form.action,
                        method: form.method,
                        hasSubmit: !!form.querySelector('[type="submit"], button:not([type="button"])'),
                        fieldCount: form.querySelectorAll('input, select, textarea').length
                    })''')
                    
                    # Get form controls
                    controls = await form.query_selector_all('''
                        input:not([type="hidden"]),
                        select,
                        textarea,
                        button,
                        [role="textbox"],
                        [role="combobox"]
                    ''')
                    
                    for element in controls:
                        try:
                            # Get element's form relationship
                            element_data = await element.evaluate('''el => {
                                const fieldset = el.closest('fieldset');
                                const label = el.labels?.[0] || 
                                            el.closest('label') ||
                                            document.querySelector(`label[for="${el.id}"]`);
                                
                                return {
                                    hasLabel: !!label,
                                    labelText: label?.textContent.trim(),
                                    inFieldset: !!fieldset,
                                    fieldsetLegend: fieldset?.querySelector('legend')?.textContent.trim(),
                                    isRequired: el.required || el.getAttribute('aria-required') === 'true',
                                    hasValidation: !!el.pattern || !!el.min || !!el.max
                                };
                            }''')
                            
                            metadata = {
                                'source': 'form_relationship',
                                'form_data': form_data,
                                'element_data': element_data,
                                'relationship': 'form_control',
                                'has_label': element_data['hasLabel']
                            }
                            
                            form_elements.append((element, metadata))
                            
                        except Exception as e:
                            logger.debug(f"Failed to analyze form element: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Failed to analyze form: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to analyze form relationships: {e}")
        
        return form_elements
    
    async def _analyze_navigation_relationships(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Analyze navigation-related element relationships"""
        nav_elements = []
        
        try:
            # Find navigation containers
            nav_containers = await page.query_selector_all('''
                nav, [role="navigation"],
                .navigation, .nav, .menu,
                header nav, footer nav
            ''')
            
            for nav in nav_containers[:10]:  # Limit
                try:
                    # Get navigation metadata
                    nav_data = await nav.evaluate('''nav => {
                        const links = nav.querySelectorAll('a, [role="link"]');
                        const items = nav.querySelectorAll('li, [role="menuitem"]');
                        
                        return {
                            linkCount: links.length,
                            itemCount: items.length,
                            hasAriaLabel: !!nav.getAttribute('aria-label'),
                            isLandmark: nav.tagName === 'NAV' || nav.getAttribute('role') === 'navigation',
                            depth: 0  // Will calculate depth
                        };
                    }''')
                    
                    # Get navigation items
                    items = await nav.query_selector_all('a, button, [role="link"], [role="menuitem"]')
                    
                    for element in items[:20]:  # Limit per nav
                        try:
                            # Analyze navigation hierarchy
                            hierarchy = await element.evaluate('''el => {
                                const ancestors = [];
                                let current = el.parentElement;
                                
                                while (current && !current.matches('nav, [role="navigation"]')) {
                                    if (current.matches('ul, ol, [role="list"]')) {
                                        ancestors.push('list');
                                    } else if (current.matches('li, [role="listitem"]')) {
                                        ancestors.push('item');
                                    }
                                    current = current.parentElement;
                                }
                                
                                return {
                                    depth: ancestors.filter(a => a === 'list').length,
                                    isNested: ancestors.length > 2,
                                    hasSubmenu: !!el.getAttribute('aria-haspopup') || 
                                               !!el.querySelector('ul, [role="menu"]')
                                };
                            }''')
                            
                            metadata = {
                                'source': 'navigation_relationship',
                                'nav_data': nav_data,
                                'hierarchy': hierarchy,
                                'relationship': 'navigation_item'
                            }
                            
                            nav_elements.append((element, metadata))
                            
                        except Exception as e:
                            logger.debug(f"Failed to analyze nav element: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Failed to analyze navigation: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to analyze navigation relationships: {e}")
        
        return nav_elements
    
    async def _analyze_control_relationships(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Analyze control relationships (buttons that control other elements)"""
        control_elements = []
        
        try:
            # Find elements with control attributes
            controllers = await page.query_selector_all('''
                [aria-controls],
                [aria-expanded],
                [data-toggle],
                [data-target],
                details > summary
            ''')
            
            for controller in controllers[:30]:  # Limit
                try:
                    # Get control metadata
                    control_data = await controller.evaluate('''el => {
                        const controls = el.getAttribute('aria-controls') || 
                                       el.getAttribute('data-target')?.replace('#', '');
                        const expanded = el.getAttribute('aria-expanded');
                        const pressed = el.getAttribute('aria-pressed');
                        
                        let targetElement = null;
                        if (controls) {
                            targetElement = document.getElementById(controls);
                        }
                        
                        return {
                            controlsId: controls,
                            hasTarget: !!targetElement,
                            targetTag: targetElement?.tagName.toLowerCase(),
                            isExpanded: expanded === 'true',
                            isPressed: pressed === 'true',
                            isToggle: !!expanded || !!pressed,
                            isDetails: el.tagName === 'SUMMARY'
                        };
                    }''')
                    
                    metadata = {
                        'source': 'control_relationship',
                        'control_data': control_data,
                        'relationship': 'controls',
                        'is_toggle': control_data['isToggle']
                    }
                    
                    control_elements.append((controller, metadata))
                    
                except Exception as e:
                    logger.debug(f"Failed to analyze control element: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to analyze control relationships: {e}")
        
        return control_elements
    
    async def _analyze_proximity_relationships(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Analyze elements based on visual proximity"""
        proximity_elements = []
        
        try:
            # Get clickable elements
            elements = await page.query_selector_all('''
                button, a, input[type="submit"], input[type="button"],
                [role="button"], [role="link"], [onclick]
            ''')
            
            # Sample elements for proximity analysis
            sample_size = min(len(elements), 50)
            sample_elements = elements[:sample_size]
            
            # Analyze proximity relationships
            for i, element in enumerate(sample_elements):
                try:
                    # Get element position
                    rect = await element.evaluate('el => el.getBoundingClientRect()')
                    
                    if rect['width'] > 0 and rect['height'] > 0:
                        # Find nearby elements
                        nearby_data = await page.evaluate('''(targetRect) => {
                            const threshold = 100; // pixels
                            const nearby = [];
                            
                            // Find elements within threshold distance
                            const candidates = document.querySelectorAll('button, a, input, label');
                            
                            for (let el of candidates) {
                                const elRect = el.getBoundingClientRect();
                                if (elRect.width === 0 || elRect.height === 0) continue;
                                
                                // Calculate distance
                                const dx = Math.abs(targetRect.x - elRect.x);
                                const dy = Math.abs(targetRect.y - elRect.y);
                                const distance = Math.sqrt(dx * dx + dy * dy);
                                
                                if (distance > 0 && distance < threshold) {
                                    nearby.push({
                                        tag: el.tagName.toLowerCase(),
                                        distance: Math.round(distance),
                                        position: dx < 10 ? 'vertical' : (dy < 10 ? 'horizontal' : 'diagonal'),
                                        text: el.textContent?.trim().substring(0, 30)
                                    });
                                }
                            }
                            
                            return {
                                nearbyCount: nearby.length,
                                nearest: nearby.slice(0, 3),
                                inButtonGroup: nearby.filter(n => n.tag === 'button' && n.position === 'horizontal').length > 1
                            };
                        }''', rect)
                        
                        if nearby_data['nearbyCount'] > 0:
                            metadata = {
                                'source': 'proximity_relationship',
                                'proximity_data': nearby_data,
                                'relationship': 'spatially_related',
                                'in_group': nearby_data['inButtonGroup']
                            }
                            
                            proximity_elements.append((element, metadata))
                            
                except Exception as e:
                    logger.debug(f"Failed to analyze proximity: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to analyze proximity relationships: {e}")
        
        return proximity_elements
    
    async def _create_relationship_candidate(
        self,
        element: ElementHandle,
        metadata: Dict[str, Any],
        context: ExtractionContext
    ) -> Optional[ElementCandidate]:
        """Create candidate from relationship analysis"""
        try:
            # Get element properties
            properties = await element.evaluate('''el => ({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim().substring(0, 200) || '',
                attributes: Array.from(el.attributes).reduce((acc, attr) => {
                    acc[attr.name] = attr.value;
                    return acc;
                }, {}),
                isVisible: el.offsetWidth > 0 && el.offsetHeight > 0,
                rect: el.getBoundingClientRect()
            })''')
            
            # Skip if not visible
            if not properties['isVisible']:
                return None
            
            # Generate selectors based on relationships
            selectors = await self._generate_relationship_selectors(element, properties, metadata)
            
            # Calculate confidence based on relationship strength
            base_confidence = self._calculate_relationship_score(metadata)
            
            # Boost for multiple relationship types
            relationship_count = 0
            if metadata.get('cluster_type'):
                relationship_count += 1
            if metadata.get('form_data'):
                relationship_count += 1
            if metadata.get('control_data'):
                relationship_count += 1
            if 'graph_data' in metadata:
                relationship_count += 1
            
            confidence = min(base_confidence + (relationship_count * 0.05), 0.95)
            
            candidate = ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.RELATIONSHIP_MAPPING},
                attributes=properties['attributes'],
                selectors=selectors,
                metadata={
                    'relationship_source': metadata['source'],
                    'relationship_type': metadata.get('relationship', 'unknown'),
                    'relationship_score': base_confidence,
                    'cluster_type': metadata.get('cluster_type'),
                    'in_form': 'form_data' in metadata,
                    'is_control': 'control_data' in metadata,
                    'has_label': metadata.get('has_label', False),
                    'element_text': properties['text'][:50] if properties['text'] else None
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create relationship candidate: {e}")
            return None
    
    def _calculate_relationship_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate score based on relationship strength"""
        score = 0.5  # Base score
        
        # Cluster relationships
        if metadata.get('cluster_type'):
            cluster_scores = {
                'form_group': 0.25,
                'navigation_group': 0.2,
                'action_group': 0.25,
                'list_item': 0.15,
                'table_cell': 0.2
            }
            score += cluster_scores.get(metadata['cluster_type'], 0.1)
        
        # Form relationships
        if metadata.get('form_data'):
            if metadata.get('has_label'):
                score += 0.15
            if metadata.get('element_data', {}).get('isRequired'):
                score += 0.1
        
        # Control relationships
        if metadata.get('control_data'):
            if metadata['control_data'].get('hasTarget'):
                score += 0.2
            if metadata['control_data'].get('isToggle'):
                score += 0.1
        
        # Navigation relationships
        if metadata.get('nav_data'):
            score += 0.15
            if metadata.get('hierarchy', {}).get('depth', 0) == 0:
                score += 0.05  # Top-level nav items
        
        # Proximity relationships
        if metadata.get('proximity_data'):
            if metadata['proximity_data'].get('inButtonGroup'):
                score += 0.15
        
        return min(score, 0.95)
    
    async def _generate_relationship_selectors(
        self,
        element: ElementHandle,
        properties: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors emphasizing relationships"""
        selectors = []
        attrs = properties['attributes']
        
        try:
            # ID selector (always preferred)
            if attrs.get('id'):
                selectors.append({
                    'type': 'css',
                    'value': f"#{attrs['id']}",
                    'score': 0.95,
                    'strategy': 'relationship-id'
                })
            
            # Form relationship selectors
            if metadata.get('form_data'):
                if attrs.get('name'):
                    form_id = metadata['form_data'].get('id')
                    if form_id:
                        selectors.append({
                            'type': 'css',
                            'value': f'#{form_id} [name="{attrs["name"]}"]',
                            'score': 0.85,
                            'strategy': 'relationship-form-field'
                        })
            
            # Control relationship selectors
            if metadata.get('control_data'):
                controls_id = metadata['control_data'].get('controlsId')
                if controls_id:
                    selectors.append({
                        'type': 'css',
                        'value': f'[aria-controls="{controls_id}"]',
                        'score': 0.9,
                        'strategy': 'relationship-controller'
                    })
            
            # Cluster-based selectors
            if metadata.get('cluster_type'):
                cluster_type = metadata['cluster_type']
                if cluster_type == 'navigation_group' and properties['text']:
                    selectors.append({
                        'type': 'xpath',
                        'value': f'//nav//a[contains(text(), "{properties["text"][:30]}")]',
                        'score': 0.7,
                        'strategy': 'relationship-nav-item'
                    })
                elif cluster_type == 'action_group':
                    selectors.append({
                        'type': 'css',
                        'value': f'.actions {properties["tag"]}',
                        'score': 0.6,
                        'strategy': 'relationship-action-group'
                    })
            
            # Proximity-based selector
            if metadata.get('proximity_data') and properties['text']:
                selectors.append({
                    'type': 'xpath',
                    'value': f'//{properties["tag"]}[normalize-space(text())="{properties["text"][:50]}"]',
                    'score': 0.5,
                    'strategy': 'relationship-proximity'
                })
                    
        except Exception as e:
            logger.debug(f"Failed to generate relationship selectors: {e}")
        
        return selectors