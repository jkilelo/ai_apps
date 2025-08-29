#!/usr/bin/env python3
"""
UNIT TESTS FOR ELEMENT EXTRACTOR PYDANTIC MODELS
=================================================
Tests for data models, validation, and serialization.
"""

import json
import pytest
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import the models to test
from element_extractor_no_llm_robust import (
    BoundingBox,
    ElementStyle,
    AccessibilityInfo,
    ElementMetrics,
    ElementData,
    ExtractionResult,
    ElementType,
    ExtractionStrategy,
    ElementState,
    Platform,
)


class TestBoundingBox:
    """Test cases for BoundingBox model"""

    def test_valid_bounding_box_creation(self):
        """Test creating a valid bounding box"""
        bbox = BoundingBox(x=10.0, y=20.0, width=100.0, height=50.0)
        assert bbox.x == 10.0
        assert bbox.y == 20.0
        assert bbox.width == 100.0
        assert bbox.height == 50.0

    def test_bounding_box_negative_coordinates_invalid(self):
        """Test that negative coordinates are rejected"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            BoundingBox(x=-10.0, y=20.0, width=100.0, height=50.0)

    def test_bounding_box_negative_dimensions_invalid(self):
        """Test that negative dimensions are rejected"""
        with pytest.raises(Exception):
            BoundingBox(x=10.0, y=20.0, width=-100.0, height=50.0)

    def test_bounding_box_center_calculation(self):
        """Test center point calculation"""
        bbox = BoundingBox(x=0.0, y=0.0, width=100.0, height=100.0)
        center = bbox.center
        assert center == (50.0, 50.0)

    def test_bounding_box_area_calculation(self):
        """Test area calculation"""
        bbox = BoundingBox(x=0.0, y=0.0, width=10.0, height=20.0)
        assert bbox.area == 200.0

    def test_bounding_box_contains_point(self):
        """Test point containment check"""
        bbox = BoundingBox(x=10.0, y=10.0, width=50.0, height=50.0)
        
        # Point inside
        assert bbox.contains_point(30.0, 30.0) is True
        
        # Point outside
        assert bbox.contains_point(5.0, 5.0) is False
        assert bbox.contains_point(70.0, 70.0) is False
        
        # Point on boundary
        assert bbox.contains_point(10.0, 10.0) is True
        assert bbox.contains_point(60.0, 60.0) is True

    def test_bounding_box_intersection(self):
        """Test bounding box intersection"""
        bbox1 = BoundingBox(x=0.0, y=0.0, width=50.0, height=50.0)
        bbox2 = BoundingBox(x=25.0, y=25.0, width=50.0, height=50.0)
        bbox3 = BoundingBox(x=100.0, y=100.0, width=50.0, height=50.0)
        
        # Overlapping boxes
        assert bbox1.intersects(bbox2) is True
        assert bbox2.intersects(bbox1) is True
        
        # Non-overlapping boxes
        assert bbox1.intersects(bbox3) is False
        assert bbox3.intersects(bbox1) is False

    def test_bounding_box_immutability(self):
        """Test that BoundingBox is immutable (frozen)"""
        bbox = BoundingBox(x=10.0, y=20.0, width=100.0, height=50.0)
        with pytest.raises(Exception):  # Frozen model
            bbox.x = 20.0


class TestElementStyle:
    """Test cases for ElementStyle model"""

    def test_element_style_creation(self):
        """Test creating ElementStyle with various properties"""
        style = ElementStyle(
            display="block",
            visibility="visible",
            opacity=0.8,
            position="absolute",
            z_index=100,
            background_color="#ffffff",
            color="#000000",
        )
        assert style.display == "block"
        assert style.opacity == 0.8
        assert style.z_index == 100

    def test_element_style_opacity_validation(self):
        """Test opacity value validation (0-1 range)"""
        # Valid opacity
        style1 = ElementStyle(opacity=0.5)
        assert style1.opacity == 0.5
        
        # Invalid opacity
        with pytest.raises(Exception):
            ElementStyle(opacity=1.5)
        
        with pytest.raises(Exception):
            ElementStyle(opacity=-0.1)

    def test_element_style_extra_fields_allowed(self):
        """Test that extra CSS properties are allowed"""
        style = ElementStyle(
            display="flex",
            custom_property="custom_value",
            webkit_transform="rotate(45deg)",
        )
        assert style.display == "flex"
        # Extra fields are stored in model


class TestAccessibilityInfo:
    """Test cases for AccessibilityInfo model"""

    def test_accessibility_info_creation(self):
        """Test creating accessibility info"""
        a11y = AccessibilityInfo(
            role="button",
            aria_label="Submit form",
            aria_describedby="submit-help",
            aria_hidden=False,
            aria_expanded=True,
            tab_index=0,
        )
        assert a11y.role == "button"
        assert a11y.aria_label == "Submit form"
        assert a11y.aria_hidden is False
        assert a11y.tab_index == 0

    def test_accessibility_info_optional_fields(self):
        """Test that all fields are optional"""
        a11y = AccessibilityInfo()
        assert a11y.role is None
        assert a11y.aria_label is None
        assert a11y.tab_index is None


class TestElementMetrics:
    """Test cases for ElementMetrics model"""

    def test_element_metrics_creation(self):
        """Test creating element metrics"""
        metrics = ElementMetrics(
            extraction_time_ms=123.45,
            strategy_used=ExtractionStrategy.DOM_REGULAR,
            retry_count=2,
            confidence_score=0.95,
            warnings=["Warning 1", "Warning 2"],
            errors=["Error 1"],
        )
        assert metrics.extraction_time_ms == 123.45
        assert metrics.strategy_used == ExtractionStrategy.DOM_REGULAR
        assert metrics.retry_count == 2
        assert len(metrics.warnings) == 2
        assert len(metrics.errors) == 1

    def test_element_metrics_validation(self):
        """Test metrics validation"""
        # Negative extraction time should fail
        with pytest.raises(Exception):
            ElementMetrics(
                extraction_time_ms=-10.0,
                strategy_used=ExtractionStrategy.DOM_REGULAR,
            )
        
        # Confidence score out of range
        with pytest.raises(Exception):
            ElementMetrics(
                extraction_time_ms=10.0,
                strategy_used=ExtractionStrategy.DOM_REGULAR,
                confidence_score=1.5,
            )

    def test_element_metrics_immutability(self):
        """Test that ElementMetrics is immutable"""
        metrics = ElementMetrics(
            extraction_time_ms=100.0,
            strategy_used=ExtractionStrategy.DOM_REGULAR,
        )
        with pytest.raises(Exception):
            metrics.retry_count = 5


class TestElementData:
    """Test cases for ElementData model"""

    @pytest.fixture
    def valid_element_data(self) -> Dict[str, Any]:
        """Fixture for valid element data"""
        return {
            "element_id": "test_element_123",
            "tag_name": "button",
            "element_type": ElementType.BUTTON,
            "text_content": "Click me",
            "is_visible": True,
            "is_clickable": True,
        }

    def test_element_data_creation(self, valid_element_data):
        """Test creating valid ElementData"""
        element = ElementData(**valid_element_data)
        assert element.element_id == "test_element_123"
        assert element.tag_name == "button"
        assert element.element_type == ElementType.BUTTON
        assert element.is_clickable is True

    def test_element_data_empty_id_validation(self):
        """Test that empty element_id is rejected"""
        with pytest.raises(Exception):
            ElementData(
                element_id="",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
            )
        
        with pytest.raises(Exception):
            ElementData(
                element_id="   ",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
            )

    def test_element_data_self_parent_validation(self):
        """Test that element cannot be its own parent"""
        with pytest.raises(Exception):
            ElementData(
                element_id="elem1",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
                parent_id="elem1",
            )

    def test_element_data_self_child_validation(self):
        """Test that element cannot be its own child"""
        with pytest.raises(Exception):
            ElementData(
                element_id="elem1",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
                children_ids=["elem1", "elem2"],
            )

    def test_element_data_with_bounding_box(self):
        """Test ElementData with BoundingBox"""
        element = ElementData(
            element_id="elem1",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            bounding_box=BoundingBox(x=10, y=20, width=100, height=50),
        )
        assert element.bounding_box is not None
        assert element.bounding_box.x == 10
        assert element.bounding_box.area == 5000

    def test_element_data_to_dict(self, valid_element_data):
        """Test converting ElementData to dictionary"""
        element = ElementData(**valid_element_data)
        data_dict = element.to_dict()
        
        assert isinstance(data_dict, dict)
        assert data_dict["element_id"] == "test_element_123"
        assert data_dict["tag_name"] == "button"
        assert "extraction_timestamp" in data_dict

    def test_element_data_to_test_data(self, valid_element_data):
        """Test generating test data structure"""
        element = ElementData(
            **valid_element_data,
            css_selector="#test-button",
            accessibility=AccessibilityInfo(role="button"),
        )
        test_data = element.to_test_data()
        
        assert test_data["selector"] == "#test-button"
        assert test_data["type"] == "button"
        assert test_data["clickable"] is True
        assert "accessibility" in test_data

    def test_element_data_shadow_dom_properties(self):
        """Test shadow DOM related properties"""
        element = ElementData(
            element_id="shadow_host",
            tag_name="custom-element",
            element_type=ElementType.SHADOW_HOST,
            has_shadow_root=True,
            shadow_mode="open",
            is_custom_element=True,
            custom_element_name="custom-element",
        )
        assert element.has_shadow_root is True
        assert element.shadow_mode == "open"
        assert element.is_custom_element is True

    def test_element_data_iframe_properties(self):
        """Test iframe context properties"""
        element = ElementData(
            element_id="iframe_elem",
            tag_name="button",
            element_type=ElementType.BUTTON,
            iframe_context="iframe_0",
            iframe_depth=2,
        )
        assert element.iframe_context == "iframe_0"
        assert element.iframe_depth == 2

    def test_element_data_form_properties(self):
        """Test form-related properties"""
        element = ElementData(
            element_id="input_email",
            tag_name="input",
            element_type=ElementType.INPUT,
            form_associated=True,
            form_id="login_form",
            input_type="email",
            validation_state="valid",
        )
        assert element.form_associated is True
        assert element.form_id == "login_form"
        assert element.input_type == "email"


class TestExtractionResult:
    """Test cases for ExtractionResult model"""

    @pytest.fixture
    def sample_elements(self) -> List[ElementData]:
        """Create sample elements for testing"""
        return [
            ElementData(
                element_id="btn1",
                tag_name="button",
                element_type=ElementType.BUTTON,
                is_clickable=True,
            ),
            ElementData(
                element_id="input1",
                tag_name="input",
                element_type=ElementType.INPUT,
                form_associated=True,
            ),
            ElementData(
                element_id="img1",
                tag_name="img",
                element_type=ElementType.IMAGE,
                media_type="image",
            ),
            ElementData(
                element_id="custom1",
                tag_name="my-component",
                element_type=ElementType.WEB_COMPONENT,
                is_custom_element=True,
                has_shadow_root=True,
            ),
        ]

    def test_extraction_result_creation(self):
        """Test creating ExtractionResult"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            page_title="Example Page",
        )
        assert result.url == "https://example.com"
        assert result.platform == Platform.DESKTOP
        assert result.extraction_id is not None
        assert isinstance(result.timestamp, datetime)

    def test_extraction_result_auto_categorization(self, sample_elements):
        """Test automatic element categorization"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=sample_elements,
        )
        
        # Check total count
        assert result.total_elements == 4
        
        # Check categorization
        assert len(result.interactive_elements) == 1  # button
        assert len(result.form_elements) == 1  # input
        assert len(result.media_elements) == 1  # image
        assert len(result.custom_elements) == 1  # web component
        
        # Check technology detection
        assert result.has_web_components is True
        assert result.has_shadow_dom is True

    def test_extraction_result_export_json(self, tmp_path, sample_elements):
        """Test exporting results to JSON"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=sample_elements,
        )
        
        json_file = tmp_path / "test_export.json"
        result.export_json(json_file)
        
        assert json_file.exists()
        
        # Load and verify JSON
        with open(json_file, "r") as f:
            data = json.load(f)
        
        assert data["url"] == "https://example.com"
        assert data["total_elements"] == 4
        assert len(data["elements"]) == 4

    def test_extraction_result_export_csv(self, tmp_path, sample_elements):
        """Test exporting results to CSV"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=sample_elements,
        )
        
        csv_file = tmp_path / "test_export.csv"
        result.export_csv(csv_file)
        
        assert csv_file.exists()
        
        # Read and verify CSV
        import csv
        
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 4
        assert rows[0]["element_id"] == "btn1"
        assert rows[0]["element_type"] == "button"

    def test_extraction_result_get_summary(self, sample_elements):
        """Test getting extraction summary"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=sample_elements,
            frameworks_detected=["React", "Redux"],
            extraction_duration_ms=1234.56,
            extraction_completeness=0.95,
            extraction_accuracy=0.98,
        )
        
        summary = result.get_summary()
        
        assert summary["url"] == "https://example.com"
        assert summary["total_elements"] == 4
        assert summary["interactive_elements"] == 1
        assert summary["frameworks"] == ["React", "Redux"]
        assert summary["extraction_time_ms"] == 1234.56
        assert summary["completeness"] == 0.95
        assert summary["accuracy"] == 0.98

    def test_extraction_result_quality_metrics(self):
        """Test extraction quality metrics"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            extraction_completeness=0.85,
            extraction_accuracy=0.92,
            warnings=["Warning 1", "Warning 2"],
            errors=["Error 1"],
        )
        
        assert result.extraction_completeness == 0.85
        assert result.extraction_accuracy == 0.92
        assert len(result.warnings) == 2
        assert len(result.errors) == 1

    def test_extraction_result_validation_ranges(self):
        """Test validation of metric ranges"""
        # Completeness out of range
        with pytest.raises(Exception):
            ExtractionResult(
                url="https://example.com",
                platform=Platform.DESKTOP,
                extraction_completeness=1.5,
            )
        
        # Negative extraction duration
        with pytest.raises(Exception):
            ExtractionResult(
                url="https://example.com",
                platform=Platform.DESKTOP,
                extraction_duration_ms=-100,
            )


class TestEnums:
    """Test cases for enum types"""

    def test_element_type_enum(self):
        """Test ElementType enum values"""
        assert ElementType.BUTTON.value == "button"
        assert ElementType.LINK.value == "link"
        assert ElementType.WEB_COMPONENT.value == "web_component"
        
        # Test all enum members are accessible
        all_types = list(ElementType)
        assert len(all_types) > 15  # Should have many element types

    def test_extraction_strategy_enum(self):
        """Test ExtractionStrategy enum values"""
        assert ExtractionStrategy.DOM_REGULAR.value == "dom_regular"
        assert ExtractionStrategy.DOM_SHADOW.value == "dom_shadow"
        assert ExtractionStrategy.WEBASSEMBLY.value == "webassembly"
        
        # Test all strategies
        all_strategies = list(ExtractionStrategy)
        assert len(all_strategies) == 18  # Should have exactly 18 strategies

    def test_element_state_enum(self):
        """Test ElementState enum values"""
        assert ElementState.VISIBLE.value == "visible"
        assert ElementState.HIDDEN.value == "hidden"
        assert ElementState.LOADING.value == "loading"

    def test_platform_enum(self):
        """Test Platform enum values"""
        assert Platform.DESKTOP.value == "desktop"
        assert Platform.MOBILE.value == "mobile"
        assert Platform.TABLET.value == "tablet"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_extremely_large_element_collection(self):
        """Test handling of large element collections"""
        # Create 1000 elements
        elements = []
        for i in range(1000):
            elements.append(
                ElementData(
                    element_id=f"elem_{i}",
                    tag_name="div",
                    element_type=ElementType.UNKNOWN,
                )
            )
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=elements,
        )
        
        assert result.total_elements == 1000
        assert len(result.elements) == 1000

    def test_deeply_nested_iframe_context(self):
        """Test deeply nested iframe contexts"""
        element = ElementData(
            element_id="deep_elem",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            iframe_context="iframe_0>iframe_1>iframe_2>iframe_3>iframe_4",
            iframe_depth=5,
        )
        assert element.iframe_depth == 5

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters"""
        element = ElementData(
            element_id="unicode_元素_🎨",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            text_content="Hello 世界 🌍 <script>alert('xss')</script>",
            attributes={"data-emoji": "🚀", "data-chinese": "你好"},
        )
        assert "🎨" in element.element_id
        assert "世界" in element.text_content
        assert element.attributes["data-emoji"] == "🚀"

    def test_null_and_empty_values(self):
        """Test handling of null and empty values"""
        element = ElementData(
            element_id="minimal",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            text_content=None,
            inner_html=None,
            value=None,
            bounding_box=None,
            computed_style=None,
            accessibility=None,
        )
        assert element.text_content is None
        assert element.bounding_box is None
        assert element.accessibility is None

    def test_circular_reference_prevention(self):
        """Test prevention of circular references"""
        # Parent-child circular reference should be prevented
        with pytest.raises(Exception):
            ElementData(
                element_id="elem1",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
                parent_id="elem2",
                children_ids=["elem1"],  # Self-reference
            )

    def test_extreme_coordinate_values(self):
        """Test extreme coordinate values"""
        # Very large coordinates
        bbox = BoundingBox(
            x=999999.99,
            y=999999.99,
            width=999999.99,
            height=999999.99,
        )
        assert bbox.area == 999999.99 * 999999.99
        
        # Very small but valid coordinates
        bbox_small = BoundingBox(
            x=0.000001,
            y=0.000001,
            width=0.000001,
            height=0.000001,
        )
        assert bbox_small.area > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])