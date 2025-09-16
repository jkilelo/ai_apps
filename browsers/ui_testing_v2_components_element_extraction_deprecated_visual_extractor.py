"""
Unified Visual Extractor - Advanced visual element extraction with stealth capabilities

This module provides visual-based element extraction using computer vision techniques
combined with stealth browser capabilities for anti-bot evasion.
"""

import base64
import io
import logging
import asyncio
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from PIL import Image
from playwright.async_api import ElementHandle, Page

from ...core.stealth_browser import create_stealth_browser
from ...core.browser_profiles import ProfileType
from .advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class VisualExtractor(ExtractionStrategyBase):
    """
    Advanced visual extractor with stealth capabilities and improved detection algorithms.
    
    Key improvements:
    - Integrated stealth browser for anti-bot evasion
    - Enhanced visual pattern recognition
    - Better handling of dynamic content
    - Improved element mapping accuracy
    """
    
    def __init__(self, config, ai_service_factory=None, stealth_level: str = "enhanced"):
        """
        Initialize the visual extractor.
        
        Args:
            config: Configuration object
            ai_service_factory: Optional AI service factory
            stealth_level: Stealth level - "none", "basic", "enhanced", or "maximum"
        """
        super().__init__(config, ai_service_factory)
        
        self.stealth_level = stealth_level
        
        # Create stealth browser
        profile_map = {
            "none": ProfileType.BOT,
            "basic": ProfileType.HUMAN,
            "enhanced": ProfileType.STEALTH,
            "maximum": ProfileType.STEALTH
        }
        profile = profile_map.get(stealth_level, ProfileType.STEALTH)
        self.stealth = create_stealth_browser(profile)
        
        # Enhanced visual detection parameters
        self.min_element_size = 10  # Minimum size in pixels
        self.contrast_threshold = 25  # Lowered for better detection
        self.edge_threshold = 80  # More sensitive edge detection
        self.color_variance_threshold = 15  # For detecting subtle boundaries
        
        # Advanced UI element patterns
        self.button_patterns = {
            'rounded_corners': True,
            'solid_background': True,
            'text_centered': True,
            'min_padding': 8,
            'shadow_detection': True,
            'gradient_detection': True,
            'hover_state_detection': True
        }
        
        self.input_patterns = {
            'rectangular': True,
            'border': True,
            'min_height': 25,  # Lowered for smaller inputs
            'aspect_ratio_range': (2, 25),  # Wider range
            'placeholder_detection': True,
            'focus_state_detection': True
        }
        
        self.link_patterns = {
            'text_decoration': ['underline', 'none'],
            'color_difference': True,
            'cursor_change': True,
            'inline_element': True
        }
        
        # Visual similarity thresholds
        self.visual_similarity_threshold = 0.85
        self.shape_similarity_threshold = 0.80
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements using advanced visual detection with stealth"""
        candidates = []
        
        try:
            # Apply stealth techniques if needed
            if self.stealth_level != "none":
                await self.stealth.apply_stealth(context.page, self.stealth_level)
                
                # Handle cookie consent with stealth
                await self.stealth.handle_cookie_consent(context.page)
                
                # Wait for page stability
                await self._wait_for_visual_stability(context.page)
            
            # Take multiple screenshots for better detection
            screenshots = await self._capture_multi_state_screenshots(context)
            if not screenshots:
                return candidates
            
            # Detect visual regions across all states
            all_regions = []
            for state_name, screenshot in screenshots.items():
                regions = await self._detect_visual_regions(screenshot, context, state_name)
                all_regions.extend(regions)
            
            # Deduplicate and merge regions
            merged_regions = self._merge_similar_regions(all_regions)
            
            # Map visual regions to DOM elements with improved accuracy
            for region in merged_regions:
                element = await self._map_region_to_element_enhanced(region, context)
                if element:
                    candidate = await self._create_visual_candidate(element, region)
                    if candidate:
                        candidates.append(candidate)
            
            # Apply visual validation
            validated_candidates = await self._validate_visual_candidates(candidates, context)
            
            logger.info(f"Visual Extractor: Found {len(validated_candidates)} validated candidates")
            return validated_candidates
            
        except Exception as e:
            logger.error(f"Visual extraction failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Visual detection with stealth provides higher confidence"""
        return 0.3 if self.stealth_level != "none" else 0.2
    
    async def _wait_for_visual_stability(self, page: Page) -> None:
        """Wait for visual stability with human-like delays"""
        try:
            # Initial wait
            await self.stealth.human_like_delay(500, 1500, "stability")
            
            # Check for visual changes
            prev_screenshot = await page.screenshot()
            stable_count = 0
            max_checks = 5
            
            for _ in range(max_checks):
                await self.stealth.human_like_delay(300, 600)
                curr_screenshot = await page.screenshot()
                
                if self._screenshots_similar(prev_screenshot, curr_screenshot):
                    stable_count += 1
                    if stable_count >= 2:
                        break
                else:
                    stable_count = 0
                
                prev_screenshot = curr_screenshot
                
        except Exception as e:
            logger.debug(f"Visual stability check error: {e}")
    
    def _screenshots_similar(self, screenshot1: bytes, screenshot2: bytes) -> bool:
        """Check if two screenshots are visually similar"""
        try:
            img1 = Image.open(io.BytesIO(screenshot1))
            img2 = Image.open(io.BytesIO(screenshot2))
            
            # Resize to small size for quick comparison
            size = (100, 100)
            img1_small = img1.resize(size, Image.Resampling.LANCZOS)
            img2_small = img2.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to arrays
            arr1 = np.array(img1_small)
            arr2 = np.array(img2_small)
            
            # Calculate difference
            diff = np.mean(np.abs(arr1.astype(float) - arr2.astype(float)))
            
            return diff < 5.0  # Threshold for similarity
            
        except:
            return True  # Assume similar on error
    
    async def _capture_multi_state_screenshots(
        self, 
        context: ExtractionContext
    ) -> Dict[str, np.ndarray]:
        """Capture screenshots in multiple states for better detection"""
        screenshots = {}
        
        try:
            # Normal state
            normal_screenshot = await self._capture_screenshot(context)
            if normal_screenshot is not None:
                screenshots['normal'] = normal_screenshot
            
            # Simulate hover states for better detection
            if self.stealth_level != "none":
                # Move mouse to different areas
                viewport = context.viewport_size
                positions = [
                    (viewport['width'] // 2, viewport['height'] // 3),
                    (viewport['width'] // 3, viewport['height'] // 2),
                    (viewport['width'] * 2 // 3, viewport['height'] // 2)
                ]
                
                for i, (x, y) in enumerate(positions):
                    await self.stealth.human_like_mouse_move(
                        context.page, x, y
                    )
                    await self.stealth.human_like_delay(100, 200)
                    
                    hover_screenshot = await self._capture_screenshot(context)
                    if hover_screenshot is not None:
                        screenshots[f'hover_{i}'] = hover_screenshot
            
            return screenshots
            
        except Exception as e:
            logger.error(f"Multi-state screenshot capture failed: {e}")
            return screenshots
    
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
        context: ExtractionContext,
        state_name: str = "normal"
    ) -> List[Dict[str, Any]]:
        """Detect visual regions with advanced algorithms"""
        regions = []
        
        try:
            # Convert to grayscale
            gray = self._convert_to_grayscale(screenshot)
            
            # Apply multiple detection methods
            edge_regions = await self._detect_edge_based_regions(gray, screenshot)
            color_regions = await self._detect_color_based_regions(screenshot)
            pattern_regions = await self._detect_pattern_based_regions(screenshot, gray)
            
            # Combine all regions
            all_regions = edge_regions + color_regions + pattern_regions
            
            # Filter and rank regions
            for region in all_regions:
                region['state'] = state_name
                if self._is_likely_interactive_enhanced(region, screenshot):
                    regions.append(region)
            
            # Sort by likelihood score
            regions.sort(key=lambda r: r.get('likelihood_score', 0), reverse=True)
            
            return regions[:150]  # Increased limit
            
        except Exception as e:
            logger.error(f"Visual region detection failed: {e}")
            return []
    
    async def _detect_edge_based_regions(
        self,
        gray: np.ndarray,
        original: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect regions using enhanced edge detection"""
        regions = []
        
        try:
            # Apply adaptive edge detection
            edges = self._adaptive_edge_detection(gray)
            
            # Find contours
            contours = self._find_contours_advanced(edges)
            
            # Analyze each contour
            for contour in contours:
                region = self._analyze_contour_enhanced(contour, original, gray)
                if region:
                    region['detection_method'] = 'edge'
                    regions.append(region)
            
            return regions
            
        except Exception as e:
            logger.debug(f"Edge detection failed: {e}")
            return []
    
    async def _detect_color_based_regions(
        self,
        screenshot: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect regions based on color clustering"""
        regions = []
        
        try:
            # Detect regions with distinct colors
            height, width = screenshot.shape[:2]
            
            # Sample colors at grid points
            grid_size = 20
            for y in range(0, height - grid_size, grid_size):
                for x in range(0, width - grid_size, grid_size):
                    region = self._analyze_color_region(screenshot, x, y, grid_size)
                    if region:
                        region['detection_method'] = 'color'
                        regions.append(region)
            
            return regions
            
        except Exception as e:
            logger.debug(f"Color detection failed: {e}")
            return []
    
    async def _detect_pattern_based_regions(
        self,
        screenshot: np.ndarray,
        gray: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect regions based on visual patterns"""
        regions = []
        
        try:
            # Detect button-like patterns
            button_regions = self._detect_button_patterns(screenshot, gray)
            regions.extend(button_regions)
            
            # Detect input-like patterns
            input_regions = self._detect_input_patterns(screenshot, gray)
            regions.extend(input_regions)
            
            # Detect link-like patterns
            link_regions = self._detect_link_patterns(screenshot, gray)
            regions.extend(link_regions)
            
            for region in regions:
                region['detection_method'] = 'pattern'
            
            return regions
            
        except Exception as e:
            logger.debug(f"Pattern detection failed: {e}")
            return []
    
    def _adaptive_edge_detection(self, gray: np.ndarray) -> np.ndarray:
        """Adaptive edge detection with multiple thresholds"""
        height, width = gray.shape
        edges = np.zeros_like(gray)
        
        # Calculate local variance for adaptive thresholding
        window_size = 5
        half_window = window_size // 2
        
        for y in range(half_window, height - half_window):
            for x in range(half_window, width - half_window):
                # Get local window
                window = gray[
                    y - half_window:y + half_window + 1,
                    x - half_window:x + half_window + 1
                ]
                
                # Calculate local variance
                local_var = np.var(window)
                
                # Adaptive threshold based on local variance
                if local_var > self.color_variance_threshold:
                    # Calculate gradients
                    gx = int(gray[y, min(x + 1, width - 1)]) - int(gray[y, max(x - 1, 0)])
                    gy = int(gray[min(y + 1, height - 1), x]) - int(gray[max(y - 1, 0), x])
                    
                    gradient = np.sqrt(gx * gx + gy * gy)
                    
                    # Adaptive threshold
                    local_threshold = self.edge_threshold * (1 + local_var / 100)
                    if gradient > local_threshold:
                        edges[y, x] = min(int(gradient), 255)
        
        return edges
    
    def _find_contours_advanced(self, edges: np.ndarray) -> List[Dict[str, Any]]:
        """Advanced contour finding with connected component analysis"""
        contours = []
        height, width = edges.shape
        visited = np.zeros_like(edges, dtype=bool)
        
        # Use different connectivity patterns
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if edges[y, x] > 0 and not visited[y, x]:
                    # Trace contour with 8-connectivity
                    contour = self._trace_contour_8connected(edges, visited, x, y)
                    
                    # Validate contour
                    if self._validate_contour(contour):
                        contours.append(contour)
        
        return contours
    
    def _trace_contour_8connected(
        self,
        edges: np.ndarray,
        visited: np.ndarray,
        start_x: int,
        start_y: int
    ) -> Dict[str, Any]:
        """Trace contour with 8-connectivity"""
        height, width = edges.shape
        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y
        pixel_count = 0
        edge_pixels = []
        
        # 8-connected neighbors
        neighbors = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),           (1, 0),
            (-1, 1),  (0, 1),  (1, 1)
        ]
        
        stack = [(start_x, start_y)]
        
        while stack and len(stack) < 10000:  # Prevent infinite loops
            x, y = stack.pop()
            
            if visited[y, x]:
                continue
                
            visited[y, x] = True
            pixel_count += 1
            edge_pixels.append((x, y))
            
            # Update bounds
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            
            # Check neighbors
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if (0 <= nx < width and 0 <= ny < height and 
                    edges[ny, nx] > 0 and not visited[ny, nx]):
                    stack.append((nx, ny))
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x + 1,
            'height': max_y - min_y + 1,
            'area': pixel_count,
            'edge_pixels': edge_pixels[:1000],  # Limit for memory
            'density': pixel_count / ((max_x - min_x + 1) * (max_y - min_y + 1))
        }
    
    def _validate_contour(self, contour: Dict[str, Any]) -> bool:
        """Validate if contour represents a valid UI element"""
        # Check minimum size
        if (contour['width'] < self.min_element_size or 
            contour['height'] < self.min_element_size):
            return False
        
        # Check aspect ratio (filter out lines)
        aspect_ratio = contour['width'] / max(contour['height'], 1)
        if aspect_ratio > 50 or aspect_ratio < 0.02:
            return False
        
        # Check density (filter out sparse contours)
        if contour['density'] < 0.1:
            return False
        
        return True
    
    def _analyze_contour_enhanced(
        self,
        contour: Dict[str, Any],
        original: np.ndarray,
        gray: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """Enhanced contour analysis with pattern recognition"""
        try:
            x, y = contour['x'], contour['y']
            w, h = contour['width'], contour['height']
            
            # Extract region
            region = original[y:y+h, x:x+w]
            gray_region = gray[y:y+h, x:x+w]
            
            # Analyze visual properties
            properties = {
                'mean_color': np.mean(region, axis=(0, 1)),
                'color_variance': np.var(region),
                'has_text': self._detect_text_presence(gray_region),
                'is_uniform': self._is_uniform_region(region),
                'has_border': self._detect_border(gray_region),
                'corner_radius': self._estimate_corner_radius(gray_region)
            }
            
            # Calculate likelihood score
            likelihood_score = self._calculate_element_likelihood(properties, w, h)
            
            return {
                **contour,
                'properties': properties,
                'likelihood_score': likelihood_score
            }
            
        except Exception:
            return None
    
    def _detect_text_presence(self, gray_region: np.ndarray) -> bool:
        """Detect if region likely contains text"""
        try:
            # Check for horizontal line patterns (text lines)
            height, width = gray_region.shape
            if height < 10 or width < 10:
                return False
            
            # Calculate horizontal variance
            horizontal_vars = [np.var(gray_region[y, :]) for y in range(height)]
            
            # Text regions have alternating high/low variance
            variance_changes = 0
            for i in range(1, len(horizontal_vars)):
                if abs(horizontal_vars[i] - horizontal_vars[i-1]) > 20:
                    variance_changes += 1
            
            return variance_changes > height * 0.3
            
        except:
            return False
    
    def _is_uniform_region(self, region: np.ndarray) -> bool:
        """Check if region has uniform color (like a button)"""
        try:
            color_var = np.var(region.reshape(-1, region.shape[-1]), axis=0)
            return np.all(color_var < 500)  # Low variance indicates uniform color
        except:
            return False
    
    def _detect_border(self, gray_region: np.ndarray) -> bool:
        """Detect if region has a border"""
        try:
            height, width = gray_region.shape
            if height < 5 or width < 5:
                return False
            
            # Check edges
            edge_mean = np.mean([
                gray_region[0, :].mean(),  # Top
                gray_region[-1, :].mean(),  # Bottom
                gray_region[:, 0].mean(),  # Left
                gray_region[:, -1].mean()  # Right
            ])
            
            # Check interior
            interior_mean = gray_region[2:-2, 2:-2].mean()
            
            # Border exists if edge is significantly different from interior
            return abs(edge_mean - interior_mean) > 30
            
        except:
            return False
    
    def _estimate_corner_radius(self, gray_region: np.ndarray) -> float:
        """Estimate corner radius (0 = sharp, 1 = very rounded)"""
        try:
            height, width = gray_region.shape
            if height < 10 or width < 10:
                return 0.0
            
            # Check corners
            corner_size = min(10, height // 4, width // 4)
            corners = [
                gray_region[:corner_size, :corner_size],  # Top-left
                gray_region[:corner_size, -corner_size:],  # Top-right
                gray_region[-corner_size:, :corner_size],  # Bottom-left
                gray_region[-corner_size:, -corner_size:]  # Bottom-right
            ]
            
            # Rounded corners have gradual transitions
            roundness_scores = []
            for corner in corners:
                gradient = np.gradient(corner.astype(float))
                roundness = 1.0 - (np.std(gradient) / 128.0)  # Normalize
                roundness_scores.append(max(0, min(1, roundness)))
            
            return np.mean(roundness_scores)
            
        except:
            return 0.0
    
    def _calculate_element_likelihood(
        self,
        properties: Dict[str, Any],
        width: int,
        height: int
    ) -> float:
        """Calculate likelihood that region is an interactive element"""
        score = 0.5  # Base score
        
        # Size factors
        if 30 <= width <= 500 and 20 <= height <= 100:
            score += 0.2  # Good button/input size
        elif width > 500 or height > 200:
            score -= 0.1  # Too large
        
        # Visual properties
        if properties.get('has_text'):
            score += 0.15
        
        if properties.get('is_uniform'):
            score += 0.1  # Buttons often have uniform background
        
        if properties.get('has_border'):
            score += 0.1  # Inputs and buttons often have borders
        
        if properties.get('corner_radius', 0) > 0.3:
            score += 0.05  # Modern buttons have rounded corners
        
        return max(0, min(1, score))
    
    def _analyze_color_region(
        self,
        screenshot: np.ndarray,
        x: int,
        y: int,
        size: int
    ) -> Optional[Dict[str, Any]]:
        """Analyze a color-based region"""
        try:
            region = screenshot[y:y+size, x:x+size]
            
            # Check if region has distinct color
            mean_color = np.mean(region, axis=(0, 1))
            
            # Compare with surrounding areas
            surrounding_colors = []
            for dx, dy in [(-size, 0), (size, 0), (0, -size), (0, size)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < screenshot.shape[1] - size and 0 <= ny < screenshot.shape[0] - size:
                    surrounding = screenshot[ny:ny+size, nx:nx+size]
                    surrounding_colors.append(np.mean(surrounding, axis=(0, 1)))
            
            if not surrounding_colors:
                return None
            
            # Calculate color difference
            avg_diff = np.mean([
                np.linalg.norm(mean_color - sc) 
                for sc in surrounding_colors
            ])
            
            if avg_diff > 30:  # Significant color difference
                return {
                    'x': x,
                    'y': y,
                    'width': size,
                    'height': size,
                    'mean_color': mean_color,
                    'color_difference': avg_diff,
                    'likelihood_score': min(1.0, avg_diff / 100)
                }
            
            return None
            
        except:
            return None
    
    def _detect_button_patterns(
        self,
        screenshot: np.ndarray,
        gray: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect button-like visual patterns"""
        regions = []
        height, width = gray.shape
        
        # Scan for button-like regions
        for y in range(0, height - 30, 10):
            for x in range(0, width - 50, 10):
                if self._is_button_like(screenshot, gray, x, y):
                    # Find exact bounds
                    bounds = self._find_element_bounds(gray, x + 25, y + 15)
                    if bounds:
                        regions.append({
                            **bounds,
                            'element_type': 'button',
                            'likelihood_score': 0.8
                        })
        
        return regions
    
    def _is_button_like(
        self,
        screenshot: np.ndarray,
        gray: np.ndarray,
        x: int,
        y: int
    ) -> bool:
        """Check if region looks like a button"""
        try:
            # Check minimum size
            region = screenshot[y:y+30, x:x+50]
            gray_region = gray[y:y+30, x:x+50]
            
            # Buttons typically have:
            # 1. Uniform or gradient background
            # 2. Centered text
            # 3. Rounded corners or defined edges
            # 4. Adequate padding
            
            # Check color uniformity
            color_std = np.std(region.reshape(-1, 3), axis=0)
            is_uniform = np.all(color_std < 40)
            
            # Check for text presence in center
            center_region = gray_region[10:20, 15:35]
            has_center_content = np.std(center_region) > 20
            
            # Check edges
            has_defined_edges = (
                np.std(gray_region[0, :]) < 20 and  # Top edge
                np.std(gray_region[-1, :]) < 20  # Bottom edge
            )
            
            return is_uniform and has_center_content and has_defined_edges
            
        except:
            return False
    
    def _detect_input_patterns(
        self,
        screenshot: np.ndarray,
        gray: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect input field patterns"""
        regions = []
        height, width = gray.shape
        
        # Scan for input-like regions
        for y in range(0, height - 35, 15):
            for x in range(0, width - 100, 20):
                if self._is_input_like(screenshot, gray, x, y):
                    bounds = self._find_element_bounds(gray, x + 50, y + 17)
                    if bounds:
                        regions.append({
                            **bounds,
                            'element_type': 'input',
                            'likelihood_score': 0.75
                        })
        
        return regions
    
    def _is_input_like(
        self,
        screenshot: np.ndarray,
        gray: np.ndarray,
        x: int,
        y: int
    ) -> bool:
        """Check if region looks like an input field"""
        try:
            region = screenshot[y:y+35, x:x+100]
            gray_region = gray[y:y+35, x:x+100]
            
            # Input fields typically have:
            # 1. Light background
            # 2. Defined border
            # 3. Horizontal shape
            # 4. Left-aligned content or placeholder
            
            # Check background brightness
            mean_brightness = np.mean(gray_region)
            is_light = mean_brightness > 200
            
            # Check for border
            has_border = self._detect_border(gray_region)
            
            # Check aspect ratio
            aspect_ratio = 100 / 35  # width / height
            is_horizontal = 2 < aspect_ratio < 10
            
            return is_light and has_border and is_horizontal
            
        except:
            return False
    
    def _detect_link_patterns(
        self,
        screenshot: np.ndarray,
        gray: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect link-like patterns"""
        regions = []
        
        # Links are harder to detect visually, focus on color differences
        # This is a simplified approach
        return regions
    
    def _find_element_bounds(
        self,
        gray: np.ndarray,
        seed_x: int,
        seed_y: int
    ) -> Optional[Dict[str, Any]]:
        """Find exact element bounds from seed point"""
        try:
            height, width = gray.shape
            
            # Flood fill to find connected region
            visited = np.zeros_like(gray, dtype=bool)
            min_x, max_x = seed_x, seed_x
            min_y, max_y = seed_y, seed_y
            
            # Get reference color
            ref_color = gray[seed_y, seed_x]
            tolerance = 30
            
            stack = [(seed_x, seed_y)]
            pixels = 0
            
            while stack and pixels < 10000:
                x, y = stack.pop()
                
                if visited[y, x]:
                    continue
                    
                if abs(int(gray[y, x]) - int(ref_color)) > tolerance:
                    continue
                    
                visited[y, x] = True
                pixels += 1
                
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
                
                # Add neighbors
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        stack.append((nx, ny))
            
            if pixels > 100:  # Minimum size
                return {
                    'x': min_x,
                    'y': min_y,
                    'width': max_x - min_x + 1,
                    'height': max_y - min_y + 1,
                    'area': pixels
                }
            
            return None
            
        except:
            return None
    
    def _merge_similar_regions(
        self,
        regions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge overlapping or similar regions"""
        if not regions:
            return []
        
        merged = []
        used = set()
        
        for i, region1 in enumerate(regions):
            if i in used:
                continue
                
            # Start with current region
            merged_region = region1.copy()
            group = [region1]
            
            # Find similar regions
            for j, region2 in enumerate(regions[i+1:], i+1):
                if j in used:
                    continue
                    
                if self._regions_overlap(region1, region2):
                    group.append(region2)
                    used.add(j)
            
            # Merge the group
            if len(group) > 1:
                merged_region = self._merge_region_group(group)
            
            merged.append(merged_region)
        
        return merged
    
    def _regions_overlap(self, r1: Dict[str, Any], r2: Dict[str, Any]) -> bool:
        """Check if two regions overlap significantly"""
        x1, y1, w1, h1 = r1['x'], r1['y'], r1['width'], r1['height']
        x2, y2, w2, h2 = r2['x'], r2['y'], r2['width'], r2['height']
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        
        intersection = x_overlap * y_overlap
        area1 = w1 * h1
        area2 = w2 * h2
        
        # Check IoU (Intersection over Union)
        union = area1 + area2 - intersection
        iou = intersection / union if union > 0 else 0
        
        return iou > 0.5
    
    def _merge_region_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge a group of regions into one"""
        min_x = min(r['x'] for r in group)
        min_y = min(r['y'] for r in group)
        max_x = max(r['x'] + r['width'] for r in group)
        max_y = max(r['y'] + r['height'] for r in group)
        
        # Average likelihood scores
        avg_likelihood = np.mean([r.get('likelihood_score', 0.5) for r in group])
        
        # Combine detection methods
        methods = set()
        for r in group:
            if 'detection_method' in r:
                methods.add(r['detection_method'])
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y,
            'likelihood_score': avg_likelihood,
            'detection_methods': list(methods),
            'merged_count': len(group)
        }
    
    def _is_likely_interactive_enhanced(
        self,
        region: Dict[str, Any],
        screenshot: np.ndarray
    ) -> bool:
        """Enhanced check for interactive elements"""
        # Use likelihood score if available
        if region.get('likelihood_score', 0) < 0.3:
            return False
        
        # Check size constraints
        w, h = region['width'], region['height']
        if w < self.min_element_size or h < self.min_element_size:
            return False
        
        # Maximum size constraints
        if w > screenshot.shape[1] * 0.8 or h > screenshot.shape[0] * 0.8:
            return False
        
        # Check aspect ratio
        aspect_ratio = w / max(h, 1)
        if aspect_ratio > 50 or aspect_ratio < 0.05:
            return False
        
        return True
    
    async def _map_region_to_element_enhanced(
        self,
        region: Dict[str, Any],
        context: ExtractionContext
    ) -> Optional[ElementHandle]:
        """Map visual region to DOM element with improved accuracy"""
        try:
            x = region['x'] + region['width'] // 2
            y = region['y'] + region['height'] // 2
            
            # Try multiple strategies to find element
            element = None
            
            # Strategy 1: Direct point query
            element = await context.page.query_selector(f'[data-visual-coords="{x},{y}"]')
            
            if not element:
                # Strategy 2: Element at point
                element = await context.page.evaluate(f'''
                    (x, y) => {{
                        const elem = document.elementFromPoint({x}, {y});
                        if (elem && elem.tagName !== 'HTML' && elem.tagName !== 'BODY') {{
                            // Mark element for later retrieval
                            elem.setAttribute('data-visual-match', 'true');
                            return true;
                        }}
                        return false;
                    }}
                ''', x, y)
                
                if element:
                    element = await context.page.query_selector('[data-visual-match="true"]')
                    if element:
                        await context.page.evaluate('''
                            elem => elem.removeAttribute('data-visual-match')
                        ''', element)
            
            if not element:
                # Strategy 3: Area search
                elements = await context.page.query_selector_all('*')
                for elem in elements[:1000]:  # Limit search
                    try:
                        box = await elem.bounding_box()
                        if box and self._box_matches_region(box, region):
                            element = elem
                            break
                    except:
                        continue
            
            return element
            
        except Exception as e:
            logger.debug(f"Element mapping failed: {e}")
            return None
    
    def _box_matches_region(
        self,
        box: Dict[str, float],
        region: Dict[str, Any]
    ) -> bool:
        """Check if bounding box matches visual region"""
        # Allow some tolerance
        tolerance = 5
        
        return (
            abs(box['x'] - region['x']) < tolerance and
            abs(box['y'] - region['y']) < tolerance and
            abs(box['width'] - region['width']) < tolerance and
            abs(box['height'] - region['height']) < tolerance
        )
    
    async def _create_visual_candidate(
        self,
        element: ElementHandle,
        region: Dict[str, Any]
    ) -> Optional[ElementCandidate]:
        """Create element candidate with visual metadata"""
        try:
            # Get element properties
            properties = await element.evaluate('''
                elem => ({
                    tagName: elem.tagName.toLowerCase(),
                    type: elem.type || '',
                    role: elem.getAttribute('role') || '',
                    hasOnClick: !!elem.onclick,
                    isContentEditable: elem.isContentEditable,
                    computedStyle: {
                        cursor: window.getComputedStyle(elem).cursor,
                        pointerEvents: window.getComputedStyle(elem).pointerEvents
                    }
                })
            ''')
            
            # Determine if interactive
            is_interactive = (
                properties['tagName'] in ['a', 'button', 'input', 'select', 'textarea'] or
                properties['role'] in ['button', 'link', 'textbox', 'combobox'] or
                properties['hasOnClick'] or
                properties['isContentEditable'] or
                properties['computedStyle']['cursor'] == 'pointer'
            )
            
            if not is_interactive:
                return None
            
            # Generate selectors
            selectors = await self._generate_selectors(element, properties)
            
            # Calculate confidence
            confidence = self._calculate_visual_confidence(region, properties)
            
            return ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.VISUAL_DETECTION},
                attributes={},
                selectors=selectors,
                metadata={
                    'visual_region': region,
                    'detection_methods': region.get('detection_methods', ['unknown']),
                    'element_type': region.get('element_type', properties['tagName']),
                    'visual_confidence': region.get('likelihood_score', 0.5)
                }
            )
            
        except Exception as e:
            logger.debug(f"Candidate creation failed: {e}")
            return None
    
    def _calculate_visual_confidence(
        self,
        region: Dict[str, Any],
        properties: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for visual detection"""
        base_confidence = 0.6
        
        # Visual likelihood
        base_confidence += region.get('likelihood_score', 0.5) * 0.2
        
        # Element type boost
        if properties['tagName'] in ['button', 'a', 'input']:
            base_confidence += 0.1
        
        # Role boost
        if properties.get('role') in ['button', 'link']:
            base_confidence += 0.05
        
        # Interactive properties
        if properties.get('hasOnClick') or properties['computedStyle']['cursor'] == 'pointer':
            base_confidence += 0.05
        
        return min(0.95, base_confidence)
    
    async def _generate_selectors(
        self,
        element: ElementHandle,
        properties: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors for element"""
        selectors = []
        
        try:
            # Get element info
            info = await element.evaluate('''
                elem => ({
                    id: elem.id,
                    className: elem.className,
                    tagName: elem.tagName.toLowerCase(),
                    textContent: elem.textContent?.trim().substring(0, 50),
                    ariaLabel: elem.getAttribute('aria-label')
                })
            ''')
            
            # ID selector
            if info['id']:
                selectors.append({
                    'type': 'css',
                    'value': f'#{info["id"]}',
                    'specificity': 1.0
                })
            
            # Class selector
            if info['className']:
                classes = info['className'].split()[:3]  # Limit classes
                if classes:
                    selector = '.' + '.'.join(classes)
                    selectors.append({
                        'type': 'css',
                        'value': f'{info["tagName"]}{selector}',
                        'specificity': 0.8
                    })
            
            # Text selector
            if info['textContent']:
                selectors.append({
                    'type': 'text',
                    'value': info['textContent'],
                    'specificity': 0.7
                })
            
            # Aria label
            if info['ariaLabel']:
                selectors.append({
                    'type': 'css',
                    'value': f'[aria-label="{info["ariaLabel"]}"]',
                    'specificity': 0.9
                })
            
            return selectors
            
        except:
            return []
    
    async def _validate_visual_candidates(
        self,
        candidates: List[ElementCandidate],
        context: ExtractionContext
    ) -> List[ElementCandidate]:
        """Validate and filter visual candidates"""
        validated = []
        
        for candidate in candidates:
            try:
                # Verify element is still valid
                is_visible = await candidate.element.is_visible()
                is_enabled = await candidate.element.is_enabled()
                
                if is_visible and is_enabled:
                    validated.append(candidate)
                    
            except:
                # Element no longer valid
                continue
        
        return validated
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            # RGB to grayscale conversion
            return np.dot(image[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        return image