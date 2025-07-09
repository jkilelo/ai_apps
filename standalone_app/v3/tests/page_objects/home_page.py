"""
Home page object
"""
from playwright.async_api import Page, Locator
from .base_page import BasePage


class HomePage(BasePage):
    """Page object for Home page"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = ""
        
    # Page elements
    @property
    def hero_section(self) -> Locator:
        return self.page.locator(".hero-section")
        
    @property
    def hero_title(self) -> Locator:
        return self.page.locator(".hero-title")
        
    @property
    def hero_subtitle(self) -> Locator:
        return self.page.locator(".hero-subtitle")
        
    @property
    def features_grid(self) -> Locator:
        return self.page.locator(".features-grid")
        
    @property
    def feature_cards(self) -> Locator:
        return self.page.locator(".feature-card")
        
    @property
    def get_started_button(self) -> Locator:
        return self.page.locator("button[data-action='get-started']")
        
    @property
    def cta_section(self) -> Locator:
        return self.page.locator(".cta-section")
        
    # Page actions
    async def navigate(self):
        """Navigate to home page"""
        await self.navigate_to(self.path)
        await self.wait_for_hero_section()
        
    async def wait_for_hero_section(self):
        """Wait for hero section to be visible"""
        await self.hero_section.wait_for(state="visible", timeout=self.timeout)
        
    async def get_hero_title_text(self) -> str:
        """Get hero title text"""
        return await self.hero_title.text_content()
        
    async def get_hero_subtitle_text(self) -> str:
        """Get hero subtitle text"""
        return await self.hero_subtitle.text_content()
        
    async def get_feature_count(self) -> int:
        """Get number of feature cards"""
        return await self.feature_cards.count()
        
    async def get_feature_titles(self) -> list[str]:
        """Get all feature card titles"""
        titles = []
        count = await self.feature_cards.count()
        
        for i in range(count):
            card = self.feature_cards.nth(i)
            title = await card.locator("h3").text_content()
            titles.append(title)
            
        return titles
        
    async def get_feature_descriptions(self) -> list[str]:
        """Get all feature card descriptions"""
        descriptions = []
        count = await self.feature_cards.count()
        
        for i in range(count):
            card = self.feature_cards.nth(i)
            desc = await card.locator("p").text_content()
            descriptions.append(desc)
            
        return descriptions
        
    async def click_get_started(self):
        """Click Get Started button"""
        await self.get_started_button.click()
        await self.wait_for_load()
        
    async def is_get_started_visible(self) -> bool:
        """Check if Get Started button is visible"""
        return await self.get_started_button.is_visible()
        
    async def hover_feature_card(self, index: int):
        """Hover over specific feature card"""
        card = self.feature_cards.nth(index)
        await card.hover()
        await self.page.wait_for_timeout(200)  # Wait for hover animation
        
    async def verify_page_structure(self):
        """Verify all expected elements are present"""
        # Hero section
        assert await self.hero_section.is_visible(), "Hero section not visible"
        assert await self.hero_title.is_visible(), "Hero title not visible"
        assert await self.hero_subtitle.is_visible(), "Hero subtitle not visible"
        
        # Features
        assert await self.features_grid.is_visible(), "Features grid not visible"
        feature_count = await self.get_feature_count()
        assert feature_count == 3, f"Expected 3 feature cards, found {feature_count}"
        
        # CTA
        assert await self.cta_section.is_visible(), "CTA section not visible"
        assert await self.get_started_button.is_visible(), "Get Started button not visible"
        
    async def verify_responsive_layout(self):
        """Verify responsive layout behavior"""
        viewport = await self.get_viewport_size()
        
        if viewport["width"] < 768:
            # Mobile layout
            # Features should stack vertically
            grid_styles = await self.features_grid.evaluate("""
                el => window.getComputedStyle(el).gridTemplateColumns
            """)
            assert "1fr" in grid_styles, "Features should stack on mobile"
        else:
            # Desktop layout
            # Features should be in grid
            grid_styles = await self.features_grid.evaluate("""
                el => window.getComputedStyle(el).gridTemplateColumns
            """)
            assert "repeat" in grid_styles, "Features should be in grid on desktop"
            
    async def test_animations(self):
        """Test page animations"""
        # Check if elements have animation classes
        hero_classes = await self.hero_section.get_attribute("class")
        
        # Scroll to trigger any scroll animations
        await self.scroll_to_element(".features-grid")
        await self.page.wait_for_timeout(1000)  # Wait for animations
        
        # Check feature cards have appeared
        for i in range(await self.feature_cards.count()):
            card = self.feature_cards.nth(i)
            opacity = await card.evaluate("el => window.getComputedStyle(el).opacity")
            assert float(opacity) == 1.0, f"Feature card {i} not fully visible"