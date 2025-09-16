"""
Element extractor for web automation
"""
from typing import List, Dict, Any
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)


async def extract_elements_from_url(url: str) -> List[Dict[str, Any]]:
    """
    Extract interactive elements from a webpage
    """
    elements = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle")
            
            # Extract buttons
            buttons = await page.query_selector_all("button, input[type='submit'], input[type='button']")
            for button in buttons:
                text = await button.text_content()
                element_id = await button.get_attribute("id")
                classes = await button.get_attribute("class")
                
                elements.append({
                    "type": "button",
                    "text": text or "",
                    "id": element_id or "",
                    "classes": classes or "",
                    "selector": f"button:has-text('{text}')" if text else f"#{element_id}" if element_id else ""
                })
            
            # Extract links
            links = await page.query_selector_all("a[href]")
            for link in links[:10]:  # Limit to 10 links
                text = await link.text_content()
                href = await link.get_attribute("href")
                
                elements.append({
                    "type": "link",
                    "text": text or "",
                    "href": href or "",
                    "selector": f"a:has-text('{text}')" if text else ""
                })
            
            # Extract input fields
            inputs = await page.query_selector_all("input[type='text'], input[type='email'], input[type='password'], textarea")
            for input_field in inputs:
                input_id = await input_field.get_attribute("id")
                name = await input_field.get_attribute("name")
                placeholder = await input_field.get_attribute("placeholder")
                
                elements.append({
                    "type": "input",
                    "id": input_id or "",
                    "name": name or "",
                    "placeholder": placeholder or "",
                    "selector": f"#{input_id}" if input_id else f"input[name='{name}']" if name else ""
                })
            
            # Extract forms
            forms = await page.query_selector_all("form")
            for idx, form in enumerate(forms):
                form_id = await form.get_attribute("id")
                action = await form.get_attribute("action")
                
                elements.append({
                    "type": "form",
                    "id": form_id or f"form_{idx}",
                    "action": action or "",
                    "selector": f"#{form_id}" if form_id else f"form:nth-of-type({idx + 1})"
                })
            
        finally:
            await browser.close()
    
    return elements