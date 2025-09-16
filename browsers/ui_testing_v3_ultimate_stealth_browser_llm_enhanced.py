#!/usr/bin/env python3
"""
Enhanced Ultimate Stealth Browser with LLM-Optimized Element Extraction

This module extends the ultimate_stealth_browser.py with additional extraction
capabilities specifically designed to provide rich context for LLM test generation.

Key Enhancements:
1. Semantic analysis of element purpose and business context
2. Hierarchical relationship extraction
3. Form field grouping and validation rule detection
4. Enhanced accessibility data extraction
5. Interaction pattern detection
6. Page-level context and user journey mapping
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import hashlib
from datetime import datetime

# Import the LLM-optimized structure
from ui_testing_v3.llm_optimized_element_structure import (
    LLMOptimizedElement,
    ElementCategory,
    InteractionPattern,
    TestPriority,
    ValidationRule,
    SemanticContext,
    InteractionContext,
    ValidationContext,
    AccessibilityContext,
    HierarchicalContext,
    VisualContext,
    StateContext,
    PageStructure
)

# Import base browser functionality
from ultimate_stealth_browser import (
    UltimateStealthBrowser,
    StealthConfig,
    ElementData,
    ExtractionResult
)


class LLMEnhancedExtractionStrategy:
    """Enhanced extraction strategy that captures rich context for LLM test generation"""
    
    @staticmethod
    async def extract_with_llm_context(page, config) -> Dict[str, Any]:
        """
        Extract elements with comprehensive context for LLM test generation.
        This is the main enhancement over the basic extraction.
        """
        
        extraction_script = """
        () => {
            // Helper function to get element's semantic role
            const getSemanticRole = (element) => {
                // Check for explicit semantic HTML5 tags
                const semanticTags = {
                    'nav': 'navigation',
                    'header': 'header',
                    'footer': 'footer',
                    'main': 'main_content',
                    'article': 'article',
                    'section': 'section',
                    'aside': 'sidebar',
                    'form': 'form',
                    'search': 'search'
                };
                
                if (semanticTags[element.tagName.toLowerCase()]) {
                    return semanticTags[element.tagName.toLowerCase()];
                }
                
                // Check ARIA roles
                if (element.role) {
                    return element.role;
                }
                
                // Infer from class names and IDs
                const classAndId = (element.className + ' ' + element.id).toLowerCase();
                if (classAndId.includes('nav')) return 'navigation';
                if (classAndId.includes('header')) return 'header';
                if (classAndId.includes('footer')) return 'footer';
                if (classAndId.includes('sidebar')) return 'sidebar';
                if (classAndId.includes('modal')) return 'modal';
                if (classAndId.includes('search')) return 'search';
                if (classAndId.includes('login') || classAndId.includes('signin')) return 'authentication';
                if (classAndId.includes('signup') || classAndId.includes('register')) return 'registration';
                if (classAndId.includes('cart')) return 'shopping_cart';
                if (classAndId.includes('checkout') || classAndId.includes('payment')) return 'payment';
                
                return null;
            };
            
            // Helper function to detect business context
            const getBusinessContext = (element) => {
                const text = (element.textContent || '').toLowerCase();
                const context = {
                    isAuthentication: false,
                    isPayment: false,
                    isSearch: false,
                    isNavigation: false,
                    isForm: false,
                    isDataEntry: false,
                    businessFunction: null
                };
                
                // Authentication context
                if (text.match(/log\\s*in|sign\\s*in|log\\s*out|sign\\s*out|password|username|email/i)) {
                    context.isAuthentication = true;
                    context.businessFunction = 'authentication';
                }
                
                // Payment context
                if (text.match(/pay|checkout|cart|card|billing|shipping|order/i)) {
                    context.isPayment = true;
                    context.businessFunction = 'payment_processing';
                }
                
                // Search context
                if (element.type === 'search' || text.match(/search|find|filter/i)) {
                    context.isSearch = true;
                    context.businessFunction = 'search_and_discovery';
                }
                
                // Form context
                if (element.tagName === 'FORM' || element.form) {
                    context.isForm = true;
                    context.isDataEntry = true;
                    
                    // Determine form type
                    const formText = element.form ? element.form.textContent : element.textContent;
                    if (formText.match(/contact/i)) context.businessFunction = 'contact_form';
                    if (formText.match(/subscribe|newsletter/i)) context.businessFunction = 'subscription';
                    if (formText.match(/feedback|review/i)) context.businessFunction = 'feedback';
                }
                
                return context;
            };
            
            // Helper function to extract validation rules
            const getValidationRules = (element) => {
                const rules = {
                    required: element.required || element.getAttribute('aria-required') === 'true',
                    pattern: element.pattern,
                    minLength: element.minLength || element.getAttribute('minlength'),
                    maxLength: element.maxLength || element.getAttribute('maxlength'),
                    min: element.min,
                    max: element.max,
                    step: element.step,
                    type: element.type,
                    autocomplete: element.autocomplete,
                    customValidation: []
                };
                
                // Check for data attributes that might contain validation rules
                for (let attr of element.attributes) {
                    if (attr.name.startsWith('data-val')) {
                        rules.customValidation.push({
                            attribute: attr.name,
                            value: attr.value
                        });
                    }
                }
                
                return rules;
            };
            
            // Helper function to get element hierarchy
            const getElementHierarchy = (element) => {
                const hierarchy = {
                    parentForm: null,
                    parentSection: null,
                    parentContainer: null,
                    siblings: [],
                    children: [],
                    depth: 0,
                    breadcrumb: []
                };
                
                // Find parent form
                const form = element.closest('form');
                if (form) {
                    hierarchy.parentForm = {
                        id: form.id,
                        name: form.name,
                        action: form.action,
                        method: form.method
                    };
                }
                
                // Find semantic parent
                const semanticParents = ['section', 'article', 'nav', 'aside', 'main', 'header', 'footer'];
                for (let tag of semanticParents) {
                    const parent = element.closest(tag);
                    if (parent) {
                        hierarchy.parentSection = {
                            tag: parent.tagName.toLowerCase(),
                            id: parent.id,
                            className: parent.className,
                            role: getSemanticRole(parent)
                        };
                        break;
                    }
                }
                
                // Get siblings (only interactive elements)
                if (element.parentElement) {
                    const interactiveTags = ['input', 'button', 'select', 'textarea', 'a'];
                    const siblings = Array.from(element.parentElement.children);
                    hierarchy.siblings = siblings
                        .filter(sib => sib !== element && interactiveTags.includes(sib.tagName.toLowerCase()))
                        .slice(0, 5)  // Limit to 5 siblings
                        .map(sib => ({
                            tag: sib.tagName.toLowerCase(),
                            id: sib.id,
                            text: (sib.textContent || '').substring(0, 50)
                        }));
                }
                
                // Get children (for containers)
                if (element.children.length > 0) {
                    hierarchy.children = Array.from(element.children)
                        .slice(0, 10)  // Limit to 10 children
                        .map(child => ({
                            tag: child.tagName.toLowerCase(),
                            id: child.id,
                            className: child.className
                        }));
                }
                
                // Build breadcrumb
                let current = element;
                while (current && current !== document.body && hierarchy.depth < 10) {
                    hierarchy.breadcrumb.unshift({
                        tag: current.tagName.toLowerCase(),
                        id: current.id,
                        className: current.className
                    });
                    current = current.parentElement;
                    hierarchy.depth++;
                }
                
                return hierarchy;
            };
            
            // Helper function to detect interaction patterns
            const getInteractionPatterns = (element) => {
                const patterns = [];
                const tag = element.tagName.toLowerCase();
                const type = element.type || '';
                
                // Click patterns
                if (tag === 'button' || tag === 'a' || element.onclick || element.role === 'button') {
                    patterns.push('click');
                }
                
                // Text input patterns
                if (tag === 'input' && ['text', 'email', 'password', 'tel', 'url', 'search'].includes(type)) {
                    patterns.push('type_text');
                }
                
                // Selection patterns
                if (tag === 'select' || (tag === 'input' && type === 'checkbox') || (tag === 'input' && type === 'radio')) {
                    patterns.push('select_option');
                }
                
                // File upload
                if (tag === 'input' && type === 'file') {
                    patterns.push('upload_file');
                }
                
                // Drag and drop
                if (element.draggable || element.ondragstart) {
                    patterns.push('drag_drop');
                }
                
                // Hover interactions
                if (element.matches(':hover') || window.getComputedStyle(element, ':hover')) {
                    patterns.push('hover');
                }
                
                // Keyboard shortcuts
                if (element.accessKey) {
                    patterns.push('keyboard_shortcut');
                }
                
                return patterns;
            };
            
            // Helper function to extract accessibility context
            const getAccessibilityContext = (element) => {
                return {
                    // ARIA attributes
                    ariaRole: element.getAttribute('role'),
                    ariaLabel: element.getAttribute('aria-label'),
                    ariaLabelledBy: element.getAttribute('aria-labelledby'),
                    ariaDescribedBy: element.getAttribute('aria-describedby'),
                    ariaLive: element.getAttribute('aria-live'),
                    ariaHidden: element.getAttribute('aria-hidden'),
                    ariaExpanded: element.getAttribute('aria-expanded'),
                    ariaSelected: element.getAttribute('aria-selected'),
                    ariaChecked: element.getAttribute('aria-checked'),
                    ariaDisabled: element.getAttribute('aria-disabled'),
                    ariaValueNow: element.getAttribute('aria-valuenow'),
                    ariaValueMin: element.getAttribute('aria-valuemin'),
                    ariaValueMax: element.getAttribute('aria-valuemax'),
                    
                    // Keyboard navigation
                    tabIndex: element.tabIndex,
                    accessKey: element.accessKey,
                    
                    // Labels and descriptions
                    label: (() => {
                        // Try to find associated label
                        if (element.id) {
                            const label = document.querySelector(`label[for="${element.id}"]`);
                            if (label) return label.textContent;
                        }
                        // Check if element is inside a label
                        const parentLabel = element.closest('label');
                        if (parentLabel) return parentLabel.textContent;
                        
                        return null;
                    })(),
                    
                    // Focus management
                    isFocusable: element.tabIndex >= 0,
                    hasFocusWithin: element.matches(':focus-within'),
                    
                    // Semantic HTML
                    isSemanticHTML: ['nav', 'main', 'header', 'footer', 'article', 'section', 'aside'].includes(element.tagName.toLowerCase())
                };
            };
            
            // Helper function to get visual context
            const getVisualContext = (element) => {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                
                return {
                    // Position and dimensions
                    position: {
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        top: Math.round(rect.top),
                        left: Math.round(rect.left),
                        bottom: Math.round(rect.bottom),
                        right: Math.round(rect.right)
                    },
                    
                    // Visibility
                    visibility: {
                        isVisible: rect.width > 0 && rect.height > 0 && styles.visibility !== 'hidden' && styles.display !== 'none',
                        isAboveFold: rect.top < window.innerHeight,
                        isBelowFold: rect.top >= window.innerHeight,
                        isInViewport: rect.top < window.innerHeight && rect.bottom > 0,
                        opacity: styles.opacity,
                        zIndex: styles.zIndex
                    },
                    
                    // Styling
                    styling: {
                        backgroundColor: styles.backgroundColor,
                        color: styles.color,
                        fontSize: styles.fontSize,
                        fontWeight: styles.fontWeight,
                        border: styles.border,
                        borderRadius: styles.borderRadius,
                        boxShadow: styles.boxShadow,
                        cursor: styles.cursor
                    },
                    
                    // Responsive
                    responsive: {
                        isResponsive: styles.width.includes('%') || styles.width.includes('vw'),
                        breakpoint: (() => {
                            const width = window.innerWidth;
                            if (width < 576) return 'xs';
                            if (width < 768) return 'sm';
                            if (width < 992) return 'md';
                            if (width < 1200) return 'lg';
                            return 'xl';
                        })()
                    }
                };
            };
            
            // Helper function to detect form field relationships
            const getFormFieldRelationships = (element) => {
                const relationships = {
                    fieldGroup: null,
                    fieldset: null,
                    relatedFields: [],
                    dependentFields: [],
                    validationGroup: null
                };
                
                // Check if element is in a fieldset
                const fieldset = element.closest('fieldset');
                if (fieldset) {
                    relationships.fieldset = {
                        legend: fieldset.querySelector('legend')?.textContent,
                        disabled: fieldset.disabled
                    };
                }
                
                // Check for field groups (common parent containers)
                const formGroup = element.closest('.form-group, .field-group, .input-group, [role="group"]');
                if (formGroup) {
                    relationships.fieldGroup = {
                        id: formGroup.id,
                        className: formGroup.className,
                        label: formGroup.querySelector('label')?.textContent
                    };
                }
                
                // Find related fields (same form)
                if (element.form) {
                    const formElements = Array.from(element.form.elements);
                    
                    // Find fields with similar names (e.g., address1, address2)
                    const baseName = element.name ? element.name.replace(/[\\d_-]+$/, '') : '';
                    if (baseName) {
                        relationships.relatedFields = formElements
                            .filter(el => el !== element && el.name && el.name.startsWith(baseName))
                            .slice(0, 5)
                            .map(el => ({
                                name: el.name,
                                id: el.id,
                                type: el.type
                            }));
                    }
                    
                    // Find dependent fields (e.g., state depends on country)
                    const dependencyAttributes = ['data-depends-on', 'data-requires', 'data-condition'];
                    for (let attr of dependencyAttributes) {
                        const dependency = element.getAttribute(attr);
                        if (dependency) {
                            const dependentElement = element.form.querySelector(`[name="${dependency}"], #${dependency}`);
                            if (dependentElement) {
                                relationships.dependentFields.push({
                                    name: dependentElement.name,
                                    id: dependentElement.id,
                                    type: dependentElement.type
                                });
                            }
                        }
                    }
                }
                
                return relationships;
            };
            
            // Helper function to detect common UI patterns
            const detectUIPatterns = (element) => {
                const patterns = [];
                const classes = element.className.toLowerCase();
                const id = element.id.toLowerCase();
                const role = element.getAttribute('role');
                
                // Modal patterns
                if (classes.includes('modal') || role === 'dialog') {
                    patterns.push('modal');
                }
                
                // Tab patterns
                if (role === 'tab' || classes.includes('tab')) {
                    patterns.push('tabs');
                }
                
                // Accordion patterns
                if (role === 'button' && element.getAttribute('aria-expanded') !== null) {
                    patterns.push('accordion');
                }
                
                // Dropdown patterns
                if (classes.includes('dropdown') || role === 'combobox') {
                    patterns.push('dropdown');
                }
                
                // Carousel patterns
                if (classes.includes('carousel') || classes.includes('slider')) {
                    patterns.push('carousel');
                }
                
                // Pagination patterns
                if (classes.includes('pagination') || role === 'navigation' && classes.includes('page')) {
                    patterns.push('pagination');
                }
                
                // Search patterns
                if (element.type === 'search' || classes.includes('search') || id.includes('search')) {
                    patterns.push('search');
                }
                
                // Filter patterns
                if (classes.includes('filter') || id.includes('filter')) {
                    patterns.push('filter');
                }
                
                return patterns;
            };
            
            // Helper function to extract data attributes
            const getDataAttributes = (element) => {
                const dataAttrs = {};
                for (let attr of element.attributes) {
                    if (attr.name.startsWith('data-')) {
                        dataAttrs[attr.name] = attr.value;
                    }
                }
                return dataAttrs;
            };
            
            // Main extraction logic
            const elements = [];
            const processedElements = new Set();
            
            // Comprehensive selectors for interactive elements
            const selectors = [
                // Form elements
                'input:not([type="hidden"])',
                'textarea',
                'select',
                'button',
                
                // Links and navigation
                'a[href]',
                '[role="link"]',
                '[role="button"]',
                
                // Interactive elements
                '[onclick]',
                '[contenteditable="true"]',
                '[draggable="true"]',
                
                // ARIA interactive roles
                '[role="checkbox"]',
                '[role="radio"]',
                '[role="switch"]',
                '[role="slider"]',
                '[role="spinbutton"]',
                '[role="combobox"]',
                '[role="listbox"]',
                '[role="menu"]',
                '[role="menuitem"]',
                '[role="tab"]',
                '[role="dialog"]',
                
                // Custom interactive elements
                '[tabindex]:not([tabindex="-1"])',
                
                // Common UI components
                '.btn',
                '.button',
                '.link',
                '.clickable',
                
                // Data elements
                'table',
                '[role="grid"]',
                '[role="table"]',
                
                // Media elements
                'video',
                'audio',
                'img[alt]',
                
                // Navigation elements
                'nav',
                '[role="navigation"]',
                '.navigation',
                '.nav',
                
                // Content sections
                'main',
                'article',
                'section',
                '[role="main"]',
                '[role="article"]',
                '[role="region"]',
                
                // Error and feedback elements
                '[role="alert"]',
                '[role="status"]',
                '.error',
                '.warning',
                '.success',
                '.message'
            ];
            
            // Process all matching elements
            document.querySelectorAll(selectors.join(', ')).forEach(element => {
                // Skip if already processed
                if (processedElements.has(element)) return;
                processedElements.add(element);
                
                // Skip if element is not important enough
                const rect = element.getBoundingClientRect();
                if (rect.width < 1 || rect.height < 1) return;
                
                // Extract comprehensive data
                const elementData = {
                    // Basic identification
                    tag_name: element.tagName.toLowerCase(),
                    id: element.id || null,
                    className: element.className || '',
                    name: element.name || null,
                    
                    // Selectors
                    xpath: (() => {
                        // Generate XPath
                        let path = '';
                        let current = element;
                        while (current && current.nodeType === Node.ELEMENT_NODE) {
                            let index = 0;
                            let sibling = current.previousSibling;
                            while (sibling) {
                                if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === current.nodeName) {
                                    index++;
                                }
                                sibling = sibling.previousSibling;
                            }
                            const tagName = current.nodeName.toLowerCase();
                            const xpathIndex = index > 0 ? `[${index + 1}]` : '';
                            path = `/${tagName}${xpathIndex}${path}`;
                            current = current.parentNode;
                        }
                        return path;
                    })(),
                    cssSelector: (() => {
                        // Generate CSS selector
                        if (element.id) return `#${element.id}`;
                        let selector = element.tagName.toLowerCase();
                        if (element.className) {
                            selector += `.${element.className.split(' ').filter(c => c).join('.')}`;
                        }
                        return selector;
                    })(),
                    
                    // Content
                    textContent: (element.textContent || '').trim().substring(0, 500),
                    value: element.value || null,
                    placeholder: element.placeholder || null,
                    innerHTML: element.innerHTML.substring(0, 1000),
                    outerHTML: element.outerHTML.substring(0, 2000),
                    
                    // Attributes
                    href: element.href || null,
                    src: element.src || null,
                    alt: element.alt || null,
                    title: element.title || null,
                    type: element.type || null,
                    
                    // State
                    isEnabled: !element.disabled,
                    isVisible: rect.width > 0 && rect.height > 0,
                    isChecked: element.checked || false,
                    isSelected: element.selected || false,
                    isRequired: element.required || false,
                    isReadonly: element.readOnly || false,
                    
                    // Semantic and business context
                    semanticRole: getSemanticRole(element),
                    businessContext: getBusinessContext(element),
                    
                    // Validation rules
                    validationRules: getValidationRules(element),
                    
                    // Hierarchy
                    hierarchy: getElementHierarchy(element),
                    
                    // Interaction patterns
                    interactionPatterns: getInteractionPatterns(element),
                    
                    // Accessibility
                    accessibility: getAccessibilityContext(element),
                    
                    // Visual context
                    visual: getVisualContext(element),
                    
                    // Form relationships
                    formRelationships: getFormFieldRelationships(element),
                    
                    // UI patterns
                    uiPatterns: detectUIPatterns(element),
                    
                    // Data attributes
                    dataAttributes: getDataAttributes(element),
                    
                    // Options (for select elements)
                    options: element.tagName === 'SELECT' ? 
                        Array.from(element.options).map(opt => ({
                            value: opt.value,
                            text: opt.text,
                            selected: opt.selected
                        })) : null,
                    
                    // Event listeners (detect if element has event handlers)
                    hasEventListeners: {
                        click: !!element.onclick,
                        change: !!element.onchange,
                        focus: !!element.onfocus,
                        blur: !!element.onblur,
                        keydown: !!element.onkeydown,
                        submit: !!element.onsubmit
                    },
                    
                    // Computed element category (for LLM understanding)
                    elementCategory: (() => {
                        const tag = element.tagName.toLowerCase();
                        const type = element.type || '';
                        const role = element.getAttribute('role');
                        
                        // Authentication elements
                        if (element.type === 'password' || element.name === 'username' || element.name === 'email' && element.closest('form[action*="login"]')) {
                            return 'authentication';
                        }
                        
                        // Payment elements
                        if (element.name && element.name.match(/card|cvv|billing|payment/i)) {
                            return 'payment';
                        }
                        
                        // Navigation
                        if (tag === 'nav' || role === 'navigation') {
                            return 'navigation';
                        }
                        
                        // Form inputs
                        if (['input', 'textarea', 'select'].includes(tag)) {
                            return 'form_input';
                        }
                        
                        // Actions
                        if (tag === 'button' || tag === 'a' || role === 'button') {
                            return 'action';
                        }
                        
                        // Data display
                        if (tag === 'table' || role === 'grid') {
                            return 'data_display';
                        }
                        
                        // Media
                        if (['img', 'video', 'audio'].includes(tag)) {
                            return 'media';
                        }
                        
                        // Search
                        if (type === 'search' || element.className.includes('search')) {
                            return 'search';
                        }
                        
                        return 'content';
                    })(),
                    
                    // Test priority hint
                    testPriority: (() => {
                        // Critical elements
                        if (element.type === 'submit' || element.textContent.match(/submit|save|confirm|pay|checkout/i)) {
                            return 'critical';
                        }
                        
                        // High priority
                        if (element.required || element.tagName === 'BUTTON' || element.type === 'password') {
                            return 'high';
                        }
                        
                        // Medium priority
                        if (['input', 'select', 'textarea'].includes(element.tagName.toLowerCase())) {
                            return 'medium';
                        }
                        
                        return 'low';
                    })()
                };
                
                elements.push(elementData);
            });
            
            // Extract page-level context
            const pageContext = {
                url: window.location.href,
                title: document.title,
                description: document.querySelector('meta[name="description"]')?.content || '',
                keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                
                // Page type detection
                pageType: (() => {
                    const url = window.location.pathname.toLowerCase();
                    const title = document.title.toLowerCase();
                    const bodyText = document.body.textContent.toLowerCase();
                    
                    if (url.includes('login') || url.includes('signin')) return 'login';
                    if (url.includes('register') || url.includes('signup')) return 'registration';
                    if (url.includes('checkout') || url.includes('payment')) return 'checkout';
                    if (url.includes('cart')) return 'shopping_cart';
                    if (url.includes('product') || url.includes('item')) return 'product_detail';
                    if (url.includes('search') || url.includes('results')) return 'search_results';
                    if (url.includes('profile') || url.includes('account')) return 'user_profile';
                    if (url.includes('dashboard')) return 'dashboard';
                    if (url === '/' || url === '/index') return 'homepage';
                    
                    return 'general';
                })(),
                
                // Forms on page
                forms: Array.from(document.forms).map(form => ({
                    id: form.id,
                    name: form.name,
                    action: form.action,
                    method: form.method,
                    fields: form.elements.length
                })),
                
                // Navigation structure
                navigation: {
                    mainNav: document.querySelector('nav, [role="navigation"]') ? true : false,
                    breadcrumbs: document.querySelector('[aria-label="breadcrumb"], .breadcrumb') ? true : false,
                    pagination: document.querySelector('[role="navigation"][aria-label*="pagination"], .pagination') ? true : false
                },
                
                // Page sections
                sections: (() => {
                    const sections = [];
                    document.querySelectorAll('section, article, [role="region"]').forEach(section => {
                        sections.push({
                            tag: section.tagName.toLowerCase(),
                            id: section.id,
                            heading: section.querySelector('h1, h2, h3')?.textContent || '',
                            ariaLabel: section.getAttribute('aria-label') || ''
                        });
                    });
                    return sections;
                })(),
                
                // Error messages on page
                errorMessages: Array.from(document.querySelectorAll('[role="alert"], .error, .warning')).map(el => el.textContent),
                
                // Modal dialogs
                hasModals: document.querySelector('[role="dialog"], .modal') ? true : false,
                
                // Framework detection
                framework: (() => {
                    if (window.React || document.querySelector('[data-reactroot]')) return 'react';
                    if (window.angular || document.querySelector('[ng-app]')) return 'angular';
                    if (window.Vue || document.querySelector('[data-v-]')) return 'vue';
                    if (document.querySelector('[class*="svelte"]')) return 'svelte';
                    if (window.jQuery) return 'jquery';
                    return null;
                })(),
                
                // Performance metrics
                performance: {
                    domElements: document.getElementsByTagName('*').length,
                    forms: document.forms.length,
                    inputs: document.querySelectorAll('input, textarea, select').length,
                    buttons: document.querySelectorAll('button, [role="button"]').length,
                    links: document.querySelectorAll('a[href]').length,
                    images: document.images.length
                }
            };
            
            return {
                elements: elements,
                pageContext: pageContext,
                extractionTimestamp: new Date().toISOString()
            };
        }
        """
        
        try:
            result = await page.evaluate(extraction_script)
            return result
        except Exception as e:
            raise Exception(f"LLM-enhanced extraction failed: {e}")


class UltimateStealthBrowserLLMEnhanced(UltimateStealthBrowser):
    """
    Enhanced version of UltimateStealthBrowser with LLM-optimized extraction.
    
    This class extends the base browser to provide rich context extraction
    specifically designed for high-quality LLM test generation.
    """
    
    async def extract_elements_for_llm(self, url: Optional[str] = None) -> PageStructure:
        """
        Extract elements with comprehensive LLM-optimized context.
        
        Returns a PageStructure object ready for LLM test generation.
        """
        
        # Navigate if URL provided
        if url:
            if not await self.navigate(url):
                raise Exception(f"Failed to navigate to {url}")
        
        # Extract with enhanced strategy
        extraction_data = await LLMEnhancedExtractionStrategy.extract_with_llm_context(
            self.page, 
            self.config
        )
        
        # Convert to LLM-optimized structure
        page_structure = self._build_page_structure(extraction_data)
        
        return page_structure
    
    def _build_page_structure(self, extraction_data: Dict[str, Any]) -> PageStructure:
        """Convert raw extraction data to PageStructure"""
        
        page_context = extraction_data.get('pageContext', {})
        elements_data = extraction_data.get('elements', [])
        
        # Create page structure
        page = PageStructure(
            url=page_context.get('url', ''),
            title=page_context.get('title', ''),
            page_type=page_context.get('pageType', 'general'),
            description=page_context.get('description', ''),
            business_purpose=self._infer_business_purpose(page_context)
        )
        
        # Convert and categorize elements
        elements_by_category = {}
        
        for elem_data in elements_data:
            # Convert to LLM-optimized element
            llm_element = self._convert_to_llm_element(elem_data, page_context)
            
            # Categorize
            category = llm_element.element_category
            if category not in elements_by_category:
                elements_by_category[category] = []
            elements_by_category[category].append(llm_element)
        
        page.elements_by_category = elements_by_category
        
        # Extract user journeys
        page.user_journeys = self._extract_user_journeys(elements_data, page_context)
        
        # Extract critical paths
        page.critical_paths = self._identify_critical_paths(elements_data, page_context)
        
        # Add page validations
        page.page_validations = self._extract_page_validations(elements_data)
        
        # Add security considerations
        page.security_considerations = self._identify_security_considerations(page_context, elements_data)
        
        return page
    
    def _convert_to_llm_element(self, elem_data: Dict[str, Any], page_context: Dict[str, Any]) -> LLMOptimizedElement:
        """Convert raw element data to LLMOptimizedElement"""
        
        # Build semantic context
        semantic = SemanticContext(
            primary_purpose=self._get_element_purpose(elem_data),
            business_function=elem_data.get('businessContext', {}).get('businessFunction'),
            user_intent=self._infer_user_intent(elem_data),
            related_features=self._get_related_features(elem_data),
            keywords=self._extract_keywords(elem_data),
            domain_tags=self._get_domain_tags(page_context)
        )
        
        # Build interaction context
        interaction = InteractionContext(
            primary_interaction=self._get_primary_interaction(elem_data),
            alternative_interactions=self._get_alternative_interactions(elem_data),
            prerequisites=self._get_prerequisites(elem_data),
            expected_outcomes=self._get_expected_outcomes(elem_data),
            common_flows=self._get_common_flows(elem_data),
            error_scenarios=self._get_error_scenarios(elem_data)
        )
        
        # Build validation context (if applicable)
        validation = None
        if elem_data.get('validationRules'):
            validation = self._build_validation_context(elem_data)
        
        # Build accessibility context
        accessibility = None
        if elem_data.get('accessibility'):
            accessibility = self._build_accessibility_context(elem_data)
        
        # Build hierarchy context
        hierarchy = None
        if elem_data.get('hierarchy'):
            hierarchy = self._build_hierarchy_context(elem_data)
        
        # Build visual context
        visual = None
        if elem_data.get('visual'):
            visual = self._build_visual_context(elem_data)
        
        # Build state context
        state = self._build_state_context(elem_data)
        
        # Create LLM element
        element = LLMOptimizedElement(
            element_id=self._generate_element_id(elem_data),
            tag_name=elem_data.get('tag_name', 'unknown'),
            element_category=self._determine_category(elem_data),
            selectors=self._extract_selectors(elem_data),
            semantic=semantic,
            interaction=interaction,
            content=self._extract_content(elem_data),
            validation=validation,
            accessibility=accessibility,
            hierarchy=hierarchy,
            visual=visual,
            state=state,
            test_priority=self._determine_test_priority(elem_data),
            suggested_test_types=self._suggest_test_types(elem_data),
            test_data_examples=self._generate_test_examples(elem_data),
            page_context={
                'url': page_context.get('url', ''),
                'page_title': page_context.get('title', ''),
                'page_type': page_context.get('pageType', '')
            }
        )
        
        return element
    
    # Helper methods for conversion
    
    def _get_element_purpose(self, elem_data: Dict[str, Any]) -> str:
        """Determine element's primary purpose"""
        text = elem_data.get('textContent', '')[:100]
        tag = elem_data.get('tag_name', '')
        element_type = elem_data.get('type', '')
        
        if elem_data.get('businessContext', {}).get('isAuthentication'):
            return f"Authentication: {text or tag}"
        elif elem_data.get('businessContext', {}).get('isPayment'):
            return f"Payment: {text or tag}"
        elif elem_data.get('businessContext', {}).get('isSearch'):
            return f"Search: {text or tag}"
        elif tag == 'button' or elem_data.get('type') == 'submit':
            return f"Action button: {text or 'Submit'}"
        elif tag == 'input':
            return f"Input field: {elem_data.get('placeholder') or elem_data.get('name') or element_type}"
        else:
            return f"{tag}: {text or 'Interactive element'}"
    
    def _infer_user_intent(self, elem_data: Dict[str, Any]) -> str:
        """Infer what the user intends to do with this element"""
        text = (elem_data.get('textContent') or '').lower()
        element_type = (elem_data.get('type') or '').lower()
        
        if 'submit' in text or element_type == 'submit':
            return "Complete and submit form"
        elif 'search' in text or element_type == 'search':
            return "Search for information"
        elif 'login' in text or 'sign in' in text:
            return "Authenticate to access account"
        elif 'add to cart' in text:
            return "Add item to shopping cart"
        elif 'checkout' in text:
            return "Proceed to payment"
        elif elem_data.get('tag_name') == 'a':
            return "Navigate to linked page"
        else:
            return "Interact with element"
    
    def _extract_keywords(self, elem_data: Dict[str, Any]) -> List[str]:
        """Extract keywords from element"""
        keywords = []
        
        # From text content
        text = elem_data.get('textContent', '')
        if text:
            words = re.findall(r'\b\w+\b', text.lower())
            keywords.extend([w for w in words if len(w) > 3][:5])
        
        # From attributes
        for attr in ['placeholder', 'aria-label', 'title', 'name']:
            value = elem_data.get(attr)
            if value:
                words = re.findall(r'\b\w+\b', value.lower())
                keywords.extend([w for w in words if len(w) > 3][:2])
        
        return list(set(keywords))
    
    def _get_domain_tags(self, page_context: Dict[str, Any]) -> List[str]:
        """Get domain-specific tags based on page context"""
        tags = []
        page_type = page_context.get('pageType', '')
        
        domain_map = {
            'login': ['authentication', 'security'],
            'registration': ['user-onboarding', 'data-collection'],
            'checkout': ['e-commerce', 'payment'],
            'shopping_cart': ['e-commerce'],
            'product_detail': ['e-commerce', 'catalog'],
            'search_results': ['discovery', 'filtering'],
            'user_profile': ['account-management'],
            'dashboard': ['analytics', 'reporting']
        }
        
        tags.extend(domain_map.get(page_type, []))
        return tags
    
    def _determine_category(self, elem_data: Dict[str, Any]) -> ElementCategory:
        """Determine element category"""
        category_str = elem_data.get('elementCategory', 'content')
        
        category_map = {
            'navigation': ElementCategory.NAVIGATION,
            'form_input': ElementCategory.FORM_INPUT,
            'action': ElementCategory.ACTION,
            'content': ElementCategory.CONTENT,
            'media': ElementCategory.MEDIA,
            'data_display': ElementCategory.DATA_DISPLAY,
            'authentication': ElementCategory.AUTHENTICATION,
            'payment': ElementCategory.PAYMENT,
            'search': ElementCategory.SEARCH
        }
        
        return category_map.get(category_str, ElementCategory.CONTENT)
    
    def _get_primary_interaction(self, elem_data: Dict[str, Any]) -> InteractionPattern:
        """Get primary interaction pattern"""
        patterns = elem_data.get('interactionPatterns', [])
        if patterns:
            pattern_map = {
                'click': InteractionPattern.CLICK,
                'type_text': InteractionPattern.TYPE_TEXT,
                'select_option': InteractionPattern.SELECT_OPTION,
                'drag_drop': InteractionPattern.DRAG_DROP,
                'hover': InteractionPattern.HOVER,
                'upload_file': InteractionPattern.UPLOAD_FILE
            }
            return pattern_map.get(patterns[0], InteractionPattern.CLICK)
        
        # Default based on element type
        tag = elem_data.get('tag_name', '')
        if tag in ['input', 'textarea']:
            return InteractionPattern.TYPE_TEXT
        elif tag == 'select':
            return InteractionPattern.SELECT_OPTION
        else:
            return InteractionPattern.CLICK
    
    def _extract_selectors(self, elem_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract multiple selector strategies"""
        selectors = {}
        
        if elem_data.get('id'):
            selectors['id'] = elem_data['id']
        
        if elem_data.get('cssSelector'):
            selectors['css'] = elem_data['cssSelector']
        
        if elem_data.get('xpath'):
            selectors['xpath'] = elem_data['xpath']
        
        # Add data-testid if present
        data_attrs = elem_data.get('dataAttributes', {})
        if 'data-testid' in data_attrs:
            selectors['data_testid'] = data_attrs['data-testid']
        
        return selectors
    
    def _determine_test_priority(self, elem_data: Dict[str, Any]) -> TestPriority:
        """Determine test priority"""
        priority_str = elem_data.get('testPriority', 'medium')
        
        priority_map = {
            'critical': TestPriority.CRITICAL,
            'high': TestPriority.HIGH,
            'medium': TestPriority.MEDIUM,
            'low': TestPriority.LOW
        }
        
        return priority_map.get(priority_str, TestPriority.MEDIUM)
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                # Handle 'auto' and other non-numeric strings
                if value.lower() in ['auto', 'inherit', 'initial']:
                    return None
                # Remove 'px' suffix if present
                value = value.replace('px', '').strip()
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _generate_element_id(self, elem_data: Dict[str, Any]) -> str:
        """Generate unique element ID"""
        # Use existing ID if available
        if elem_data.get('id'):
            return elem_data['id']
        
        # Generate from attributes
        id_source = f"{elem_data.get('tag_name', '')}_{elem_data.get('xpath', '')}_{elem_data.get('textContent', '')}"
        return hashlib.md5(id_source.encode()).hexdigest()[:8]
    
    def _infer_business_purpose(self, page_context: Dict[str, Any]) -> str:
        """Infer business purpose of the page"""
        page_type = page_context.get('pageType', '')
        
        purpose_map = {
            'login': 'User authentication and access control',
            'registration': 'New user account creation',
            'checkout': 'Complete purchase transaction',
            'shopping_cart': 'Review and manage selected items',
            'product_detail': 'View product information and make purchase decision',
            'search_results': 'Find relevant products or information',
            'user_profile': 'Manage user account and preferences',
            'dashboard': 'Monitor and analyze key metrics',
            'homepage': 'Entry point and navigation hub'
        }
        
        return purpose_map.get(page_type, 'Provide user functionality')
    
    def _extract_user_journeys(self, elements_data: List[Dict], page_context: Dict) -> List[Dict[str, Any]]:
        """Extract common user journeys from page elements"""
        journeys = []
        
        # Check for common journey patterns
        has_login = any(e.get('businessContext', {}).get('isAuthentication') for e in elements_data)
        has_search = any(e.get('businessContext', {}).get('isSearch') for e in elements_data)
        has_payment = any(e.get('businessContext', {}).get('isPayment') for e in elements_data)
        has_form = any(e.get('tag_name') == 'form' for e in elements_data)
        
        if has_login:
            journeys.append({
                'name': 'User Authentication',
                'steps': ['Enter credentials', 'Submit login form', 'Verify successful login'],
                'critical': True
            })
        
        if has_search:
            journeys.append({
                'name': 'Search and Discovery',
                'steps': ['Enter search terms', 'Submit search', 'Review results', 'Select item'],
                'critical': False
            })
        
        if has_payment:
            journeys.append({
                'name': 'Payment Processing',
                'steps': ['Enter payment details', 'Verify information', 'Submit payment', 'Confirm transaction'],
                'critical': True
            })
        
        if has_form and not has_login and not has_payment:
            journeys.append({
                'name': 'Form Submission',
                'steps': ['Fill required fields', 'Validate inputs', 'Submit form', 'Verify submission'],
                'critical': True
            })
        
        return journeys
    
    def _identify_critical_paths(self, elements_data: List[Dict], page_context: Dict) -> List[Dict[str, Any]]:
        """Identify critical user paths that must be tested"""
        critical_paths = []
        
        # Find submit buttons and critical actions
        for element in elements_data:
            if element.get('testPriority') == 'critical' or element.get('type') == 'submit':
                critical_paths.append({
                    'element': element.get('id') or element.get('textContent', '')[:50],
                    'action': 'click',
                    'prerequisites': self._find_required_fields(elements_data, element),
                    'expected_outcome': 'Form submission or critical action completion'
                })
        
        return critical_paths[:5]  # Limit to top 5 critical paths
    
    def _find_required_fields(self, elements_data: List[Dict], submit_element: Dict) -> List[str]:
        """Find required fields related to a submit button"""
        required = []
        
        # If submit button is in a form, find required fields in the same form
        form_id = submit_element.get('hierarchy', {}).get('parentForm', {}).get('id')
        
        for element in elements_data:
            if element.get('isRequired'):
                if not form_id or element.get('hierarchy', {}).get('parentForm', {}).get('id') == form_id:
                    field_id = element.get('id') or element.get('name') or element.get('placeholder', '')[:30]
                    required.append(field_id)
        
        return required
    
    def _extract_page_validations(self, elements_data: List[Dict]) -> List[str]:
        """Extract page-level validation rules"""
        validations = set()
        
        for element in elements_data:
            rules = element.get('validationRules', {})
            
            if rules.get('required'):
                validations.add(f"Required field: {element.get('name') or element.get('id')}")
            
            if rules.get('pattern'):
                validations.add(f"Pattern validation: {element.get('name')} must match {rules.get('pattern')}")
            
            if rules.get('minLength') or rules.get('maxLength'):
                validations.add(f"Length validation: {element.get('name')} has length constraints")
        
        return list(validations)[:10]  # Limit to 10 most important
    
    def _identify_security_considerations(self, page_context: Dict, elements_data: List[Dict]) -> List[str]:
        """Identify security aspects to test"""
        considerations = []
        
        # Check for sensitive fields
        has_password = any(e.get('type') == 'password' for e in elements_data)
        has_payment = any(e.get('businessContext', {}).get('isPayment') for e in elements_data)
        has_file_upload = any(e.get('type') == 'file' for e in elements_data)
        
        if has_password:
            considerations.append("Password field security and encryption")
            considerations.append("Brute force protection")
        
        if has_payment:
            considerations.append("Payment data encryption")
            considerations.append("PCI compliance")
            considerations.append("Secure payment gateway integration")
        
        if has_file_upload:
            considerations.append("File type validation")
            considerations.append("File size limits")
            considerations.append("Malware scanning")
        
        # XSS and injection
        if any(e.get('tag_name') in ['input', 'textarea'] for e in elements_data):
            considerations.append("XSS prevention in input fields")
            considerations.append("SQL injection prevention")
        
        return considerations
    
    # Additional helper methods...
    
    def _get_related_features(self, elem_data: Dict[str, Any]) -> List[str]:
        """Get related features based on element context"""
        features = []
        
        if elem_data.get('formRelationships', {}).get('fieldset'):
            features.append(f"Part of: {elem_data['formRelationships']['fieldset'].get('legend', 'Field group')}")
        
        if elem_data.get('uiPatterns'):
            features.extend(elem_data['uiPatterns'])
        
        return features
    
    def _get_alternative_interactions(self, elem_data: Dict[str, Any]) -> List[InteractionPattern]:
        """Get alternative interaction patterns"""
        patterns = []
        
        # Keyboard alternatives
        if elem_data.get('accessibility', {}).get('accessKey'):
            patterns.append(InteractionPattern.KEYBOARD_SHORTCUT)
        
        # Hover for tooltips
        if elem_data.get('title'):
            patterns.append(InteractionPattern.HOVER)
        
        return patterns
    
    def _get_prerequisites(self, elem_data: Dict[str, Any]) -> List[str]:
        """Get prerequisites for interacting with element"""
        prereqs = []
        
        # Check if element is in a form that requires login
        if elem_data.get('businessContext', {}).get('isAuthentication'):
            prereqs.append("User must be on login page")
        
        # Check if element depends on other fields
        deps = elem_data.get('formRelationships', {}).get('dependentFields', [])
        for dep in deps:
            prereqs.append(f"Field '{dep.get('name')}' must be filled")
        
        return prereqs
    
    def _get_expected_outcomes(self, elem_data: Dict[str, Any]) -> List[str]:
        """Get expected outcomes after interaction"""
        outcomes = []
        
        element_type = elem_data.get('type', '')
        tag = elem_data.get('tag_name', '')
        
        if element_type == 'submit':
            outcomes.append("Form submission")
            outcomes.append("Validation messages if errors")
            outcomes.append("Navigation to next page if successful")
        elif tag == 'a':
            outcomes.append("Navigation to linked page")
        elif element_type == 'checkbox':
            outcomes.append("Toggle checked state")
        
        return outcomes
    
    def _get_common_flows(self, elem_data: Dict[str, Any]) -> List[str]:
        """Get common user flows involving this element"""
        flows = []
        
        if elem_data.get('businessContext', {}).get('isAuthentication'):
            flows.append("Login → Dashboard")
        
        if elem_data.get('businessContext', {}).get('isPayment'):
            flows.append("Add to Cart → Checkout → Payment → Confirmation")
        
        return flows
    
    def _get_error_scenarios(self, elem_data: Dict[str, Any]) -> List[str]:
        """Get common error scenarios to test"""
        scenarios = []
        
        if elem_data.get('isRequired'):
            scenarios.append("Submit without filling required field")
        
        if elem_data.get('validationRules', {}).get('pattern'):
            scenarios.append("Enter invalid format")
        
        if elem_data.get('type') == 'email':
            scenarios.append("Enter invalid email format")
        
        return scenarios
    
    def _suggest_test_types(self, elem_data: Dict[str, Any]) -> List[str]:
        """Suggest test types for element"""
        test_types = ['functional']
        
        if elem_data.get('validationRules'):
            test_types.append('validation')
        
        if elem_data.get('accessibility'):
            test_types.append('accessibility')
        
        if elem_data.get('businessContext', {}).get('isPayment'):
            test_types.append('security')
        
        if elem_data.get('visual', {}).get('responsive'):
            test_types.append('responsive')
        
        return test_types
    
    def _generate_test_examples(self, elem_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test data examples"""
        examples = []
        
        element_type = elem_data.get('type', '')
        
        if element_type == 'email':
            examples = [
                {'value': 'test@example.com', 'expected': 'valid'},
                {'value': 'invalid.email', 'expected': 'invalid'},
                {'value': '', 'expected': 'required_error' if elem_data.get('isRequired') else 'valid'}
            ]
        elif element_type == 'password':
            examples = [
                {'value': 'StrongP@ss123', 'expected': 'valid'},
                {'value': '123', 'expected': 'too_short'},
                {'value': '', 'expected': 'required_error'}
            ]
        elif element_type == 'number':
            min_val = elem_data.get('validationRules', {}).get('min')
            max_val = elem_data.get('validationRules', {}).get('max')
            examples = [
                {'value': '50', 'expected': 'valid'},
                {'value': 'abc', 'expected': 'invalid'},
            ]
            if min_val:
                examples.append({'value': str(int(min_val) - 1), 'expected': 'below_minimum'})
            if max_val:
                examples.append({'value': str(int(max_val) + 1), 'expected': 'above_maximum'})
        
        return examples
    
    def _extract_content(self, elem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract element content"""
        content = {}
        
        if elem_data.get('textContent'):
            content['text'] = elem_data['textContent'][:200]
        
        if elem_data.get('placeholder'):
            content['placeholder'] = elem_data['placeholder']
        
        if elem_data.get('value'):
            content['value'] = elem_data['value']
        
        if elem_data.get('options'):
            content['options'] = [opt['text'] for opt in elem_data['options']]
        
        if elem_data.get('href'):
            content['href'] = elem_data['href']
        
        return content
    
    def _build_validation_context(self, elem_data: Dict[str, Any]) -> ValidationContext:
        """Build validation context from element data"""
        rules = []
        constraints = {}
        
        validation_rules = elem_data.get('validationRules', {})
        
        if validation_rules.get('required'):
            rules.append(ValidationRule.REQUIRED)
        
        if validation_rules.get('pattern'):
            rules.append(ValidationRule.PATTERN)
            constraints['pattern'] = validation_rules['pattern']
        
        if validation_rules.get('minLength') or validation_rules.get('maxLength'):
            rules.append(ValidationRule.LENGTH)
            if validation_rules.get('minLength'):
                constraints['minLength'] = validation_rules['minLength']
            if validation_rules.get('maxLength'):
                constraints['maxLength'] = validation_rules['maxLength']
        
        if validation_rules.get('min') or validation_rules.get('max'):
            rules.append(ValidationRule.RANGE)
            if validation_rules.get('min'):
                constraints['min'] = validation_rules['min']
            if validation_rules.get('max'):
                constraints['max'] = validation_rules['max']
        
        return ValidationContext(
            rules=rules,
            constraints=constraints,
            valid_values=self._generate_valid_values(elem_data),
            invalid_values=self._generate_invalid_values(elem_data),
            edge_cases=self._generate_edge_cases(elem_data),
            error_messages={}
        )
    
    def _generate_valid_values(self, elem_data: Dict[str, Any]) -> List[Any]:
        """Generate valid test values"""
        element_type = elem_data.get('type', '')
        
        if element_type == 'email':
            return ['test@example.com', 'user.name@domain.co.uk']
        elif element_type == 'number':
            return [1, 100, 50.5]
        elif element_type == 'tel':
            return ['+1234567890', '555-0123']
        else:
            return ['Valid input', 'Test data']
    
    def _generate_invalid_values(self, elem_data: Dict[str, Any]) -> List[Any]:
        """Generate invalid test values"""
        element_type = elem_data.get('type', '')
        
        if element_type == 'email':
            return ['invalid', '@example.com', 'test@']
        elif element_type == 'number':
            return ['abc', '!@#', '']
        else:
            return ['', '<script>alert("XSS")</script>']
    
    def _generate_edge_cases(self, elem_data: Dict[str, Any]) -> List[str]:
        """Generate edge cases to test"""
        cases = []
        
        if elem_data.get('validationRules', {}).get('maxLength'):
            cases.append("Maximum length input")
            cases.append("One character over maximum")
        
        if elem_data.get('type') == 'number':
            cases.append("Negative numbers")
            cases.append("Decimal values")
            cases.append("Very large numbers")
        
        return cases
    
    def _build_accessibility_context(self, elem_data: Dict[str, Any]) -> AccessibilityContext:
        """Build accessibility context"""
        acc = elem_data.get('accessibility', {})
        
        return AccessibilityContext(
            aria_role=acc.get('ariaRole'),
            aria_label=acc.get('ariaLabel'),
            aria_description=acc.get('ariaDescribedBy'),
            aria_properties={
                'expanded': acc.get('ariaExpanded'),
                'selected': acc.get('ariaSelected'),
                'checked': acc.get('ariaChecked')
            },
            keyboard_accessible=acc.get('isFocusable', False),
            tab_index=acc.get('tabIndex'),
            screen_reader_text=acc.get('label') or acc.get('ariaLabel')
        )
    
    def _build_hierarchy_context(self, elem_data: Dict[str, Any]) -> HierarchicalContext:
        """Build hierarchy context"""
        hierarchy = elem_data.get('hierarchy', {})
        
        parent_section_data = hierarchy.get('parentSection') or {}
        parent_form_data = hierarchy.get('parentForm') or {}
        
        return HierarchicalContext(
            parent_section=parent_section_data.get('tag') if parent_section_data else None,
            parent_form=parent_form_data.get('id') if parent_form_data else None,
            siblings=[s.get('id') or s.get('text', '')[:30] for s in hierarchy.get('siblings', [])],
            children=[c.get('id') or c.get('tag') for c in hierarchy.get('children', [])],
            navigation_order=elem_data.get('accessibility', {}).get('tabIndex')
        )
    
    def _build_visual_context(self, elem_data: Dict[str, Any]) -> VisualContext:
        """Build visual context"""
        visual = elem_data.get('visual', {})
        position = visual.get('position', {})
        visibility = visual.get('visibility', {})
        
        return VisualContext(
            x=position.get('x', 0),
            y=position.get('y', 0),
            width=position.get('width', 0),
            height=position.get('height', 0),
            is_visible=visibility.get('isVisible', True),
            is_above_fold=visibility.get('isAboveFold', False),
            z_index=self._safe_int(visibility.get('zIndex')),
            responsive_behavior={'breakpoint': visual.get('responsive', {}).get('breakpoint')}
        )
    
    def _build_state_context(self, elem_data: Dict[str, Any]) -> StateContext:
        """Build state context"""
        return StateContext(
            is_enabled=elem_data.get('isEnabled', True),
            is_readonly=elem_data.get('isReadonly', False),
            is_required=elem_data.get('isRequired', False),
            is_selected=elem_data.get('isSelected', False),
            is_checked=elem_data.get('isChecked', False),
            possible_states=[],
            state_triggers={},
            updates_dynamically=False,
            update_triggers=[],
            depends_on=[d.get('name') for d in elem_data.get('formRelationships', {}).get('dependentFields', [])],
            affects=[]
        )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_enhanced_extraction():
        """Test the enhanced extraction"""
        
        # Configure browser
        config = StealthConfig(
            level=StealthLevel.MAXIMUM,
            headless=False,
            detect_frameworks=True,
            detect_captcha=True
        )
        
        # Create enhanced browser
        async with UltimateStealthBrowserLLMEnhanced(config) as browser:
            # Extract with LLM optimization
            page_structure = await browser.extract_elements_for_llm("https://example.com")
            
            # Convert to JSON for LLM
            import json
            llm_data = json.dumps(page_structure.model_dump(), indent=2, default=str)
            
            print("LLM-Optimized Extraction Complete!")
            print(f"Page Type: {page_structure.page_type}")
            print(f"Business Purpose: {page_structure.business_purpose}")
            print(f"Total Elements: {sum(len(elems) for elems in page_structure.elements_by_category.values())}")
            print(f"Categories: {list(page_structure.elements_by_category.keys())}")
            print(f"User Journeys: {len(page_structure.user_journeys)}")
            print(f"Critical Paths: {len(page_structure.critical_paths)}")
            
            # Save to file
            with open("llm_extraction_output.json", "w") as f:
                f.write(llm_data)
            
            print("\nExtraction saved to llm_extraction_output.json")
    
    # Run test
    asyncio.run(test_enhanced_extraction())