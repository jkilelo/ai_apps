"""
Unified Visual Strategy - Consolidates visual detection from visual_strategy.py and visual_extractor.py.
Combines OCR, edge detection, pattern recognition, and visual element analysis.
"""

import asyncio
import base64
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from PIL import Image
import io

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available. Visual detection features will be limited.")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract OCR not available. Text detection features will be limited.")

from playwright.async_api import Page
from selenium.webdriver.remote.webdriver import WebDriver

from ..extraction_utils import (
    ElementType, InteractionType, ElementTypeDetector,
    ConfidenceCalculator, ElementValidator
)

logger = logging.getLogger(__name__)


@dataclass
class VisualExtractionConfig:
    """Configuration for visual extraction"""
    enable_ocr: bool = True
    enable_edge_detection: bool = True
    enable_pattern_matching: bool = True
    enable_color_analysis: bool = True
    enable_layout_analysis: bool = True
    ocr_confidence_threshold: float = 0.7
    edge_threshold_low: int = 50
    edge_threshold_high: int = 150
    pattern_match_threshold: float = 0.8
    min_element_area: int = 100
    max_elements: int = 500


class UnifiedVisualStrategy:
    """
    Unified visual extraction strategy combining OCR, edge detection, and pattern recognition.
    Consolidates functionality from visual_strategy.py and visual_extractor.py.
    """
    
    def __init__(self, config: Optional[VisualExtractionConfig] = None):
        self.config = config or VisualExtractionConfig()
        self.type_detector = ElementTypeDetector()
        self.confidence_calculator = ConfidenceCalculator()
        self.validator = ElementValidator()
        self._visual_patterns = self._load_visual_patterns()
        
    def _load_visual_patterns(self) -> Dict[str, Any]:
        """Load visual patterns for element detection"""
        return {
            'button': {
                'min_width': 50,
                'max_width': 400,
                'min_height': 20,
                'max_height': 100,
                'aspect_ratio_range': (1.5, 8.0),
                'common_colors': ['#007bff', '#28a745', '#dc3545', '#ffc107'],
                'text_patterns': ['submit', 'click', 'continue', 'next', 'save', 'cancel']
            },
            'input': {
                'min_width': 100,
                'max_width': 600,
                'min_height': 20,
                'max_height': 60,
                'aspect_ratio_range': (3.0, 20.0),
                'border_required': True,
                'background_colors': ['#ffffff', '#f8f9fa', '#e9ecef']
            },
            'link': {
                'text_color_patterns': ['#0000ff', '#0066cc', '#1a73e8'],
                'underline_detection': True,
                'cursor_change': 'pointer'
            },
            'image': {
                'min_width': 20,
                'min_height': 20,
                'high_color_variance': True,
                'aspect_ratio_range': (0.5, 3.0)
            }
        }
    
    async def extract_playwright(self, page: Page) -> List[Dict[str, Any]]:
        """Extract visual elements using Playwright"""
        try:
            # Take screenshot
            screenshot_bytes = await page.screenshot(full_page=True)
            
            # Get viewport and page dimensions
            viewport = await page.viewport_size()
            dimensions = await page.evaluate("() => ({ width: document.body.scrollWidth, height: document.body.scrollHeight })")
            
            # Process screenshot
            elements = self._process_screenshot(
                screenshot_bytes,
                dimensions['width'],
                dimensions['height']
            )
            
            # Map visual elements to DOM if possible
            mapped_elements = await self._map_to_dom_playwright(page, elements)
            
            return mapped_elements[:self.config.max_elements]
            
        except Exception as e:
            logger.error(f"Error in Playwright visual extraction: {e}")
            return []
    
    def extract_selenium(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Extract visual elements using Selenium"""
        try:
            # Take screenshot
            screenshot_base64 = driver.get_screenshot_as_base64()
            screenshot_bytes = base64.b64decode(screenshot_base64)
            
            # Get page dimensions
            dimensions = driver.execute_script(
                "return { width: document.body.scrollWidth, height: document.body.scrollHeight }"
            )
            
            # Process screenshot
            elements = self._process_screenshot(
                screenshot_bytes,
                dimensions['width'],
                dimensions['height']
            )
            
            # Map visual elements to DOM if possible
            mapped_elements = self._map_to_dom_selenium(driver, elements)
            
            return mapped_elements[:self.config.max_elements]
            
        except Exception as e:
            logger.error(f"Error in Selenium visual extraction: {e}")
            return []
    
    def _process_screenshot(self, screenshot_bytes: bytes, width: int, height: int) -> List[Dict[str, Any]]:
        """Process screenshot to extract visual elements"""
        elements = []
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Convert to numpy array for OpenCV processing
        if CV2_AVAILABLE:
            img_array = np.array(image)
            
            # Extract elements using different techniques
            if self.config.enable_edge_detection:
                edge_elements = self._detect_edges(img_array)
                elements.extend(edge_elements)
            
            if self.config.enable_pattern_matching:
                pattern_elements = self._detect_patterns(img_array)
                elements.extend(pattern_elements)
            
            if self.config.enable_color_analysis:
                color_elements = self._analyze_colors(img_array)
                elements.extend(color_elements)
            
            if self.config.enable_layout_analysis:
                layout_elements = self._analyze_layout(img_array)
                elements.extend(layout_elements)
        
        # OCR text detection
        if self.config.enable_ocr and TESSERACT_AVAILABLE:
            ocr_elements = self._perform_ocr(image)
            elements.extend(ocr_elements)
        
        # Filter and deduplicate
        filtered_elements = self._filter_visual_elements(elements)
        
        return filtered_elements
    
    def _detect_edges(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Detect elements using edge detection"""
        if not CV2_AVAILABLE:
            return []
        
        elements = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect edges using Canny
        edges = cv2.Canny(
            blurred,
            self.config.edge_threshold_low,
            self.config.edge_threshold_high
        )
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size
            area = w * h
            if area < self.config.min_element_area:
                continue
            
            # Analyze contour properties
            element_type = self._classify_by_shape(w, h, contour)
            
            elements.append({
                'detection_method': 'edge_detection',
                'bounding_box': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                },
                'visual_type': element_type,
                'confidence': self._calculate_edge_confidence(contour, area),
                'contour_area': int(area),
                'aspect_ratio': w / h if h > 0 else 0
            })
        
        return elements
    
    def _detect_patterns(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI patterns like buttons, inputs, etc."""
        if not CV2_AVAILABLE:
            return []
        
        elements = []
        
        # Convert to grayscale for pattern matching
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detect button-like patterns
        button_elements = self._detect_button_patterns(gray, img_array)
        elements.extend(button_elements)
        
        # Detect input field patterns
        input_elements = self._detect_input_patterns(gray, img_array)
        elements.extend(input_elements)
        
        # Detect clickable areas
        clickable_elements = self._detect_clickable_patterns(img_array)
        elements.extend(clickable_elements)
        
        return elements
    
    def _detect_button_patterns(self, gray: np.ndarray, color_img: np.ndarray) -> List[Dict[str, Any]]:
        """Detect button-like visual patterns"""
        elements = []
        
        if not CV2_AVAILABLE:
            return elements
        
        # Look for rectangular regions with consistent background
        # Apply threshold to find regions
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        button_pattern = self._visual_patterns['button']
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check if dimensions match button pattern
            if (button_pattern['min_width'] <= w <= button_pattern['max_width'] and
                button_pattern['min_height'] <= h <= button_pattern['max_height']):
                
                aspect_ratio = w / h if h > 0 else 0
                if button_pattern['aspect_ratio_range'][0] <= aspect_ratio <= button_pattern['aspect_ratio_range'][1]:
                    
                    # Extract region for color analysis
                    region = color_img[y:y+h, x:x+w]
                    
                    # Check if region has button-like characteristics
                    if self._is_button_like(region):
                        elements.append({
                            'detection_method': 'pattern_button',
                            'bounding_box': {
                                'x': int(x),
                                'y': int(y),
                                'width': int(w),
                                'height': int(h)
                            },
                            'visual_type': 'button',
                            'confidence': 0.7,
                            'element_type': ElementType.BUTTON.value
                        })
        
        return elements
    
    def _detect_input_patterns(self, gray: np.ndarray, color_img: np.ndarray) -> List[Dict[str, Any]]:
        """Detect input field visual patterns"""
        elements = []
        
        if not CV2_AVAILABLE:
            return elements
        
        # Look for horizontal lines (input field borders)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            input_pattern = self._visual_patterns['input']
            
            # Group lines into potential input fields
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Check if line is horizontal
                if abs(y2 - y1) < 5:  # Nearly horizontal
                    width = abs(x2 - x1)
                    
                    if input_pattern['min_width'] <= width <= input_pattern['max_width']:
                        # Look for matching bottom line
                        for other_line in lines:
                            ox1, oy1, ox2, oy2 = other_line[0]
                            
                            # Check if this could be the bottom border
                            if (abs(oy1 - y1) > input_pattern['min_height'] and
                                abs(oy1 - y1) < input_pattern['max_height'] and
                                abs(ox1 - x1) < 20):  # Aligned horizontally
                                
                                elements.append({
                                    'detection_method': 'pattern_input',
                                    'bounding_box': {
                                        'x': min(x1, ox1),
                                        'y': min(y1, oy1),
                                        'width': max(x2, ox2) - min(x1, ox1),
                                        'height': abs(oy1 - y1)
                                    },
                                    'visual_type': 'input',
                                    'confidence': 0.6,
                                    'element_type': ElementType.INPUT.value
                                })
                                break
        
        return elements
    
    def _detect_clickable_patterns(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Detect clickable areas based on visual cues"""
        elements = []
        
        if not CV2_AVAILABLE:
            return elements
        
        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Look for link-like colors (blues)
        link_pattern = self._visual_patterns['link']
        
        # Define blue color range in HSV
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        # Create mask for blue regions
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter small regions
            if w * h < 50:
                continue
            
            # Check aspect ratio for link-like text
            if 2 <= w/h <= 20:
                elements.append({
                    'detection_method': 'pattern_link',
                    'bounding_box': {
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h)
                    },
                    'visual_type': 'link',
                    'confidence': 0.5,
                    'element_type': ElementType.LINK.value
                })
        
        return elements
    
    def _analyze_colors(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze color regions to identify UI elements"""
        elements = []
        
        if not CV2_AVAILABLE:
            return elements
        
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Segment by color intensity and saturation
        # High saturation often indicates UI elements
        saturation = hsv[:, :, 1]
        
        # Threshold to find high saturation regions
        _, high_sat = cv2.threshold(saturation, 100, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(high_sat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if area < self.config.min_element_area:
                continue
            
            # Extract dominant color
            region = img_array[y:y+h, x:x+w]
            dominant_color = self._get_dominant_color(region)
            
            elements.append({
                'detection_method': 'color_analysis',
                'bounding_box': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                },
                'dominant_color': dominant_color,
                'visual_type': 'colored_region',
                'confidence': 0.4
            })
        
        return elements
    
    def _analyze_layout(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze page layout to identify structural elements"""
        elements = []
        
        if not CV2_AVAILABLE:
            return elements
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply morphological operations to find text blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        dilated = cv2.dilate(gray, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Classify based on aspect ratio and position
            layout_type = self._classify_layout_element(x, y, w, h, img_array.shape)
            
            if layout_type:
                elements.append({
                    'detection_method': 'layout_analysis',
                    'bounding_box': {
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h)
                    },
                    'visual_type': layout_type,
                    'confidence': 0.5
                })
        
        return elements
    
    def _perform_ocr(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Perform OCR to detect text elements"""
        elements = []
        
        if not TESSERACT_AVAILABLE:
            return elements
        
        try:
            # Perform OCR with bounding boxes
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                # Filter by confidence
                if float(ocr_data['conf'][i]) < self.config.ocr_confidence_threshold * 100:
                    continue
                
                text = ocr_data['text'][i].strip()
                if not text:
                    continue
                
                # Get bounding box
                x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                             ocr_data['width'][i], ocr_data['height'][i])
                
                # Classify text element
                element_type = self._classify_text_element(text)
                
                elements.append({
                    'detection_method': 'ocr',
                    'bounding_box': {
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h
                    },
                    'text': text,
                    'ocr_confidence': float(ocr_data['conf'][i]) / 100,
                    'visual_type': element_type,
                    'confidence': float(ocr_data['conf'][i]) / 100
                })
        
        except Exception as e:
            logger.error(f"OCR error: {e}")
        
        return elements
    
    async def _map_to_dom_playwright(self, page: Page, visual_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map visual elements to DOM elements using Playwright"""
        mapped_elements = []
        
        for v_element in visual_elements:
            bbox = v_element['bounding_box']
            
            # Try to find DOM element at this position
            dom_element = await page.evaluate("""
                (bbox) => {
                    const element = document.elementFromPoint(
                        bbox.x + bbox.width / 2,
                        bbox.y + bbox.height / 2
                    );
                    
                    if (element) {
                        const rect = element.getBoundingClientRect();
                        const attributes = {};
                        for (const attr of element.attributes) {
                            attributes[attr.name] = attr.value;
                        }
                        
                        return {
                            tag_name: element.tagName.toLowerCase(),
                            text: element.textContent?.trim().substring(0, 200),
                            attributes: attributes,
                            dom_bbox: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            }
                        };
                    }
                    return null;
                }
            """, bbox)
            
            if dom_element:
                # Merge visual and DOM data
                merged = {**v_element, **dom_element}
                merged['has_dom_mapping'] = True
                
                # Determine element type using DOM info
                element_type = self.type_detector.determine_element_type(
                    dom_element['tag_name'],
                    dom_element['attributes']
                )
                merged['element_type'] = element_type.value
                
                mapped_elements.append(merged)
            else:
                # Keep visual-only element
                v_element['has_dom_mapping'] = False
                mapped_elements.append(v_element)
        
        return mapped_elements
    
    def _map_to_dom_selenium(self, driver: WebDriver, visual_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map visual elements to DOM elements using Selenium"""
        mapped_elements = []
        
        for v_element in visual_elements:
            bbox = v_element['bounding_box']
            
            # Try to find DOM element at this position
            script = """
                const element = document.elementFromPoint(
                    arguments[0] + arguments[2] / 2,
                    arguments[1] + arguments[3] / 2
                );
                
                if (element) {
                    const rect = element.getBoundingClientRect();
                    const attributes = {};
                    for (const attr of element.attributes) {
                        attributes[attr.name] = attr.value;
                    }
                    
                    return {
                        tag_name: element.tagName.toLowerCase(),
                        text: element.textContent?.trim().substring(0, 200),
                        attributes: attributes
                    };
                }
                return null;
            """
            
            dom_element = driver.execute_script(
                script,
                bbox['x'], bbox['y'], bbox['width'], bbox['height']
            )
            
            if dom_element:
                merged = {**v_element, **dom_element}
                merged['has_dom_mapping'] = True
                mapped_elements.append(merged)
            else:
                v_element['has_dom_mapping'] = False
                mapped_elements.append(v_element)
        
        return mapped_elements
    
    def _classify_by_shape(self, width: int, height: int, contour: np.ndarray) -> str:
        """Classify element type based on shape characteristics"""
        aspect_ratio = width / height if height > 0 else 0
        
        # Button-like shape
        if 1.5 <= aspect_ratio <= 8 and 20 <= height <= 100:
            return 'button'
        
        # Input field shape
        if 3 <= aspect_ratio <= 20 and 20 <= height <= 60:
            return 'input'
        
        # Image-like shape
        if 0.5 <= aspect_ratio <= 2 and width > 50 and height > 50:
            return 'image'
        
        # Text block shape
        if aspect_ratio > 5 and height < 50:
            return 'text'
        
        return 'unknown'
    
    def _calculate_edge_confidence(self, contour: np.ndarray, area: float) -> float:
        """Calculate confidence based on edge detection quality"""
        if not CV2_AVAILABLE:
            return 0.5
        
        # Calculate contour properties
        perimeter = cv2.arcLength(contour, True)
        
        # Circularity measure
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Convexity
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        convexity = area / hull_area if hull_area > 0 else 0
        
        # Combine metrics
        confidence = (circularity * 0.3 + convexity * 0.3 + 0.4)
        
        return min(confidence, 1.0)
    
    def _is_button_like(self, region: np.ndarray) -> bool:
        """Check if a region looks like a button"""
        if not CV2_AVAILABLE:
            return False
        
        # Check color consistency
        mean_color = np.mean(region, axis=(0, 1))
        std_color = np.std(region, axis=(0, 1))
        
        # Buttons typically have consistent background color
        color_consistency = np.mean(std_color) < 50
        
        # Check for rounded corners or borders
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = np.sum(edges > 0) / edges.size
        
        # Buttons have defined edges but not too many
        has_borders = 0.01 < edge_ratio < 0.3
        
        return color_consistency and has_borders
    
    def _get_dominant_color(self, region: np.ndarray) -> str:
        """Get dominant color as hex string"""
        if not CV2_AVAILABLE:
            return "#000000"
        
        # Calculate mean color
        mean_color = np.mean(region, axis=(0, 1)).astype(int)
        
        # Convert to hex
        return "#{:02x}{:02x}{:02x}".format(mean_color[0], mean_color[1], mean_color[2])
    
    def _classify_layout_element(self, x: int, y: int, w: int, h: int, img_shape: Tuple) -> Optional[str]:
        """Classify layout element based on position and size"""
        img_height, img_width = img_shape[:2]
        
        # Header detection
        if y < img_height * 0.15 and w > img_width * 0.8:
            return 'header'
        
        # Footer detection
        if y > img_height * 0.85 and w > img_width * 0.8:
            return 'footer'
        
        # Sidebar detection
        if w < img_width * 0.3 and h > img_height * 0.5:
            if x < img_width * 0.2:
                return 'left_sidebar'
            elif x > img_width * 0.7:
                return 'right_sidebar'
        
        # Main content area
        if w > img_width * 0.4 and h > img_height * 0.3:
            return 'main_content'
        
        return None
    
    def _classify_text_element(self, text: str) -> str:
        """Classify text element based on content"""
        text_lower = text.lower()
        
        # Button text patterns
        button_keywords = ['submit', 'click', 'continue', 'next', 'save', 'cancel', 'ok', 'apply']
        if any(keyword in text_lower for keyword in button_keywords):
            return 'button'
        
        # Link patterns
        if text_lower.startswith('http') or 'www.' in text_lower:
            return 'link'
        
        # Label patterns
        if text_lower.endswith(':') or len(text) < 20:
            return 'label'
        
        # Heading patterns
        if text.isupper() or (len(text) < 50 and text[0].isupper()):
            return 'heading'
        
        return 'text'
    
    def _filter_visual_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and deduplicate visual elements"""
        filtered = []
        seen_regions = set()
        
        for element in elements:
            bbox = element['bounding_box']
            
            # Create region signature
            region_sig = (
                bbox['x'] // 10,
                bbox['y'] // 10,
                bbox['width'] // 10,
                bbox['height'] // 10
            )
            
            # Skip if we've seen a similar region
            if region_sig in seen_regions:
                continue
            
            seen_regions.add(region_sig)
            
            # Skip very small elements
            if bbox['width'] * bbox['height'] < self.config.min_element_area:
                continue
            
            filtered.append(element)
        
        # Sort by confidence if available
        filtered.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return filtered