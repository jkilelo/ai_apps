"""
Visual Detection Strategy - Computer vision-based element detection
"""

import base64
import io
import logging
from typing import Any, Dict, List, Optional
import numpy as np
from PIL import Image
from playwright.async_api import ElementHandle

from ..advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class VisualDetectionStrategy(ExtractionStrategyBase):
    """
    Visual detection strategy using computer vision techniques
    for element identification and analysis
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Visual detection parameters
        self.min_element_size = 10  # Minimum size in pixels
        self.contrast_threshold = 30  # Minimum contrast for detection
        self.edge_threshold = 100  # Edge detection threshold
        
        # Common UI element visual patterns
        self.button_patterns = {
            'rounded_corners': True,
            'solid_background': True,
            'text_centered': True,
            'min_padding': 8
        }
        
        self.input_patterns = {
            'rectangular': True,
            'border': True,
            'min_height': 30,
            'aspect_ratio_range': (3, 20)
        }
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements using visual detection"""
        candidates = []
        
        try:
            # Take screenshot of the page
            screenshot = await self._capture_screenshot(context)
            if screenshot is None:
                return candidates
            
            # Detect visual regions
            visual_regions = await self._detect_visual_regions(screenshot, context)
            
            # Map visual regions to DOM elements
            for region in visual_regions:
                element = await self._map_region_to_element(region, context)
                if element:
                    candidate = await self._create_visual_candidate(element, region)
                    if candidate:
                        candidates.append(candidate)
            
            logger.info(f"Visual Strategy: Found {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            import traceback
            logger.error(f"Visual detection failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Visual detection provides moderate confidence boost"""
        return 0.2
    
    async def _capture_screenshot(self, context: ExtractionContext) -> Optional[np.ndarray]:
        """Capture page screenshot and convert to numpy array"""
        try:
            # Take screenshot
            screenshot_bytes = await context.page.screenshot(full_page=False)
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(screenshot_bytes))
            
            # Convert to numpy array
            screenshot_array = np.array(image)
            
            return screenshot_array
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None
    
    async def _detect_visual_regions(
        self,
        screenshot: np.ndarray,
        context: ExtractionContext
    ) -> List[Dict[str, Any]]:
        """Detect visual regions that might be interactive elements"""
        regions = []
        
        try:
            # Convert to grayscale for edge detection
            gray = self._convert_to_grayscale(screenshot)
            
            # Apply edge detection
            edges = self._detect_edges(gray)
            
            # Find contours (potential element boundaries)
            contours = self._find_contours(edges)
            
            # Analyze each contour
            for contour in contours:
                region = self._analyze_contour(contour, screenshot)
                if region and self._is_likely_interactive(region):
                    regions.append(region)
            
            # Sort by size and position
            regions.sort(key=lambda r: (r['y'], r['x']))
            
            return regions[:100]  # Limit to top 100 regions
            
        except Exception as e:
            logger.error(f"Visual region detection failed: {e}")
            return []
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            # RGB to grayscale conversion
            return np.dot(image[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        return image
    
    def _detect_edges(self, gray_image: np.ndarray) -> np.ndarray:
        """Simple edge detection using gradient"""
        # Simplified edge detection (in production, use cv2.Canny)
        height, width = gray_image.shape
        edges = np.zeros_like(gray_image)
        
        # Horizontal edges
        for y in range(1, height - 1):
            for x in range(width):
                diff = abs(int(gray_image[y + 1, x]) - int(gray_image[y - 1, x]))
                edges[y, x] = min(diff, 255)
        
        # Vertical edges
        for y in range(height):
            for x in range(1, width - 1):
                diff = abs(int(gray_image[y, x + 1]) - int(gray_image[y, x - 1]))
                edges[y, x] = max(edges[y, x], min(diff, 255))
        
        # Threshold
        edges = np.where(edges < self.edge_threshold, 0, 255)
        
        return edges
    
    def _find_contours(self, edges: np.ndarray) -> List[Dict[str, Any]]:
        """Find contours in edge image (simplified version)"""
        contours = []
        height, width = edges.shape
        visited = np.zeros_like(edges, dtype=bool)
        
        # Simple connected component analysis
        for y in range(height):
            for x in range(width):
                if edges[y, x] > 0 and not visited[y, x]:
                    # Found a new contour, trace it
                    contour = self._trace_contour(edges, visited, x, y)
                    if contour['area'] > self.min_element_size * self.min_element_size:
                        contours.append(contour)
        
        return contours
    
    def _trace_contour(
        self,
        edges: np.ndarray,
        visited: np.ndarray,
        start_x: int,
        start_y: int
    ) -> Dict[str, Any]:
        """Trace a contour using flood fill (simplified)"""
        height, width = edges.shape
        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y
        pixel_count = 0
        
        # Simple flood fill to find bounding box
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if visited[y, x] or edges[y, x] == 0:
                continue
            
            visited[y, x] = True
            pixel_count += 1
            
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            
            # Add neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                stack.append((x + dx, y + dy))
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x + 1,
            'height': max_y - min_y + 1,
            'area': pixel_count
        }
    
    def _analyze_contour(
        self,
        contour: Dict[str, Any],
        screenshot: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """Analyze contour to extract visual features"""
        try:
            x, y, w, h = contour['x'], contour['y'], contour['width'], contour['height']
            
            # Extract region from screenshot
            region = screenshot[y:y+h, x:x+w]
            
            # Calculate visual features
            features = {
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'aspect_ratio': w / h if h > 0 else 0,
                'area': w * h,
                'avg_color': self._calculate_average_color(region),
                'color_variance': self._calculate_color_variance(region),
                'has_text': self._detect_text_presence(region),
                'is_rectangular': self._is_rectangular(contour),
                'has_rounded_corners': self._has_rounded_corners(region)
            }
            
            return features
            
        except Exception:
            return None
    
    def _calculate_average_color(self, region: np.ndarray) -> List[float]:
        """Calculate average color of region"""
        if len(region.shape) == 3:
            return [float(np.mean(region[:, :, i])) for i in range(3)]
        else:
            avg = float(np.mean(region))
            return [avg, avg, avg]
    
    def _calculate_color_variance(self, region: np.ndarray) -> float:
        """Calculate color variance to detect uniform regions"""
        if len(region.shape) == 3:
            return float(np.mean([np.var(region[:, :, i]) for i in range(3)]))
        else:
            return float(np.var(region))
    
    def _detect_text_presence(self, region: np.ndarray) -> bool:
        """Detect if region likely contains text (simplified)"""
        # Convert to grayscale if needed
        if len(region.shape) == 3:
            gray = self._convert_to_grayscale(region)
        else:
            gray = region
        
        # High variance in small areas suggests text
        h, w = gray.shape
        if h < 20 or w < 20:
            return False
        
        # Check for high frequency content (text characteristics)
        variance = np.var(gray)
        return variance > 1000  # Threshold for text detection
    
    def _is_rectangular(self, contour: Dict[str, Any]) -> bool:
        """Check if contour is roughly rectangular"""
        # In a real implementation, we'd check the actual contour points
        # For now, we'll use area vs bounding box area
        bbox_area = contour['width'] * contour['height']
        fill_ratio = contour['area'] / bbox_area if bbox_area > 0 else 0
        return fill_ratio > 0.8  # 80% filled means roughly rectangular
    
    def _has_rounded_corners(self, region: np.ndarray) -> bool:
        """Detect if region has rounded corners (simplified)"""
        h, w = region.shape[:2]
        if h < 10 or w < 10:
            return False
        
        # Check corners for rounded pattern
        corner_size = min(5, h // 4, w // 4)
        
        # Check if corners have gradient (indicating roundness)
        # This is a very simplified check
        try:
            # Top-left corner
            corner = region[:corner_size, :corner_size]
            if len(corner.shape) == 3:
                corner = self._convert_to_grayscale(corner)
            
            # High variance in corner suggests rounded edge
            return np.var(corner) > 500
        except:
            return False
    
    def _is_likely_interactive(self, region: Dict[str, Any]) -> bool:
        """Determine if visual region is likely an interactive element"""
        # Size constraints
        width = float(region['width'])
        height = float(region['height'])
        
        if width < self.min_element_size or height < self.min_element_size:
            return False
        
        # Aspect ratio constraints (avoid very thin lines)
        aspect_ratio = float(region['aspect_ratio'])
        if aspect_ratio > 50 or aspect_ratio < 0.02:
            return False
        
        # Color variance (uniform regions are more likely to be buttons)
        color_variance = float(region['color_variance'])
        if color_variance < 100:  # Solid color
            if bool(region['has_text']):  # Solid color with text = likely button
                return True
        
        # Rectangular regions with moderate size
        if bool(region['is_rectangular']):
            if 20 <= height <= 100 and 40 <= width <= 400:
                return True
        
        # Regions with rounded corners (common in modern UI)
        if bool(region['has_rounded_corners']) and bool(region['has_text']):
            return True
        
        return False
    
    async def _map_region_to_element(
        self,
        region: Dict[str, Any],
        context: ExtractionContext
    ) -> Optional[ElementHandle]:
        """Map visual region to DOM element"""
        try:
            # Get element at region center
            center_x = region['x'] + region['width'] // 2
            center_y = region['y'] + region['height'] // 2
            
            element = await context.page.evaluate_handle(
                f'''() => document.elementFromPoint({center_x}, {center_y})'''
            )
            
            if not element:
                return None
            
            # Verify element bounds roughly match region
            box = await element.bounding_box()
            if box:
                # Allow some tolerance
                tolerance = 10
                if (abs(box['x'] - region['x']) < tolerance and
                    abs(box['y'] - region['y']) < tolerance and
                    abs(box['width'] - region['width']) < tolerance * 2 and
                    abs(box['height'] - region['height']) < tolerance * 2):
                    return element
            
            # Try to find parent that matches better
            parent = await element.evaluate_handle('el => el.parentElement')
            if parent:
                parent_box = await parent.bounding_box()
                if parent_box:
                    if (abs(parent_box['x'] - region['x']) < tolerance and
                        abs(parent_box['y'] - region['y']) < tolerance):
                        return parent
            
            return element  # Return original if no better match
            
        except Exception as e:
            logger.debug(f"Failed to map region to element: {e}")
            return None
    
    async def _create_visual_candidate(
        self,
        element: ElementHandle,
        region: Dict[str, Any]
    ) -> Optional[ElementCandidate]:
        """Create element candidate from visual detection"""
        try:
            # Get element properties
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            text = await element.text_content()
            
            # Calculate confidence based on visual features
            confidence = self._calculate_visual_confidence(region, tag_name)
            
            # Generate visual-based selectors
            selectors = await self._generate_visual_selectors(element, region)
            
            attributes = await element.evaluate('''el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }''')
            
            candidate = ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.VISUAL_DETECTION},
                attributes=attributes,
                selectors=selectors,
                metadata={
                    'visual_region': region,
                    'detection_method': 'visual',
                    'has_text': region['has_text'],
                    'is_rectangular': region['is_rectangular'],
                    'has_rounded_corners': region['has_rounded_corners']
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create visual candidate: {e}")
            return None
    
    def _calculate_visual_confidence(
        self,
        region: Dict[str, Any],
        tag_name: str
    ) -> float:
        """Calculate confidence based on visual features"""
        confidence = 0.5  # Base confidence for visual detection
        
        # Boost for button-like appearance
        if region['has_rounded_corners'] and region['has_text']:
            confidence += 0.2
        
        # Boost for rectangular solid regions
        if region['is_rectangular'] and region['color_variance'] < 100:
            confidence += 0.15
        
        # Boost for appropriate size
        if 30 <= region['height'] <= 60 and 60 <= region['width'] <= 200:
            confidence += 0.1
        
        # Boost for known interactive tags
        if tag_name in ['button', 'a', 'input']:
            confidence += 0.15
        
        return min(confidence, 0.9)
    
    async def _generate_visual_selectors(
        self,
        element: ElementHandle,
        region: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors based on visual properties"""
        selectors = []
        
        try:
            # Try to generate selector based on visual position
            selector = await element.evaluate('''(el) => {
                const rect = el.getBoundingClientRect();
                const path = [];
                let current = el;
                
                while (current && current !== document.body) {
                    const tag = current.tagName.toLowerCase();
                    const id = current.id;
                    
                    if (id) {
                        path.unshift(`#${id}`);
                        break;
                    } else {
                        const parent = current.parentElement;
                        if (parent) {
                            const index = Array.from(parent.children).indexOf(current);
                            path.unshift(`${tag}:nth-child(${index + 1})`);
                        } else {
                            path.unshift(tag);
                        }
                    }
                    current = current.parentElement;
                }
                
                return path.join(' > ');
            }''')
            
            if selector:
                selectors.append({
                    'type': 'css',
                    'value': selector,
                    'score': 0.4,
                    'strategy': 'visual-position'
                })
            
            # Add position-based selector as backup
            selectors.append({
                'type': 'css',
                'value': f'*[style*="position"][style*="{region["x"]}"]',
                'score': 0.2,
                'strategy': 'visual-style'
            })
            
        except Exception:
            pass
        
        return selectors