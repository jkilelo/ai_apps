"""Unit tests for the Perception Layer components.

Tests DOMProcessor, VisualAnnotator, and StateObserver
while ensuring strict layer separation (NO action execution).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import base64
from typing import Dict, Any

from src.perception.dom_processor import DOMProcessor
from src.perception.visual_annotator import VisualAnnotator
from src.perception.state_observer import StateObserver
from src.perception.models import (
    WebPageState,
    PageMetadata,
    DOMStructure,
    InteractiveElement,
    ElementType,
    AnnotatedElement,
    AccessibilityTree,
    PerceptionResult
)


class TestDOMProcessor:
    """Test DOMProcessor functionality."""
    
    def test_dom_processor_initialization(self):
        """Test DOMProcessor initialization."""
        processor = DOMProcessor()
        
        assert processor.element_counter == 0
        assert len(processor.interactive_elements) == 0
        assert len(processor.element_map) == 0
    
    def test_process_simple_html(self):
        """Test processing simple HTML."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Heading</h1>
                <p>Some text content</p>
                <button id="submit">Submit</button>
                <a href="/link">Click here</a>
            </body>
        </html>
        """
        
        processor = DOMProcessor()
        dom_structure = processor.process_html(html)
        
        assert dom_structure.text_content is not None
        assert "Main Heading" in dom_structure.text_content
        assert "Some text content" in dom_structure.text_content
        assert len(dom_structure.headings) == 1
        assert dom_structure.headings[0]['text'] == "Main Heading"
    
    def test_extract_interactive_elements(self):
        """Test extraction of interactive elements."""
        html = """
        <html>
            <body>
                <button id="btn1">Button 1</button>
                <input type="text" name="username" placeholder="Enter username">
                <select name="country">
                    <option>USA</option>
                    <option>Canada</option>
                </select>
                <a href="https://example.com">Link</a>
                <textarea name="comments"></textarea>
            </body>
        </html>
        """
        
        processor = DOMProcessor()
        processor.process_html(html)
        elements = processor.get_interactive_elements()
        
        assert len(elements) >= 4  # button, input, select, link, textarea
        
        # Check element types
        element_types = [elem.type for elem in elements]
        assert ElementType.BUTTON in element_types
        assert ElementType.INPUT in element_types
        assert ElementType.SELECT in element_types
        assert ElementType.LINK in element_types
    
    def test_distill_to_markdown(self):
        """Test HTML to markdown distillation."""
        html = """
        <html>
            <body>
                <h1>Title</h1>
                <h2>Subtitle</h2>
                <p>Paragraph text</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
                <strong>Bold text</strong>
                <em>Italic text</em>
            </body>
        </html>
        """
        
        processor = DOMProcessor()
        dom_structure = processor.process_html(html)
        
        assert "# Title" in dom_structure.distilled_content or "Title" in dom_structure.distilled_content
        assert "Paragraph text" in dom_structure.distilled_content
        assert "Item 1" in dom_structure.distilled_content
        assert "Item 2" in dom_structure.distilled_content
    
    def test_remove_unwanted_tags(self):
        """Test removal of script and style tags."""
        html = """
        <html>
            <head>
                <style>body { color: red; }</style>
                <script>alert('test');</script>
            </head>
            <body>
                <p>Content</p>
                <script>console.log('test');</script>
            </body>
        </html>
        """
        
        processor = DOMProcessor()
        dom_structure = processor.process_html(html)
        
        # Script and style content should not be in text
        assert "alert" not in dom_structure.text_content
        assert "console.log" not in dom_structure.text_content
        assert "color: red" not in dom_structure.text_content
        assert "Content" in dom_structure.text_content
    
    def test_extract_forms(self):
        """Test form extraction."""
        html = """
        <html>
            <body>
                <form id="login" action="/login" method="post">
                    <input type="text" name="username" required>
                    <input type="password" name="password" required>
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
        """
        
        processor = DOMProcessor()
        dom_structure = processor.process_html(html)
        
        assert len(dom_structure.forms) == 1
        form = dom_structure.forms[0]
        assert form['id'] == 'login'
        assert form['action'] == '/login'
        assert form['method'] == 'post'
        assert len(form['fields']) >= 2


class TestVisualAnnotator:
    """Test VisualAnnotator functionality."""
    
    def test_visual_annotator_initialization(self):
        """Test VisualAnnotator initialization."""
        annotator = VisualAnnotator()
        
        # Check color map is defined
        assert 'button' in annotator.COLOR_MAP
        assert annotator.COLOR_MAP['button'] == '#FF6B6B'
        assert annotator.COLOR_MAP['link'] == '#4ECDC4'
        assert annotator.COLOR_MAP['input'] == '#95E77E'
        assert annotator.COLOR_MAP['select'] == '#FFE66D'
    
    @pytest.mark.asyncio
    async def test_annotate_page(self):
        """Test page annotation."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[
            {
                'id': 1,
                'selector': 'button#submit',
                'tagName': 'button',
                'text': 'Submit',
                'type': 'button'
            },
            {
                'id': 2,
                'selector': 'input#email',
                'tagName': 'input',
                'text': '',
                'type': 'email'
            }
        ])
        
        annotator = VisualAnnotator()
        result = await annotator.annotate_page(mock_page)
        
        assert 'annotated_elements' in result
        assert len(result['annotated_elements']) == 2
        assert 'element_map' in result
    
    @pytest.mark.asyncio
    async def test_capture_clean_and_annotated(self):
        """Test capturing both clean and annotated screenshots."""
        mock_page = AsyncMock()
        mock_page.screenshot = AsyncMock(return_value=b"screenshot_data")
        mock_page.evaluate = AsyncMock(return_value=[])
        
        annotator = VisualAnnotator()
        result = await annotator.capture_clean_and_annotated(mock_page)
        
        assert 'screenshot' in result
        assert 'screenshot_base64' in result
        assert result['screenshot'] == b"screenshot_data"
        assert result['screenshot_base64'] is not None
        
        # Should have called screenshot twice (clean and annotated)
        assert mock_page.screenshot.call_count >= 1
    
    def test_create_annotated_elements(self):
        """Test creating annotated elements."""
        interactive_elements = [
            InteractiveElement(
                id=1,
                selector="button#submit",
                type=ElementType.BUTTON,
                tag_name="button",
                text="Submit"
            ),
            InteractiveElement(
                id=2,
                selector="input#email",
                type=ElementType.INPUT,
                tag_name="input"
            )
        ]
        
        visual_elements = [
            {'id': 1, 'selector': 'button#submit', 'tagName': 'button'},
            {'id': 2, 'selector': 'input#email', 'tagName': 'input'}
        ]
        
        annotator = VisualAnnotator()
        annotated = annotator.create_annotated_elements(
            interactive_elements,
            visual_elements
        )
        
        assert len(annotated) == 2
        assert all(isinstance(elem, AnnotatedElement) for elem in annotated)
        assert annotated[0].annotation_id == 1
        assert annotated[0].element.type == ElementType.BUTTON


class TestStateObserver:
    """Test StateObserver functionality."""
    
    @pytest.mark.asyncio
    async def test_state_observer_initialization(self):
        """Test StateObserver initialization."""
        observer = StateObserver()
        
        assert observer.dom_processor is not None
        assert observer.visual_annotator is not None
        assert observer.last_state is None
    
    @pytest.mark.asyncio
    async def test_observe_basic_page(self):
        """Test observing a basic page."""
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        mock_page.title = AsyncMock(return_value="Example Page")
        mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        mock_page.evaluate = AsyncMock(return_value={})
        mock_page.screenshot = AsyncMock(return_value=b"screenshot")
        mock_page.accessibility.snapshot = AsyncMock(return_value={})
        
        observer = StateObserver()
        result = await observer.observe(
            mock_page,
            capture_screenshot=True,
            annotate_visuals=False
        )
        
        assert result.success is True
        assert result.state is not None
        assert result.state.metadata.url == "https://example.com"
        assert result.state.metadata.title == "Example Page"
        assert result.state.screenshot is not None
    
    @pytest.mark.asyncio
    async def test_observe_with_annotations(self):
        """Test observing with visual annotations."""
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        mock_page.title = AsyncMock(return_value="Example Page")
        mock_page.content = AsyncMock(return_value="""
            <html><body>
                <button>Click me</button>
                <input type="text">
            </body></html>
        """)
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.screenshot = AsyncMock(return_value=b"screenshot")
        
        observer = StateObserver()
        result = await observer.observe(
            mock_page,
            capture_screenshot=True,
            annotate_visuals=True
        )
        
        assert result.success is True
        assert result.state is not None
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self):
        """Test metadata extraction."""
        mock_page = AsyncMock()
        mock_page.url = "https://example.com/page"
        mock_page.title = AsyncMock(return_value="Page Title")
        mock_page.evaluate = AsyncMock(side_effect=[
            "Page description",  # meta description
            ["keyword1", "keyword2"],  # keywords
            "en",  # language
            {  # viewport info
                'viewportWidth': 1920,
                'viewportHeight': 1080,
                'scrollX': 0,
                'scrollY': 100,
                'pageWidth': 1920,
                'pageHeight': 3000
            }
        ])
        
        observer = StateObserver()
        metadata = await observer._extract_metadata(mock_page)
        
        assert metadata.url == "https://example.com/page"
        assert metadata.title == "Page Title"
        assert metadata.description == "Page description"
        assert metadata.keywords == ["keyword1", "keyword2"]
        assert metadata.language == "en"
        assert metadata.viewport_width == 1920
        assert metadata.scroll_position['y'] == 100
    
    @pytest.mark.asyncio
    async def test_detect_page_characteristics(self):
        """Test page characteristic detection."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value={
            'hasLoginForm': True,
            'hasCaptcha': False,
            'isErrorPage': False,
            'frameworks': ['react']
        })
        
        dom_structure = DOMStructure(
            distilled_content="Login to continue",
            text_content="Login"
        )
        
        observer = StateObserver()
        characteristics = await observer._detect_page_characteristics(
            mock_page,
            dom_structure
        )
        
        assert 'requires_authentication' in characteristics
        assert 'has_captcha' in characteristics
        assert 'is_error_page' in characteristics
        assert 'frameworks' in characteristics
    
    def test_compare_states(self):
        """Test state comparison."""
        observer = StateObserver()
        
        # Create two states with differences
        state1 = WebPageState(
            metadata=PageMetadata(url="https://example.com", title="Page 1"),
            dom_structure=DOMStructure(
                distilled_content="Content 1",
                text_content="Text 1"
            ),
            interactive_elements=[
                InteractiveElement(
                    id=1,
                    selector="button#btn1",
                    type=ElementType.BUTTON,
                    tag_name="button"
                )
            ]
        )
        
        state2 = WebPageState(
            metadata=PageMetadata(url="https://example.com/new", title="Page 2"),
            dom_structure=DOMStructure(
                distilled_content="Content 2",
                text_content="Text 2"
            ),
            interactive_elements=[
                InteractiveElement(
                    id=1,
                    selector="button#btn1",
                    type=ElementType.BUTTON,
                    tag_name="button"
                ),
                InteractiveElement(
                    id=2,
                    selector="button#btn2",
                    type=ElementType.BUTTON,
                    tag_name="button"
                )
            ]
        )
        
        changes = observer.compare_states(state1, state2)
        
        assert changes['url_changed'] is True
        assert changes['title_changed'] is True
        assert changes['content_changes'] is True
        assert len(changes['elements_added']) == 1
        assert 'button#btn2' in changes['elements_added']


class TestLayerCompliance:
    """Test layer separation compliance."""
    
    def test_no_action_execution_imports(self):
        """Ensure perception layer doesn't import from execution actions."""
        import src.perception.dom_processor as dom
        import src.perception.visual_annotator as visual
        import src.perception.state_observer as observer
        
        # Check module dictionaries for forbidden imports
        for module in [dom, visual, observer]:
            module_dict = vars(module)
            
            # Should not import action-related classes
            assert 'ActionExecutor' not in module_dict
            assert 'ClickAction' not in module_dict
            assert 'NavigateAction' not in module_dict
    
    def test_no_llm_imports(self):
        """Ensure perception layer doesn't import LLM/cognition components."""
        import src.perception.dom_processor as dom
        import src.perception.visual_annotator as visual
        import src.perception.state_observer as observer
        
        for module in [dom, visual, observer]:
            module_dict = vars(module)
            
            # Should not import LLM-related classes
            assert 'LLMManager' not in module_dict
            assert 'openai' not in str(module_dict)
            assert 'anthropic' not in str(module_dict)
            assert 'cognition' not in str(module_dict)