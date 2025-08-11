"""
AI Service implementations for UI Testing v2
"""

import asyncio
import base64
import json
import logging
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

try:
    import anthropic
    from anthropic import AsyncAnthropic
except ImportError:
    anthropic = None
    AsyncAnthropic = None

import cv2
import numpy as np
from PIL import Image

from ..core.interfaces import AIServiceInterface
from ..core.exceptions import AIServiceError, ConfigurationError
from ..core.logging import get_logger
from ..models.common import ElementData, TestCase

# Import prompt management
from .prompt_manager import PromptManager, ContextManager, PromptType, PromptTemplate, get_prompt_manager
from .reasoning import ReasoningEngine, ReasoningResult, ReasoningType

logger = get_logger("ai_service")


class BaseAIService(AIServiceInterface):
    """Base AI service implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model", "")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.7)
        self.timeout = config.get("timeout", 60)
        self._client = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the AI service"""
        if self._initialized:
            return
        
        try:
            await self._create_client()
            self._initialized = True
            logger.info(f"AI service initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise AIServiceError(f"AI service initialization failed: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup AI service resources"""
        if self._client and hasattr(self._client, 'close'):
            await self._client.close()
        self._initialized = False
        logger.info("AI service cleaned up")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health"""
        try:
            if not self._initialized:
                return {"status": "unhealthy", "error": "Not initialized"}
            
            # Simple test generation
            test_prompt = "Generate a simple test case title for a login button."
            response = await self.generate_text(test_prompt, max_tokens=50)
            
            return {
                "status": "healthy",
                "model": self.model,
                "test_response_length": len(response),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @abstractmethod
    async def _create_client(self) -> None:
        """Create the AI service client"""
        pass


class OpenAIService(BaseAIService):
    """OpenAI GPT service implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ConfigurationError("OpenAI API key is required")
        
        self.model = config.get("model", "gpt-4")
        self.organization = config.get("organization")
    
    async def _create_client(self) -> None:
        """Create OpenAI client"""
        if not AsyncOpenAI:
            raise AIServiceError("OpenAI package not installed. Run: pip install openai")
        
        client_kwargs = {"api_key": self.api_key}
        if self.organization:
            client_kwargs["organization"] = self.organization
        
        self._client = AsyncOpenAI(**client_kwargs)
        
        # Test connection
        try:
            models = await self._client.models.list()
            logger.info(f"OpenAI connection successful. Available models: {len(models.data)}")
        except Exception as e:
            raise AIServiceError(f"OpenAI connection test failed: {e}")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using OpenAI GPT"""
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                **kwargs,
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Generated text: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            raise AIServiceError(f"Text generation failed: {e}")
    
    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze image using OpenAI Vision"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = await self._client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                **kwargs,
            )
            
            analysis = response.choices[0].message.content
            logger.debug(f"Image analysis completed: {len(analysis)} characters")
            
            return {
                "analysis": analysis,
                "model": "gpt-4-vision-preview",
                "image_path": image_path,
            }
            
        except Exception as e:
            logger.error(f"OpenAI image analysis failed: {e}")
            raise AIServiceError(f"Image analysis failed: {e}")
    
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract structured data using OpenAI"""
        if not self._initialized:
            await self.initialize()
        
        prompt = f"""
Extract structured data from the following text according to the provided schema.

Schema:
{json.dumps(schema, indent=2)}

Text:
{text}

Return only valid JSON that matches the schema exactly.
"""
        
        try:
            response = await self.generate_text(prompt, **kwargs)
            
            # Try to parse as JSON
            try:
                structured_data = json.loads(response)
                return structured_data
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    structured_data = json.loads(json_match.group())
                    return structured_data
                else:
                    raise AIServiceError("Could not extract valid JSON from response")
                    
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            raise AIServiceError(f"Structured data extraction failed: {e}")


class AnthropicService(BaseAIService):
    """Anthropic Claude service implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ConfigurationError("Anthropic API key is required")
        
        self.model = config.get("model", "claude-3-sonnet-20240229")
    
    async def _create_client(self) -> None:
        """Create Anthropic client"""
        if not AsyncAnthropic:
            raise AIServiceError("Anthropic package not installed. Run: pip install anthropic")
        
        self._client = AsyncAnthropic(api_key=self.api_key)
        
        # Test connection
        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            logger.info("Anthropic connection successful")
        except Exception as e:
            raise AIServiceError(f"Anthropic connection test failed: {e}")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Anthropic Claude"""
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            
            content = response.content[0].text
            logger.debug(f"Generated text: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Anthropic text generation failed: {e}")
            raise AIServiceError(f"Text generation failed: {e}")
    
    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze image using Anthropic Claude Vision"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine image type
            image_type = "image/jpeg"
            if image_path.lower().endswith('.png'):
                image_type = "image/png"
            
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": image_type,
                                    "data": image_data
                                }
                            }
                        ]
                    }
                ],
                **kwargs,
            )
            
            analysis = response.content[0].text
            logger.debug(f"Image analysis completed: {len(analysis)} characters")
            
            return {
                "analysis": analysis,
                "model": self.model,
                "image_path": image_path,
            }
            
        except Exception as e:
            logger.error(f"Anthropic image analysis failed: {e}")
            raise AIServiceError(f"Image analysis failed: {e}")
    
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract structured data using Anthropic Claude"""
        if not self._initialized:
            await self.initialize()
        
        prompt = f"""
Extract structured data from the following text according to the provided schema.

Schema:
{json.dumps(schema, indent=2)}

Text:
{text}

Return only valid JSON that matches the schema exactly. Do not include any explanation or markdown formatting.
"""
        
        try:
            response = await self.generate_text(prompt, **kwargs)
            
            # Try to parse as JSON
            try:
                structured_data = json.loads(response)
                return structured_data
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    structured_data = json.loads(json_match.group())
                    return structured_data
                else:
                    raise AIServiceError("Could not extract valid JSON from response")
                    
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            raise AIServiceError(f"Structured data extraction failed: {e}")


class AIServiceFactory:
    """Factory for creating AI service instances"""
    
    _services = {
        "openai": OpenAIService,
        "anthropic": AnthropicService,
    }
    
    @classmethod
    def create_service(cls, provider: str, config: Dict[str, Any]) -> AIServiceInterface:
        """Create AI service instance"""
        if provider not in cls._services:
            raise ConfigurationError(f"Unsupported AI provider: {provider}")
        
        service_class = cls._services[provider]
        return service_class(config)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available AI providers"""
        return list(cls._services.keys())


class ComputerVisionAnalyzer:
    """Computer vision analyzer for UI elements"""
    
    def __init__(self):
        self.logger = get_logger("computer_vision")
    
    async def analyze_screenshot(
        self,
        image_path: str,
        elements: Optional[List[ElementData]] = None,
    ) -> Dict[str, Any]:
        """Analyze screenshot for UI elements"""
        try:
            # Load image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise AIServiceError(f"Could not load image: {image_path}")
            
            height, width = image.shape[:2]
            
            analysis = {
                "image_path": image_path,
                "dimensions": {"width": width, "height": height},
                "detected_elements": [],
                "ui_patterns": [],
                "accessibility_issues": [],
            }
            
            # Detect common UI elements using OpenCV
            analysis["detected_elements"] = await self._detect_ui_elements(image)
            
            # Analyze existing elements if provided
            if elements:
                analysis["element_analysis"] = await self._analyze_elements(image, elements)
            
            # Detect UI patterns
            analysis["ui_patterns"] = await self._detect_ui_patterns(image)
            
            # Check for accessibility issues
            analysis["accessibility_issues"] = await self._check_accessibility(image, elements)
            
            self.logger.info(f"Screenshot analysis completed: {len(analysis['detected_elements'])} elements detected")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Screenshot analysis failed: {e}")
            raise AIServiceError(f"Screenshot analysis failed: {e}")
    
    async def _detect_ui_elements(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements using computer vision"""
        elements = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect buttons using contour detection
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area (buttons are usually medium-sized)
            if 500 < area < 10000:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (buttons are usually rectangular)
                aspect_ratio = float(w) / h
                if 0.5 < aspect_ratio < 5.0:
                    elements.append({
                        "type": "potential_button",
                        "position": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        "area": float(area),
                        "aspect_ratio": float(aspect_ratio),
                        "confidence": min(1.0, area / 5000),  # Simple confidence score
                    })
        
        # Detect text regions using MSER (Maximally Stable Extremal Regions)
        try:
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            
            for region in regions:
                if len(region) > 10:  # Filter small regions
                    hull = cv2.convexHull(region.reshape(-1, 1, 2))
                    x, y, w, h = cv2.boundingRect(hull)
                    
                    if w > 20 and h > 10:  # Minimum text size
                        elements.append({
                            "type": "potential_text",
                            "position": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                            "confidence": 0.7,
                        })
        except Exception as e:
            self.logger.warning(f"Text detection failed: {e}")
        
        return elements[:50]  # Limit to 50 elements
    
    async def _analyze_elements(
        self, 
        image: np.ndarray, 
        elements: List[ElementData]
    ) -> List[Dict[str, Any]]:
        """Analyze provided elements for visual properties"""
        analysis = []
        
        for element in elements:
            try:
                pos = element.position
                if not pos or not all(k in pos for k in ['x', 'y', 'width', 'height']):
                    continue
                
                x, y, w, h = int(pos['x']), int(pos['y']), int(pos['width']), int(pos['height'])
                
                # Extract element region
                if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                    x2 = min(x + w, image.shape[1])
                    y2 = min(y + h, image.shape[0])
                    
                    if x2 > x and y2 > y:
                        element_region = image[y:y2, x:x2]
                        
                        # Analyze colors
                        mean_color = np.mean(element_region, axis=(0, 1))
                        
                        # Analyze contrast
                        gray_region = cv2.cvtColor(element_region, cv2.COLOR_BGR2GRAY)
                        contrast = np.std(gray_region)
                        
                        analysis.append({
                            "element_id": element.id,
                            "visual_properties": {
                                "mean_color": mean_color.tolist(),
                                "contrast": float(contrast),
                                "brightness": float(np.mean(gray_region)),
                            },
                            "accessibility_score": await self._calculate_accessibility_score(element_region),
                        })
                        
            except Exception as e:
                self.logger.warning(f"Element analysis failed for {element.id}: {e}")
                continue
        
        return analysis
    
    async def _detect_ui_patterns(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect common UI patterns"""
        patterns = []
        
        # Detect navigation bars (horizontal rectangles at top)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Check top 20% for navigation
        nav_region = gray[:int(height * 0.2), :]
        nav_edges = cv2.Canny(nav_region, 50, 150)
        
        if np.sum(nav_edges) > width * 5:  # Threshold for navigation detection
            patterns.append({
                "type": "navigation_bar",
                "position": {"x": 0, "y": 0, "width": width, "height": int(height * 0.2)},
                "confidence": 0.8,
            })
        
        # Detect form patterns (groups of input-like rectangles)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        input_candidates = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # Input fields are typically wide and shallow
            if 3 < aspect_ratio < 10 and 20 < h < 60 and w > 100:
                input_candidates.append({"x": x, "y": y, "width": w, "height": h})
        
        if len(input_candidates) >= 2:
            patterns.append({
                "type": "form_pattern",
                "elements": input_candidates,
                "confidence": 0.7,
            })
        
        return patterns
    
    async def _check_accessibility(
        self, 
        image: np.ndarray, 
        elements: Optional[List[ElementData]] = None
    ) -> List[Dict[str, Any]]:
        """Check for accessibility issues"""
        issues = []
        
        # Check overall contrast
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        overall_contrast = np.std(gray)
        
        if overall_contrast < 30:
            issues.append({
                "type": "low_contrast",
                "severity": "warning",
                "description": "Overall page contrast may be too low",
                "recommendation": "Increase color contrast between elements",
            })
        
        # Check for very small elements
        if elements:
            for element in elements:
                pos = element.position
                if pos and 'width' in pos and 'height' in pos:
                    if pos['width'] < 44 or pos['height'] < 44:
                        issues.append({
                            "type": "small_touch_target",
                            "element_id": element.id,
                            "severity": "error",
                            "description": f"Element {element.id} may be too small for touch interaction",
                            "recommendation": "Ensure touch targets are at least 44x44 pixels",
                        })
        
        return issues
    
    async def _calculate_accessibility_score(self, element_region: np.ndarray) -> float:
        """Calculate accessibility score for an element"""
        try:
            gray = cv2.cvtColor(element_region, cv2.COLOR_BGR2GRAY)
            
            # Factors for accessibility score
            contrast = np.std(gray) / 255.0  # Normalized contrast
            brightness = np.mean(gray) / 255.0  # Normalized brightness
            
            # Size factor
            height, width = element_region.shape[:2]
            size_factor = min(1.0, (width * height) / (44 * 44))  # Based on minimum touch target
            
            # Combined score
            score = (contrast * 0.4 + (1 - abs(brightness - 0.5) * 2) * 0.3 + size_factor * 0.3)
            
            return float(np.clip(score, 0.0, 1.0))
            
        except Exception:
            return 0.5  # Default score if calculation fails
