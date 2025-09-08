"""DOM processing and simplification for perception"""

from bs4 import BeautifulSoup, NavigableString, Tag
from typing import List, Dict, Any, Optional, Set, Tuple
from loguru import logger
import re
from .models import ElementType, InteractiveElement, DOMStructure


class DOMProcessor:
    """Processes and distills HTML DOM into simplified representations"""
    
    # Tags to extract for interactive elements
    INTERACTIVE_TAGS = {
        'button', 'a', 'input', 'select', 'textarea', 
        'video', 'audio', 'iframe', 'form'
    }
    
    # Tags with semantic content
    CONTENT_TAGS = {
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'span', 'div', 'li', 'td', 'th',
        'label', 'caption', 'article', 'section',
        'main', 'nav', 'aside', 'header', 'footer'
    }
    
    # Tags to completely remove
    REMOVE_TAGS = {
        'script', 'style', 'meta', 'link', 'noscript',
        'svg', 'path', 'defs', 'symbol'
    }
    
    # Attributes to preserve
    PRESERVE_ATTRIBUTES = {
        'id', 'class', 'name', 'value', 'href', 'src',
        'alt', 'title', 'placeholder', 'type', 'role',
        'aria-label', 'aria-describedby', 'data-testid',
        'for', 'checked', 'selected', 'disabled', 'readonly'
    }
    
    def __init__(self):
        self.element_counter = 0
        self.interactive_elements: List[InteractiveElement] = []
        self.element_map: Dict[int, str] = {}
    
    def process_html(self, raw_html: str) -> DOMStructure:
        """Process raw HTML into structured representation"""
        try:
            # Parse HTML
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            # Reset counters
            self.element_counter = 0
            self.interactive_elements = []
            self.element_map = {}
            
            # Remove unwanted tags
            self._remove_unwanted_tags(soup)
            
            # Extract structured information
            headings = self._extract_headings(soup)
            forms = self._extract_forms(soup)
            tables = self._extract_tables(soup)
            images = self._extract_images(soup)
            links = self._extract_links(soup)
            
            # Extract interactive elements
            self._extract_interactive_elements(soup)
            
            # Generate distilled content
            distilled_content = self._distill_to_markdown(soup)
            text_content = self._extract_text_content(soup)
            
            return DOMStructure(
                raw_html=None,  # Don't store raw HTML to save memory
                distilled_content=distilled_content,
                text_content=text_content,
                headings=headings,
                forms=forms,
                tables=tables,
                images=images,
                links=links
            )
            
        except Exception as e:
            logger.error(f"Failed to process HTML: {e}")
            return DOMStructure(
                distilled_content="Failed to process page content",
                text_content=""
            )
    
    def _remove_unwanted_tags(self, soup: BeautifulSoup) -> None:
        """Remove script, style, and other non-content tags"""
        for tag_name in self.REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract heading hierarchy"""
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    'level': str(level),  # Convert to string for Pydantic
                    'text': heading.get_text(strip=True),
                    'id': heading.get('id', ''),
                    'class': ' '.join(heading.get('class', []))
                })
        return headings
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form structures"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'id': form.get('id', ''),
                'fields': []
            }
            
            # Extract form fields
            for input_elem in form.find_all(['input', 'select', 'textarea']):
                field = {
                    'tag': input_elem.name,
                    'type': input_elem.get('type', 'text'),
                    'name': input_elem.get('name', ''),
                    'id': input_elem.get('id', ''),
                    'placeholder': input_elem.get('placeholder', ''),
                    'required': input_elem.has_attr('required'),
                    'value': input_elem.get('value', '')
                }
                form_data['fields'].append(field)
            
            forms.append(form_data)
        return forms
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract table structures"""
        tables = []
        for table in soup.find_all('table'):
            table_data = {
                'id': table.get('id', ''),
                'class': ' '.join(table.get('class', [])),
                'headers': [],
                'rows': []
            }
            
            # Extract headers
            for th in table.find_all('th'):
                table_data['headers'].append(th.get_text(strip=True))
            
            # Extract rows (limited to first 10)
            for tr in table.find_all('tr')[:10]:
                row = []
                for td in tr.find_all('td'):
                    row.append(td.get_text(strip=True))
                if row:
                    table_data['rows'].append(row)
            
            tables.append(table_data)
        return tables
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract image information"""
        images = []
        for img in soup.find_all('img'):
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'id': img.get('id', ''),
                'class': ' '.join(img.get('class', []))
            }
            if img_data['src']:  # Only include if src exists
                images.append(img_data)
        return images[:20]  # Limit to first 20 images
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract link information"""
        links = []
        for a in soup.find_all('a'):
            link_data = {
                'href': a.get('href', ''),
                'text': a.get_text(strip=True),
                'title': a.get('title', ''),
                'target': a.get('target', ''),
                'id': a.get('id', ''),
                'class': ' '.join(a.get('class', []))
            }
            if link_data['href']:  # Only include if href exists
                links.append(link_data)
        return links[:50]  # Limit to first 50 links
    
    def _extract_interactive_elements(self, soup: BeautifulSoup) -> None:
        """Extract all interactive elements"""
        # Find all interactive elements
        interactive_tags = soup.find_all(list(self.INTERACTIVE_TAGS))
        
        # Also find elements with onclick attributes
        onclick_elements = soup.find_all(attrs={'onclick': True})
        
        # Combine and deduplicate
        all_interactive = list(set(interactive_tags + onclick_elements))
        
        for element in all_interactive:
            if self._is_visible(element):
                self._create_interactive_element(element)
    
    def _is_visible(self, element: Tag) -> bool:
        """Check if element is likely visible"""
        # Check for hidden attributes
        if element.has_attr('hidden'):
            return False
        
        # Check style attribute
        style = element.get('style', '')
        if 'display:none' in style.replace(' ', '') or 'visibility:hidden' in style.replace(' ', ''):
            return False
        
        # Check for common hidden classes
        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = [classes]
        hidden_classes = {'hidden', 'd-none', 'invisible', 'hide'}
        if any(cls in hidden_classes for cls in classes):
            return False
        
        # Check if element has any visible content
        if element.name in ['input', 'button', 'select', 'textarea']:
            return True  # Form elements are interactive even without text
        
        # Check for text or nested interactive elements
        text = element.get_text(strip=True)
        return bool(text) or any(child.name in self.INTERACTIVE_TAGS for child in element.children if isinstance(child, Tag))
    
    def _create_interactive_element(self, element: Tag) -> None:
        """Create InteractiveElement from BeautifulSoup element"""
        self.element_counter += 1
        element_id = self.element_counter
        
        # Generate CSS selector
        selector = self._generate_css_selector(element)
        
        # Determine element type
        element_type = self._determine_element_type(element)
        
        # Extract attributes
        attributes = {}
        for attr in self.PRESERVE_ATTRIBUTES:
            if element.has_attr(attr):
                value = element.get(attr)
                if isinstance(value, list):
                    value = ' '.join(value)
                attributes[attr] = str(value)
        
        # Create InteractiveElement
        interactive_elem = InteractiveElement(
            id=element_id,
            selector=selector,
            type=element_type,
            tag_name=element.name,
            text=element.get_text(strip=True)[:200],  # Limit text length
            value=element.get('value', ''),
            placeholder=element.get('placeholder', ''),
            href=element.get('href', ''),
            attributes=attributes,
            is_visible=True,
            is_enabled=not element.has_attr('disabled'),
            is_checked=element.has_attr('checked') if element.name in ['input'] else None,
            aria_label=element.get('aria-label', ''),
            aria_role=element.get('role', '')
        )
        
        self.interactive_elements.append(interactive_elem)
        self.element_map[element_id] = selector
    
    def _generate_css_selector(self, element: Tag) -> str:
        """Generate CSS selector for element"""
        # Try ID first
        if element.has_attr('id'):
            return f"#{element['id']}"
        
        # Try unique class combination
        if element.has_attr('class'):
            classes = element['class']
            if isinstance(classes, str):
                classes = [classes]
            if classes:
                class_selector = '.' + '.'.join(classes)
                # Check if unique
                parent = element.parent
                if parent and len(parent.select(class_selector)) == 1:
                    return class_selector
        
        # Try data-testid
        if element.has_attr('data-testid'):
            return f"[data-testid='{element['data-testid']}']"
        
        # Fall back to nth-child
        return self._generate_nth_child_selector(element)
    
    def _generate_nth_child_selector(self, element: Tag) -> str:
        """Generate nth-child selector for element"""
        path_parts = []
        current = element
        
        while current and current.name != '[document]':
            if current.name:
                # Find position among siblings
                siblings = [s for s in current.parent.children if isinstance(s, Tag) and s.name == current.name]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    path_parts.append(f"{current.name}:nth-of-type({index})")
                else:
                    path_parts.append(current.name)
            
            current = current.parent
            
            # Stop at body or html
            if current and current.name in ['body', 'html']:
                break
        
        return ' > '.join(reversed(path_parts))
    
    def _determine_element_type(self, element: Tag) -> ElementType:
        """Determine the type of interactive element"""
        tag_name = element.name.lower()
        
        if tag_name == 'button':
            return ElementType.BUTTON
        elif tag_name == 'a':
            return ElementType.LINK
        elif tag_name == 'input':
            input_type = element.get('type', 'text').lower()
            if input_type in ['checkbox']:
                return ElementType.CHECKBOX
            elif input_type in ['radio']:
                return ElementType.RADIO
            else:
                return ElementType.INPUT
        elif tag_name == 'select':
            return ElementType.SELECT
        elif tag_name == 'textarea':
            return ElementType.TEXTAREA
        elif tag_name == 'img':
            return ElementType.IMAGE
        elif tag_name == 'video':
            return ElementType.VIDEO
        elif tag_name == 'iframe':
            return ElementType.IFRAME
        elif tag_name == 'form':
            return ElementType.FORM
        elif tag_name == 'table':
            return ElementType.TABLE
        else:
            return ElementType.OTHER
    
    def _distill_to_markdown(self, soup: BeautifulSoup) -> str:
        """Convert HTML to simplified markdown representation"""
        lines = []
        
        def process_element(element, depth=0):
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    lines.append(text)
            elif isinstance(element, Tag):
                # Handle different tags
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(element.name[1])
                    lines.append('')
                    lines.append('#' * level + ' ' + element.get_text(strip=True))
                    lines.append('')
                
                elif element.name == 'p':
                    lines.append('')
                    lines.append(element.get_text(strip=True))
                    lines.append('')
                
                elif element.name == 'a':
                    text = element.get_text(strip=True)
                    href = element.get('href', '#')
                    if text:
                        lines.append(f"[{text}]({href})")
                
                elif element.name == 'button':
                    text = element.get_text(strip=True)
                    if text:
                        lines.append(f"[Button: {text}]")
                
                elif element.name == 'input':
                    input_type = element.get('type', 'text')
                    placeholder = element.get('placeholder', '')
                    name = element.get('name', '')
                    lines.append(f"[Input ({input_type}): {name or placeholder}]")
                
                elif element.name == 'img':
                    alt = element.get('alt', 'Image')
                    lines.append(f"[Image: {alt}]")
                
                elif element.name in ['ul', 'ol']:
                    lines.append('')
                    for li in element.find_all('li', recursive=False):
                        lines.append('• ' + li.get_text(strip=True))
                    lines.append('')
                
                elif element.name == 'table':
                    lines.append('')
                    lines.append('[Table with ' + str(len(element.find_all('tr'))) + ' rows]')
                    lines.append('')
                
                elif element.name in ['div', 'section', 'article', 'main']:
                    # Process children
                    for child in element.children:
                        process_element(child, depth + 1)
                
                else:
                    # For other elements, just process children
                    for child in element.children:
                        process_element(child, depth + 1)
        
        # Process body or entire soup
        body = soup.body if soup.body else soup
        process_element(body)
        
        # Clean up and join lines
        markdown = '\n'.join(lines)
        
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        return markdown.strip()
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract plain text content"""
        # Get all text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text[:10000]  # Limit to 10k chars
    
    def get_interactive_elements(self) -> List[InteractiveElement]:
        """Get list of interactive elements found"""
        return self.interactive_elements
    
    def get_element_map(self) -> Dict[int, str]:
        """Get mapping from element ID to selector"""
        return self.element_map