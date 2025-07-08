"""
Enhanced Dynamic Content Handler for Modern Web Applications
Handles complex SPAs, infinite scroll, real-time updates, and framework-specific behaviors
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from playwright.async_api import Page, ElementHandle

logger = logging.getLogger(__name__)


class FrameworkType(Enum):
    """Supported frontend frameworks"""
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    NEXT = "next"
    NUXT = "nuxt"
    UNKNOWN = "unknown"


class ContentLoadState(Enum):
    """Dynamic content loading states"""
    INITIAL = "initial"
    LOADING = "loading"
    PARTIAL = "partial"
    COMPLETE = "complete"
    ERROR = "error"
    IDLE = "idle"


@dataclass
class MutationRecord:
    """Record of DOM mutations"""
    timestamp: float
    mutation_type: str
    target: str
    added_nodes: int
    removed_nodes: int
    attributes_changed: List[str]


@dataclass
class DynamicRegion:
    """Represents a dynamic region in the page"""
    selector: str
    region_type: str  # infinite-scroll, live-update, lazy-load, etc.
    update_frequency: float  # updates per second
    last_update: float
    mutation_count: int


class DynamicContentHandler:
    """Advanced handler for dynamic web content"""
    
    # Mutation observer script
    MUTATION_OBSERVER_SCRIPT = """
    (() => {
        if (window.__dynamicContentObserver) return;
        
        window.__mutationRecords = [];
        window.__mutationStats = {
            total: 0,
            byType: {},
            byTarget: {},
            regions: new Map()
        };
        
        const observer = new MutationObserver((mutations) => {
            const now = Date.now();
            mutations.forEach((mutation) => {
                const record = {
                    timestamp: now,
                    type: mutation.type,
                    target: mutation.target.tagName || 'TEXT',
                    targetId: mutation.target.id,
                    targetClass: mutation.target.className,
                    addedNodes: mutation.addedNodes.length,
                    removedNodes: mutation.removedNodes.length,
                    attributes: mutation.attributeName ? [mutation.attributeName] : []
                };
                
                window.__mutationRecords.push(record);
                window.__mutationStats.total++;
                
                // Track mutation frequency by region
                const selector = mutation.target.id ? `#${mutation.target.id}` : 
                               mutation.target.className ? `.${mutation.target.className.split(' ')[0]}` : 
                               mutation.target.tagName;
                
                if (!window.__mutationStats.regions.has(selector)) {
                    window.__mutationStats.regions.set(selector, {
                        count: 0,
                        firstSeen: now,
                        lastSeen: now
                    });
                }
                
                const regionStats = window.__mutationStats.regions.get(selector);
                regionStats.count++;
                regionStats.lastSeen = now;
            });
            
            // Limit record storage
            if (window.__mutationRecords.length > 1000) {
                window.__mutationRecords = window.__mutationRecords.slice(-500);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeOldValue: true,
            characterData: true
        });
        
        window.__dynamicContentObserver = observer;
        
        // Helper functions
        window.__getDynamicRegions = () => {
            const regions = [];
            for (const [selector, stats] of window.__mutationStats.regions) {
                const duration = (stats.lastSeen - stats.firstSeen) / 1000;
                if (duration > 0) {
                    regions.push({
                        selector,
                        mutationCount: stats.count,
                        frequency: stats.count / duration,
                        duration
                    });
                }
            }
            return regions.sort((a, b) => b.frequency - a.frequency).slice(0, 20);
        };
        
        window.__getMutationSummary = () => {
            return {
                total: window.__mutationStats.total,
                records: window.__mutationRecords.slice(-100),
                dynamicRegions: window.__getDynamicRegions()
            };
        };
    })();
    """
    
    # Framework detection script
    FRAMEWORK_DETECTION_SCRIPT = """
    (() => {
        const detections = {
            react: {
                detected: false,
                version: null,
                indicators: []
            },
            vue: {
                detected: false,
                version: null,
                indicators: []
            },
            angular: {
                detected: false,
                version: null,
                indicators: []
            },
            svelte: {
                detected: false,
                version: null,
                indicators: []
            }
        };
        
        // React detection
        if (window.React || window.ReactDOM) {
            detections.react.detected = true;
            detections.react.version = window.React?.version || 'unknown';
            detections.react.indicators.push('window.React');
        }
        if (document.querySelector('[data-reactroot], [data-react-root], [data-reactid]')) {
            detections.react.detected = true;
            detections.react.indicators.push('React root element');
        }
        if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
            detections.react.detected = true;
            detections.react.indicators.push('React DevTools');
        }
        
        // Vue detection
        if (window.Vue) {
            detections.vue.detected = true;
            detections.vue.version = window.Vue.version || 'unknown';
            detections.vue.indicators.push('window.Vue');
        }
        const vueApp = document.querySelector('#app, [data-v-]');
        if (vueApp && (vueApp.__vue__ || vueApp._vnode)) {
            detections.vue.detected = true;
            detections.vue.indicators.push('Vue app instance');
        }
        
        // Angular detection
        if (window.ng || window.angular) {
            detections.angular.detected = true;
            detections.angular.version = window.angular?.version?.full || 'unknown';
            detections.angular.indicators.push('window.angular');
        }
        if (document.querySelector('[ng-app], [data-ng-app], .ng-scope, [ng-controller]')) {
            detections.angular.detected = true;
            detections.angular.indicators.push('Angular directives');
        }
        if (window.getAllAngularRootElements) {
            detections.angular.detected = true;
            detections.angular.indicators.push('Angular root elements');
        }
        
        // Next.js detection
        if (window.__NEXT_DATA__) {
            detections.next = {
                detected: true,
                version: window.__NEXT_DATA__.version || 'unknown',
                indicators: ['__NEXT_DATA__']
            };
        }
        
        // Nuxt detection
        if (window.$nuxt || window.__NUXT__) {
            detections.nuxt = {
                detected: true,
                indicators: ['Nuxt globals']
            };
        }
        
        return detections;
    })();
    """
    
    # Infinite scroll detection script
    INFINITE_SCROLL_DETECTION = """
    (() => {
        const scrollContainers = [];
        
        // Check main window
        if (document.body.scrollHeight > window.innerHeight * 2) {
            scrollContainers.push({
                element: 'window',
                scrollHeight: document.body.scrollHeight,
                clientHeight: window.innerHeight,
                hasScroll: true
            });
        }
        
        // Check common scroll containers
        const selectors = [
            '[class*="scroll"]', '[class*="infinite"]', '[class*="feed"]',
            '[class*="list"]', '[class*="container"]', 'main', 'article'
        ];
        
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                if (el.scrollHeight > el.clientHeight) {
                    scrollContainers.push({
                        element: el.tagName + (el.id ? '#' + el.id : ''),
                        selector: el.id ? '#' + el.id : selector,
                        scrollHeight: el.scrollHeight,
                        clientHeight: el.clientHeight,
                        hasScroll: true
                    });
                }
            });
        });
        
        return scrollContainers;
    })();
    """
    
    def __init__(self):
        self.detected_framework: Optional[FrameworkType] = None
        self.dynamic_regions: List[DynamicRegion] = []
        self.mutation_history: List[MutationRecord] = []
        self.content_state = ContentLoadState.INITIAL
        
    async def initialize(self, page: Page) -> None:
        """Initialize dynamic content monitoring"""
        logger.info("Initializing dynamic content handler")
        
        # Inject mutation observer
        await page.evaluate(self.MUTATION_OBSERVER_SCRIPT)
        
        # Detect framework
        self.detected_framework = await self.detect_framework(page)
        logger.info(f"Detected framework: {self.detected_framework.value}")
        
        # Start monitoring
        asyncio.create_task(self._monitor_mutations(page))
        
    async def detect_framework(self, page: Page) -> FrameworkType:
        """Detect the frontend framework being used"""
        try:
            detections = await page.evaluate(self.FRAMEWORK_DETECTION_SCRIPT)
            
            # Prioritize detection
            if detections.get("next", {}).get("detected"):
                return FrameworkType.NEXT
            elif detections.get("nuxt", {}).get("detected"):
                return FrameworkType.NUXT
            elif detections.get("react", {}).get("detected"):
                return FrameworkType.REACT
            elif detections.get("vue", {}).get("detected"):
                return FrameworkType.VUE
            elif detections.get("angular", {}).get("detected"):
                return FrameworkType.ANGULAR
            else:
                return FrameworkType.UNKNOWN
                
        except Exception as e:
            logger.error(f"Framework detection failed: {e}")
            return FrameworkType.UNKNOWN
    
    async def wait_for_dynamic_content(self, page: Page, timeout: int = 30000) -> None:
        """Intelligent wait for dynamic content to load"""
        logger.info("Waiting for dynamic content to stabilize")
        
        start_time = asyncio.get_event_loop().time()
        stability_checks = 0
        required_stable_checks = 3
        check_interval = 500  # ms
        
        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
            try:
                # Get mutation summary
                summary = await page.evaluate("window.__getMutationSummary ? window.__getMutationSummary() : {total: 0}")
                current_mutations = summary.get("total", 0)
                
                # Check network activity
                network_idle = await self._check_network_idle(page)
                
                # Framework-specific checks
                framework_idle = await self._check_framework_idle(page)
                
                # Check for active animations
                animations_complete = await self._check_animations_complete(page)
                
                # Determine if content is stable
                if network_idle and framework_idle and animations_complete:
                    if len(self.mutation_history) >= 2:
                        recent_rate = self._calculate_mutation_rate()
                        if recent_rate < 0.5:  # Less than 0.5 mutations per second
                            stability_checks += 1
                            if stability_checks >= required_stable_checks:
                                logger.info("Dynamic content stabilized")
                                self.content_state = ContentLoadState.COMPLETE
                                break
                    else:
                        stability_checks += 1
                else:
                    stability_checks = 0
                    self.content_state = ContentLoadState.LOADING
                
                # Store mutation record
                self.mutation_history.append(MutationRecord(
                    timestamp=asyncio.get_event_loop().time(),
                    mutation_type="summary",
                    target="page",
                    added_nodes=current_mutations,
                    removed_nodes=0,
                    attributes_changed=[]
                ))
                
                # Keep history size manageable
                if len(self.mutation_history) > 100:
                    self.mutation_history = self.mutation_history[-50:]
                
                await asyncio.sleep(check_interval / 1000)
                
            except Exception as e:
                logger.error(f"Error during dynamic content wait: {e}")
                break
        
        # Identify dynamic regions
        await self._identify_dynamic_regions(page)
        
    async def _monitor_mutations(self, page: Page) -> None:
        """Continuously monitor DOM mutations"""
        while True:
            try:
                if page.is_closed():
                    break
                    
                summary = await page.evaluate("window.__getMutationSummary ? window.__getMutationSummary() : null")
                if summary and summary.get("dynamicRegions"):
                    self.dynamic_regions = [
                        DynamicRegion(
                            selector=region["selector"],
                            region_type=self._classify_region_type(region),
                            update_frequency=region["frequency"],
                            last_update=asyncio.get_event_loop().time(),
                            mutation_count=region["mutationCount"]
                        )
                        for region in summary["dynamicRegions"]
                    ]
                    
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.debug(f"Mutation monitoring error: {e}")
                break
    
    async def _check_network_idle(self, page: Page, threshold: int = 500) -> bool:
        """Check if network is idle"""
        try:
            # Use Playwright's wait_for_load_state with timeout
            await page.wait_for_load_state("networkidle", timeout=threshold)
            return True
        except:
            return False
    
    async def _check_framework_idle(self, page: Page) -> bool:
        """Check if framework is idle based on detected framework"""
        if self.detected_framework == FrameworkType.REACT:
            return await self._check_react_idle(page)
        elif self.detected_framework == FrameworkType.VUE:
            return await self._check_vue_idle(page)
        elif self.detected_framework == FrameworkType.ANGULAR:
            return await self._check_angular_idle(page)
        else:
            return True
    
    async def _check_react_idle(self, page: Page) -> bool:
        """Check if React is idle"""
        try:
            is_idle = await page.evaluate("""
                () => {
                    // Check React Fiber
                    const hasPendingWork = () => {
                        const root = document.querySelector('#root')._reactRootContainer;
                        return root && root._internalRoot && 
                               root._internalRoot.pendingTime !== 0;
                    };
                    
                    // Check for pending effects
                    const hasPendingEffects = window.__REACT_DEVTOOLS_GLOBAL_HOOK__?.
                        renderers?.size > 0;
                    
                    return !hasPendingWork() && !hasPendingEffects;
                }
            """)
            return is_idle
        except:
            return True
    
    async def _check_vue_idle(self, page: Page) -> bool:
        """Check if Vue is idle"""
        try:
            is_idle = await page.evaluate("""
                () => {
                    const app = document.querySelector('#app');
                    if (app && app.__vue__) {
                        // Check Vue 2
                        return !app.__vue__.$el._pending;
                    } else if (app && app._vnode) {
                        // Check Vue 3
                        return !app._vnode.component?.isMounted === false;
                    }
                    return true;
                }
            """)
            return is_idle
        except:
            return True
    
    async def _check_angular_idle(self, page: Page) -> bool:
        """Check if Angular is idle"""
        try:
            is_idle = await page.evaluate("""
                () => {
                    if (window.getAllAngularTestabilities) {
                        const testabilities = window.getAllAngularTestabilities();
                        return testabilities.every(t => t.isStable());
                    }
                    return true;
                }
            """)
            return is_idle
        except:
            return True
    
    async def _check_animations_complete(self, page: Page) -> bool:
        """Check if CSS animations and transitions are complete"""
        try:
            animations_done = await page.evaluate("""
                () => {
                    const animations = document.getAnimations();
                    return animations.every(animation => 
                        animation.playState === 'finished' || 
                        animation.playState === 'idle'
                    );
                }
            """)
            return animations_done
        except:
            return True
    
    def _calculate_mutation_rate(self) -> float:
        """Calculate recent mutation rate per second"""
        if len(self.mutation_history) < 2:
            return 0.0
            
        recent = self.mutation_history[-10:]  # Last 10 records
        if len(recent) < 2:
            return 0.0
            
        time_span = recent[-1].timestamp - recent[0].timestamp
        if time_span == 0:
            return 0.0
            
        total_mutations = sum(r.added_nodes for r in recent)
        return total_mutations / time_span
    
    def _classify_region_type(self, region: Dict[str, Any]) -> str:
        """Classify the type of dynamic region"""
        selector = region.get("selector", "").lower()
        frequency = region.get("frequency", 0)
        
        # Classify based on selector patterns
        if any(keyword in selector for keyword in ["infinite", "scroll", "feed"]):
            return "infinite-scroll"
        elif any(keyword in selector for keyword in ["chat", "message", "comment"]):
            return "live-chat"
        elif any(keyword in selector for keyword in ["chart", "graph", "metric"]):
            return "real-time-data"
        elif frequency > 10:  # More than 10 updates per second
            return "high-frequency-update"
        elif frequency > 1:
            return "live-update"
        else:
            return "lazy-load"
    
    async def _identify_dynamic_regions(self, page: Page) -> None:
        """Identify and classify dynamic regions on the page"""
        try:
            summary = await page.evaluate("window.__getMutationSummary ? window.__getMutationSummary() : null")
            if not summary:
                return
                
            regions = summary.get("dynamicRegions", [])
            self.dynamic_regions = []
            
            for region in regions:
                if region["frequency"] > 0.1:  # At least 0.1 updates per second
                    dynamic_region = DynamicRegion(
                        selector=region["selector"],
                        region_type=self._classify_region_type(region),
                        update_frequency=region["frequency"],
                        last_update=asyncio.get_event_loop().time(),
                        mutation_count=region["mutationCount"]
                    )
                    self.dynamic_regions.append(dynamic_region)
                    logger.info(f"Identified dynamic region: {dynamic_region.selector} "
                              f"({dynamic_region.region_type}) - "
                              f"{dynamic_region.update_frequency:.2f} updates/sec")
                              
        except Exception as e:
            logger.error(f"Failed to identify dynamic regions: {e}")
    
    async def handle_infinite_scroll(self, page: Page, max_scrolls: int = 10) -> List[Dict[str, Any]]:
        """Handle infinite scroll to load all content"""
        logger.info("Handling infinite scroll")
        
        scroll_containers = await page.evaluate(self.INFINITE_SCROLL_DETECTION)
        if not scroll_containers:
            logger.info("No infinite scroll containers detected")
            return []
        
        loaded_content = []
        
        for container in scroll_containers:
            if container["element"] == "window":
                # Scroll main window
                loaded_content.extend(
                    await self._scroll_window(page, max_scrolls)
                )
            else:
                # Scroll specific container
                loaded_content.extend(
                    await self._scroll_container(page, container["selector"], max_scrolls)
                )
        
        return loaded_content
    
    async def _scroll_window(self, page: Page, max_scrolls: int) -> List[Dict[str, Any]]:
        """Scroll the main window and track loaded content"""
        loaded_content = []
        previous_height = 0
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            # Get current height
            current_height = await page.evaluate("document.body.scrollHeight")
            
            if current_height == previous_height:
                logger.info("No new content loaded after scroll")
                break
            
            # Scroll to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for new content
            await self.wait_for_dynamic_content(page, timeout=5000)
            
            # Track newly loaded elements
            new_elements = await page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*')).slice(-100);
                    return elements.map(el => ({
                        tag: el.tagName,
                        id: el.id,
                        class: el.className,
                        text: el.textContent?.slice(0, 100)
                    }));
                }
            """)
            
            loaded_content.extend(new_elements)
            previous_height = current_height
            scroll_count += 1
            
            logger.info(f"Scroll {scroll_count}: Loaded {len(new_elements)} new elements")
        
        return loaded_content
    
    async def _scroll_container(self, page: Page, selector: str, max_scrolls: int) -> List[Dict[str, Any]]:
        """Scroll a specific container and track loaded content"""
        loaded_content = []
        
        try:
            container = await page.query_selector(selector)
            if not container:
                return []
            
            for i in range(max_scrolls):
                # Scroll container
                await container.evaluate("el => el.scrollTop = el.scrollHeight")
                
                # Wait for new content
                await self.wait_for_dynamic_content(page, timeout=3000)
                
                # Check if more content was loaded
                new_height = await container.evaluate("el => el.scrollHeight")
                if new_height == await container.evaluate("el => el.scrollTop + el.clientHeight"):
                    break
                    
        except Exception as e:
            logger.error(f"Error scrolling container {selector}: {e}")
        
        return loaded_content
    
    def get_dynamic_regions_summary(self) -> Dict[str, Any]:
        """Get summary of detected dynamic regions"""
        return {
            "total_regions": len(self.dynamic_regions),
            "regions": [
                {
                    "selector": region.selector,
                    "type": region.region_type,
                    "update_frequency": region.update_frequency,
                    "mutation_count": region.mutation_count
                }
                for region in self.dynamic_regions
            ],
            "most_active": max(self.dynamic_regions, key=lambda r: r.update_frequency).selector
                           if self.dynamic_regions else None,
            "framework": self.detected_framework.value
        }