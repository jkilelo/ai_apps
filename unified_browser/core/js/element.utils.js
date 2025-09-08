/**
 * Utility functions for element detection and interaction
 */

// Check if an element is truly visible
function isElementVisible(element) {
    if (!element) return false;
    
    const style = window.getComputedStyle(element);
    if (style.display === 'none' || 
        style.visibility === 'hidden' || 
        parseFloat(style.opacity) < 0.1) {
        return false;
    }
    
    const rect = element.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) {
        return false;
    }
    
    // Check if in viewport with buffer
    const buffer = 50;
    const inViewport = (
        rect.top >= -buffer &&
        rect.left >= -buffer &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + buffer &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) + buffer
    );
    
    return inViewport;
}

// Check if element is interactive
function isInteractive(element) {
    const tag = element.tagName.toLowerCase();
    const role = element.getAttribute('role');
    const tabIndex = element.getAttribute('tabindex');
    
    // Check if it's a naturally interactive element
    const interactiveTags = [
        'a', 'button', 'input', 'select', 'textarea', 
        'details', 'summary', 'option', 'label'
    ];
    if (interactiveTags.includes(tag)) return true;
    
    // Check ARIA roles
    const interactiveRoles = [
        'button', 'link', 'checkbox', 'radio', 
        'textbox', 'combobox', 'menuitem', 'tab',
        'switch', 'slider', 'searchbox'
    ];
    if (role && interactiveRoles.includes(role)) return true;
    
    // Check if it has click handlers
    if (element.onclick || 
        element.getAttribute('onclick') ||
        element.hasAttribute('ng-click') ||
        element.hasAttribute('@click') ||
        element.hasAttribute('v-on:click')) {
        return true;
    }
    
    // Check if it's focusable
    if (tabIndex !== null && tabIndex !== '-1') return true;
    
    // Check for cursor pointer
    const style = window.getComputedStyle(element);
    if (style.cursor === 'pointer') return true;
    
    // Check for contenteditable
    if (element.contentEditable === 'true') return true;
    
    return false;
}

// Extract clean text from element
function getCleanText(element) {
    let text = '';
    
    // Try aria-label first
    const ariaLabel = element.getAttribute('aria-label');
    if (ariaLabel) return ariaLabel.trim();
    
    // Try value for inputs
    if (element.value !== undefined && element.value !== null) {
        return String(element.value).trim();
    }
    
    // Try alt text for images
    if (element.alt) return element.alt.trim();
    
    // Try placeholder
    if (element.placeholder) return element.placeholder.trim();
    
    // Try title
    if (element.title) return element.title.trim();
    
    // Get text content
    text = element.textContent || element.innerText || '';
    
    // Clean up whitespace
    return text.replace(/\s+/g, ' ').trim().substring(0, 100);
}

// Wait for element to appear
function waitForElement(selector, timeout = 10000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const checkElement = () => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                return;
            }
            
            if (Date.now() - startTime > timeout) {
                reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                return;
            }
            
            requestAnimationFrame(checkElement);
        };
        
        checkElement();
    });
}

// Get element by XPath
function getElementByXPath(xpath) {
    const result = document.evaluate(
        xpath,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    );
    return result.singleNodeValue;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isElementVisible,
        isInteractive,
        getCleanText,
        waitForElement,
        getElementByXPath
    };
}