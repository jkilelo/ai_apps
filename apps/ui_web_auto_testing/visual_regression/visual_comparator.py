"""
Visual Regression Testing Module
Compares screenshots to detect UI changes using multiple strategies
"""

import asyncio
import base64
import hashlib
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from PIL import Image, ImageChops, ImageDraw, ImageFilter
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
import imagehash

logger = logging.getLogger(__name__)


class ComparisonStrategy(Enum):
    """Visual comparison strategies"""
    PIXEL_DIFF = "pixel_diff"
    STRUCTURAL_SIMILARITY = "structural_similarity"
    PERCEPTUAL_HASH = "perceptual_hash"
    FEATURE_MATCHING = "feature_matching"
    AI_SEMANTIC = "ai_semantic"


class DiffSeverity(Enum):
    """Severity levels for visual differences"""
    NONE = "none"
    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class VisualDiff:
    """Represents a visual difference between images"""
    severity: DiffSeverity
    confidence: float
    diff_percentage: float
    affected_regions: List[Tuple[int, int, int, int]]  # x, y, width, height
    diff_image_path: Optional[str] = None
    comparison_metrics: Dict[str, float] = None
    description: str = ""
    suggestions: List[str] = None


@dataclass
class VisualRegressionResult:
    """Complete visual regression test result"""
    test_id: str
    baseline_path: str
    current_path: str
    timestamp: datetime
    passed: bool
    diffs: List[VisualDiff]
    overall_similarity: float
    execution_time: float
    metadata: Dict[str, Any]


class VisualComparator:
    """Advanced visual regression testing with multiple comparison strategies"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.baseline_dir = Path(self.config.get("baseline_dir", "./visual_baselines"))
        self.diff_dir = Path(self.config.get("diff_dir", "./visual_diffs"))
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.diff_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for visual comparison"""
        return {
            "threshold": {
                "pixel_diff": 0.05,  # 5% difference threshold
                "ssim": 0.95,  # 95% similarity required
                "perceptual_hash": 10,  # Hash distance threshold
                "feature_match": 0.7  # 70% feature match required
            },
            "ignore_regions": [],  # Regions to ignore (e.g., timestamps)
            "antialiasing": True,
            "color_threshold": 10,  # Color difference threshold
            "blur_radius": 1,  # Blur for minor pixel shifts
            "strategies": [
                ComparisonStrategy.PIXEL_DIFF,
                ComparisonStrategy.STRUCTURAL_SIMILARITY,
                ComparisonStrategy.PERCEPTUAL_HASH
            ]
        }
    
    async def capture_screenshot(self, page, selector: Optional[str] = None) -> bytes:
        """Capture screenshot of page or specific element"""
        if selector:
            element = await page.query_selector(selector)
            if element:
                return await element.screenshot()
        return await page.screenshot(full_page=True)
    
    async def compare_images(
        self,
        baseline: Image.Image,
        current: Image.Image,
        test_id: str,
        ignore_regions: Optional[List[Tuple[int, int, int, int]]] = None
    ) -> VisualRegressionResult:
        """Compare two images using multiple strategies"""
        start_time = asyncio.get_event_loop().time()
        
        # Ensure images are same size
        if baseline.size != current.size:
            current = current.resize(baseline.size, Image.Resampling.LANCZOS)
        
        # Apply ignore regions
        if ignore_regions:
            baseline, current = self._apply_ignore_regions(
                baseline.copy(), current.copy(), ignore_regions
            )
        
        # Run comparison strategies
        diffs = []
        metrics = {}
        
        for strategy in self.config["strategies"]:
            if strategy == ComparisonStrategy.PIXEL_DIFF:
                diff = await self._pixel_diff_comparison(baseline, current, test_id)
                metrics["pixel_diff"] = diff.diff_percentage
                diffs.append(diff)
                
            elif strategy == ComparisonStrategy.STRUCTURAL_SIMILARITY:
                diff = await self._ssim_comparison(baseline, current, test_id)
                metrics["ssim"] = diff.comparison_metrics.get("ssim", 0)
                diffs.append(diff)
                
            elif strategy == ComparisonStrategy.PERCEPTUAL_HASH:
                diff = await self._perceptual_hash_comparison(baseline, current)
                metrics["hash_distance"] = diff.comparison_metrics.get("hash_distance", 0)
                diffs.append(diff)
        
        # Calculate overall similarity
        overall_similarity = self._calculate_overall_similarity(metrics)
        
        # Determine if test passed
        passed = all(d.severity in [DiffSeverity.NONE, DiffSeverity.NEGLIGIBLE] for d in diffs)
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return VisualRegressionResult(
            test_id=test_id,
            baseline_path=str(self.baseline_dir / f"{test_id}_baseline.png"),
            current_path=str(self.diff_dir / f"{test_id}_current.png"),
            timestamp=datetime.now(),
            passed=passed,
            diffs=[d for d in diffs if d.severity != DiffSeverity.NONE],
            overall_similarity=overall_similarity,
            execution_time=execution_time,
            metadata={
                "strategies_used": [s.value for s in self.config["strategies"]],
                "thresholds": self.config["threshold"],
                "image_size": baseline.size
            }
        )
    
    async def _pixel_diff_comparison(
        self, baseline: Image.Image, current: Image.Image, test_id: str
    ) -> VisualDiff:
        """Pixel-by-pixel comparison with intelligent diffing"""
        # Apply slight blur to handle anti-aliasing differences
        if self.config.get("antialiasing"):
            baseline_blurred = baseline.filter(ImageFilter.GaussianBlur(radius=1))
            current_blurred = current.filter(ImageFilter.GaussianBlur(radius=1))
        else:
            baseline_blurred = baseline
            current_blurred = current
        
        # Calculate difference
        diff = ImageChops.difference(baseline_blurred, current_blurred)
        
        # Convert to numpy for analysis
        diff_array = np.array(diff)
        baseline_array = np.array(baseline)
        
        # Calculate diff percentage
        total_pixels = diff_array.shape[0] * diff_array.shape[1]
        diff_pixels = np.sum(diff_array > self.config["color_threshold"])
        diff_percentage = (diff_pixels / total_pixels) * 100
        
        # Find affected regions
        affected_regions = self._find_diff_regions(diff_array)
        
        # Generate diff image with highlights
        diff_image = self._generate_diff_image(baseline, current, affected_regions)
        diff_image_path = self.diff_dir / f"{test_id}_pixel_diff.png"
        diff_image.save(diff_image_path)
        
        # Determine severity
        severity = self._calculate_severity(diff_percentage, self.config["threshold"]["pixel_diff"])
        
        return VisualDiff(
            severity=severity,
            confidence=0.95,
            diff_percentage=diff_percentage,
            affected_regions=affected_regions,
            diff_image_path=str(diff_image_path),
            comparison_metrics={"pixel_diff_percentage": diff_percentage},
            description=f"Pixel difference: {diff_percentage:.2f}%",
            suggestions=self._generate_suggestions(severity, diff_percentage)
        )
    
    async def _ssim_comparison(
        self, baseline: Image.Image, current: Image.Image, test_id: str
    ) -> VisualDiff:
        """Structural Similarity Index comparison"""
        # Convert to grayscale for SSIM
        baseline_gray = np.array(baseline.convert('L'))
        current_gray = np.array(current.convert('L'))
        
        # Calculate SSIM
        similarity, diff_image = ssim(baseline_gray, current_gray, full=True)
        
        # Convert diff to percentage
        diff_percentage = (1 - similarity) * 100
        
        # Find regions with low similarity
        diff_regions = self._find_ssim_diff_regions(diff_image)
        
        # Save SSIM diff visualization
        ssim_diff = Image.fromarray((diff_image * 255).astype(np.uint8))
        ssim_diff_path = self.diff_dir / f"{test_id}_ssim_diff.png"
        ssim_diff.save(ssim_diff_path)
        
        # Determine severity
        severity = self._calculate_severity(
            similarity, self.config["threshold"]["ssim"], inverse=True
        )
        
        return VisualDiff(
            severity=severity,
            confidence=0.90,
            diff_percentage=diff_percentage,
            affected_regions=diff_regions,
            diff_image_path=str(ssim_diff_path),
            comparison_metrics={"ssim": similarity},
            description=f"Structural similarity: {similarity:.3f}",
            suggestions=self._generate_suggestions(severity, diff_percentage)
        )
    
    async def _perceptual_hash_comparison(
        self, baseline: Image.Image, current: Image.Image
    ) -> VisualDiff:
        """Perceptual hash comparison for semantic similarity"""
        # Calculate perceptual hashes
        baseline_hash = imagehash.average_hash(baseline)
        current_hash = imagehash.average_hash(current)
        
        # Calculate hash distance
        hash_distance = baseline_hash - current_hash
        
        # Determine severity based on hash distance
        threshold = self.config["threshold"]["perceptual_hash"]
        if hash_distance <= threshold * 0.3:
            severity = DiffSeverity.NONE
        elif hash_distance <= threshold * 0.6:
            severity = DiffSeverity.NEGLIGIBLE
        elif hash_distance <= threshold:
            severity = DiffSeverity.MINOR
        else:
            severity = DiffSeverity.MODERATE
        
        return VisualDiff(
            severity=severity,
            confidence=0.85,
            diff_percentage=(hash_distance / 64) * 100,  # Normalize to percentage
            affected_regions=[],  # Hash comparison doesn't identify regions
            comparison_metrics={"hash_distance": hash_distance},
            description=f"Perceptual hash distance: {hash_distance}",
            suggestions=[]
        )
    
    def _apply_ignore_regions(
        self, baseline: Image.Image, current: Image.Image, 
        regions: List[Tuple[int, int, int, int]]
    ) -> Tuple[Image.Image, Image.Image]:
        """Apply ignore regions by masking them out"""
        mask_color = (128, 128, 128)  # Gray mask
        
        for x, y, w, h in regions:
            # Draw gray rectangles over ignore regions
            ImageDraw.Draw(baseline).rectangle([x, y, x+w, y+h], fill=mask_color)
            ImageDraw.Draw(current).rectangle([x, y, x+w, y+h], fill=mask_color)
        
        return baseline, current
    
    def _find_diff_regions(self, diff_array: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Find bounding boxes of different regions"""
        # Threshold the difference
        threshold = self.config["color_threshold"]
        binary = np.any(diff_array > threshold, axis=2).astype(np.uint8) * 255
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Get bounding boxes
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out tiny differences
            if w * h > 100:  # Minimum area threshold
                regions.append((x, y, w, h))
        
        return regions
    
    def _find_ssim_diff_regions(self, diff_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Find regions with low SSIM scores"""
        # Invert and threshold
        binary = ((1 - diff_image) * 255).astype(np.uint8)
        _, thresh = cv2.threshold(binary, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > 100:
                regions.append((x, y, w, h))
        
        return regions
    
    def _generate_diff_image(
        self, baseline: Image.Image, current: Image.Image, 
        regions: List[Tuple[int, int, int, int]]
    ) -> Image.Image:
        """Generate a visual diff image with highlighted changes"""
        # Create a copy of the current image
        diff_image = current.copy()
        draw = ImageDraw.Draw(diff_image)
        
        # Draw rectangles around changed regions
        for x, y, w, h in regions:
            draw.rectangle([x, y, x+w, y+h], outline="red", width=3)
        
        # Create side-by-side comparison
        width = baseline.width + current.width + diff_image.width + 20
        height = max(baseline.height, current.height, diff_image.height) + 40
        
        comparison = Image.new('RGB', (width, height), color='white')
        
        # Add labels
        draw_comp = ImageDraw.Draw(comparison)
        draw_comp.text((10, 10), "Baseline", fill="black")
        draw_comp.text((baseline.width + 20, 10), "Current", fill="black")
        draw_comp.text((baseline.width + current.width + 30, 10), "Differences", fill="black")
        
        # Paste images
        comparison.paste(baseline, (0, 30))
        comparison.paste(current, (baseline.width + 10, 30))
        comparison.paste(diff_image, (baseline.width + current.width + 20, 30))
        
        return comparison
    
    def _calculate_severity(
        self, value: float, threshold: float, inverse: bool = False
    ) -> DiffSeverity:
        """Calculate severity based on value and threshold"""
        if inverse:  # For metrics where higher is better (like SSIM)
            if value >= threshold:
                return DiffSeverity.NONE
            elif value >= threshold * 0.95:
                return DiffSeverity.NEGLIGIBLE
            elif value >= threshold * 0.90:
                return DiffSeverity.MINOR
            elif value >= threshold * 0.80:
                return DiffSeverity.MODERATE
            elif value >= threshold * 0.60:
                return DiffSeverity.MAJOR
            else:
                return DiffSeverity.CRITICAL
        else:  # For metrics where lower is better (like diff percentage)
            if value <= threshold:
                return DiffSeverity.NONE
            elif value <= threshold * 2:
                return DiffSeverity.NEGLIGIBLE
            elif value <= threshold * 5:
                return DiffSeverity.MINOR
            elif value <= threshold * 10:
                return DiffSeverity.MODERATE
            elif value <= threshold * 20:
                return DiffSeverity.MAJOR
            else:
                return DiffSeverity.CRITICAL
    
    def _calculate_overall_similarity(self, metrics: Dict[str, float]) -> float:
        """Calculate weighted overall similarity score"""
        weights = {
            "pixel_diff": 0.3,
            "ssim": 0.5,
            "hash_distance": 0.2
        }
        
        score = 0
        total_weight = 0
        
        if "pixel_diff" in metrics:
            score += (1 - metrics["pixel_diff"] / 100) * weights["pixel_diff"]
            total_weight += weights["pixel_diff"]
        
        if "ssim" in metrics:
            score += metrics["ssim"] * weights["ssim"]
            total_weight += weights["ssim"]
        
        if "hash_distance" in metrics:
            normalized_hash = 1 - min(metrics["hash_distance"] / 64, 1)
            score += normalized_hash * weights["hash_distance"]
            total_weight += weights["hash_distance"]
        
        return score / total_weight if total_weight > 0 else 0
    
    def _generate_suggestions(self, severity: DiffSeverity, diff_percentage: float) -> List[str]:
        """Generate actionable suggestions based on diff analysis"""
        suggestions = []
        
        if severity == DiffSeverity.NEGLIGIBLE:
            suggestions.append("Minor pixel differences detected - likely due to anti-aliasing or rendering variations")
            suggestions.append("Consider updating baseline if changes are intentional")
        
        elif severity in [DiffSeverity.MINOR, DiffSeverity.MODERATE]:
            suggestions.append(f"Visual changes detected ({diff_percentage:.1f}% difference)")
            suggestions.append("Review the diff image to verify if changes are expected")
            suggestions.append("Update baseline image if changes are approved")
        
        elif severity in [DiffSeverity.MAJOR, DiffSeverity.CRITICAL]:
            suggestions.append(f"Significant visual regression detected ({diff_percentage:.1f}% difference)")
            suggestions.append("Investigate recent code changes that might have affected the UI")
            suggestions.append("Check browser console for rendering errors")
            suggestions.append("Verify CSS and layout changes")
        
        return suggestions
    
    async def update_baseline(self, test_id: str, image: Image.Image):
        """Update baseline image for a test"""
        baseline_path = self.baseline_dir / f"{test_id}_baseline.png"
        image.save(baseline_path)
        logger.info(f"Updated baseline for test: {test_id}")
    
    async def get_baseline(self, test_id: str) -> Optional[Image.Image]:
        """Get baseline image for a test"""
        baseline_path = self.baseline_dir / f"{test_id}_baseline.png"
        if baseline_path.exists():
            return Image.open(baseline_path)
        return None
    
    def generate_report(self, results: List[VisualRegressionResult]) -> Dict[str, Any]:
        """Generate comprehensive visual regression report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        
        severity_counts = {
            severity.value: 0 for severity in DiffSeverity
        }
        
        for result in results:
            for diff in result.diffs:
                severity_counts[diff.severity.value] += 1
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "execution_time": sum(r.execution_time for r in results),
                "timestamp": datetime.now().isoformat()
            },
            "severity_distribution": severity_counts,
            "failed_tests": [
                {
                    "test_id": r.test_id,
                    "similarity": r.overall_similarity,
                    "diffs": [asdict(d) for d in r.diffs],
                    "suggestions": list(set(
                        suggestion 
                        for d in r.diffs 
                        for suggestion in (d.suggestions or [])
                    ))
                }
                for r in results if not r.passed
            ],
            "recommendations": self._generate_report_recommendations(results)
        }
    
    def _generate_report_recommendations(self, results: List[VisualRegressionResult]) -> List[str]:
        """Generate overall recommendations based on results"""
        recommendations = []
        
        failed_count = sum(1 for r in results if not r.passed)
        
        if failed_count == 0:
            recommendations.append("All visual regression tests passed - UI is stable")
        elif failed_count < len(results) * 0.1:
            recommendations.append("Minor visual regressions detected - review individual failures")
        else:
            recommendations.append("Significant visual regressions detected across multiple tests")
            recommendations.append("Consider reviewing recent UI changes or framework updates")
            recommendations.append("Run tests in isolation to rule out environmental factors")
        
        # Check for patterns
        critical_count = sum(
            1 for r in results 
            for d in r.diffs 
            if d.severity == DiffSeverity.CRITICAL
        )
        
        if critical_count > 0:
            recommendations.append(f"{critical_count} critical visual issues found - immediate attention required")
        
        return recommendations