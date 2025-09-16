#!/usr/bin/env python3
"""Investigation utilities for debugging element extraction issues."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import logging
from typing import Tuple, Optional

from playwright.async_api import async_playwright
from enhanced_stealth_extractor import EnhancedExtractionConfig

logger = logging.getLogger(__name__)

class ElementExtractionInvestigator:
    """Utility class for investigating element extraction issues."""
    
    def __init__(self, config: Optional[EnhancedExtractionConfig] = None):
        self.config = config or EnhancedExtractionConfig()
    
    async def investigate_zero_elements(self, url: str, name: str) -> dict:
        """Investigate why a site returns zero elements."""
        
        print(f"\n{'='*80}")
        print(f"INVESTIGATING: {name}")
        print(f"URL: {url}")
        print('='*80)
        
        investigation_result = {
            "site": name,
            "url": url,
            "issues_found": [],
            "recommendations": [],
            "page_info": {}
        }
        
        try:
            # Manual page investigation
            page_info = await self._investigate_page_content(url, name)
            investigation_result["page_info"] = page_info
            
            # Analyze issues
            issues = self._analyze_issues(page_info)
            investigation_result["issues_found"] = issues
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues)
            investigation_result["recommendations"] = recommendations
            
        except Exception as e:
            investigation_result["error"] = str(e)
            logger.error(f"Investigation failed for {name}: {e}")
        
        return investigation_result
    
    async def _investigate_page_content(self, url: str, name: str) -> dict:
        """Manually investigate page content to understand blocking."""
        
        print(f"\n🔍 MANUAL PAGE INVESTIGATION FOR {name}")
        print("-" * 60)
        
        page_info = {
            "title": None,
            "current_url": None,
            "redirected": False,
            "body_exists": False,
            "interactive_elements": 0,
            "error_messages": [],
            "anti_bot_scripts": [],
            "js_execution": None
        }
        
        async with async_playwright() as p:
            # Launch browser with maximum stealth
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--start-maximized'
            ]
            
            browser = await p.chromium.launch(headless=False, args=browser_args)
            
            # Create stealth context
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            page = await context.new_page()
            
            try:
                # Navigate to page
                print("1. Navigating to page...")
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for page to settle
                await page.wait_for_timeout(3000)
                
                # Check page title
                title = await page.title()
                page_info["title"] = title
                print(f"   Page Title: {title}")
                
                # Check if we're on the expected page
                current_url = page.url
                page_info["current_url"] = current_url
                print(f"   Current URL: {current_url}")
                
                # Check for redirect
                if url not in current_url:
                    page_info["redirected"] = True
                    print(f"   ⚠️ REDIRECTED: Expected {url}, got {current_url}")
                
                # Check page content
                print("\n2. Analyzing page content...")
                
                # Get body content
                body_exists = await page.locator('body').count() > 0
                page_info["body_exists"] = body_exists
                print(f"   Body element exists: {body_exists}")
                
                if body_exists:
                    # Check for error messages
                    error_selectors = [
                        'text=Access Denied',
                        'text=Blocked',
                        'text=Security Check',
                        'text=Verification Required',
                        'text=Please verify',
                        'text=Challenge',
                        '[class*="error"]',
                        '[class*="blocked"]',
                        '[class*="challenge"]'
                    ]
                    
                    for selector in error_selectors:
                        try:
                            count = await page.locator(selector).count()
                            if count > 0:
                                text = await page.locator(selector).first.text_content()
                                page_info["error_messages"].append({
                                    "selector": selector,
                                    "text": text[:100] if text else ""
                                })
                                print(f"   🚫 ERROR FOUND: {selector} -> {text[:50] if text else ''}")
                        except:
                            pass
                    
                    # Check for interactive elements
                    interactive_selectors = [
                        'a', 'button', 'input', 'select', 'textarea', 'form',
                        '[role="button"]', '[role="link"]'
                    ]
                    
                    total_interactive = 0
                    for selector in interactive_selectors:
                        try:
                            count = await page.locator(selector).count()
                            total_interactive += count
                            if count > 0:
                                print(f"   📊 {selector}: {count} elements")
                        except:
                            pass
                    
                    page_info["interactive_elements"] = total_interactive
                    print(f"   Total Interactive Elements: {total_interactive}")
                    
                    if total_interactive == 0:
                        print("   ⚠️ NO INTERACTIVE ELEMENTS - Possible content blocking")
                        
                        # Check if content is dynamically loaded
                        await page.wait_for_timeout(5000)  # Wait longer
                        
                        # Re-check after waiting
                        total_after_wait = 0
                        for selector in interactive_selectors:
                            try:
                                count = await page.locator(selector).count()
                                total_after_wait += count
                            except:
                                pass
                        
                        print(f"   After 5s wait: {total_after_wait} interactive elements")
                        page_info["interactive_elements_after_wait"] = total_after_wait
                    
                    # Check for JavaScript blocking
                    print("\n3. Testing JavaScript execution...")
                    try:
                        js_result = await page.evaluate('window.navigator.userAgent')
                        page_info["js_execution"] = "working"
                        print(f"   JS Execution: ✅ Working (UA: {js_result[:50]}...)")
                    except Exception as e:
                        page_info["js_execution"] = f"blocked: {str(e)}"
                        print(f"   JS Execution: ❌ Blocked ({e})")
                    
                    # Check for common anti-bot scripts
                    print("\n4. Checking for anti-bot detection...")
                    
                    anti_bot_indicators = [
                        'script[src*="cloudflare"]',
                        'script[src*="incapsula"]',
                        'script[src*="akamai"]',
                        'script[src*="perimeter"]',
                        'script[src*="datadome"]',
                        'script[src*="shape"]',
                        'script[src*="f5"]',
                        'script[src*="adobe"]',
                        'script[src*="ensighten"]',
                        'script[src*="bot-detection"]',
                        'script[src*="anti-bot"]'
                    ]
                    
                    for selector in anti_bot_indicators:
                        try:
                            count = await page.locator(selector).count()
                            if count > 0:
                                scripts = await page.locator(selector).all()
                                for script in scripts:
                                    src = await script.get_attribute('src')
                                    if src:
                                        page_info["anti_bot_scripts"].append(src)
                                        print(f"   🛡️ ANTI-BOT SCRIPT: {src}")
                        except:
                            pass
                
            except Exception as e:
                print(f"   ❌ Investigation failed: {e}")
                page_info["error"] = str(e)
            
            finally:
                await browser.close()
        
        return page_info
    
    def _analyze_issues(self, page_info: dict) -> list:
        """Analyze page info to identify issues."""
        
        issues = []
        
        # Check for redirects
        if page_info.get("redirected"):
            issues.append({
                "type": "redirect",
                "severity": "medium",
                "description": "Site redirects to different URL, may cause context issues"
            })
        
        # Check for anti-bot scripts
        if page_info.get("anti_bot_scripts"):
            issues.append({
                "type": "anti_bot_scripts",
                "severity": "high", 
                "description": f"Anti-bot scripts detected: {len(page_info['anti_bot_scripts'])} scripts",
                "scripts": page_info["anti_bot_scripts"]
            })
        
        # Check for error messages
        if page_info.get("error_messages"):
            issues.append({
                "type": "blocking_detected",
                "severity": "high",
                "description": "Blocking or error messages found on page",
                "messages": page_info["error_messages"]
            })
        
        # Check for no interactive elements
        if page_info.get("interactive_elements", 0) == 0:
            issues.append({
                "type": "no_interactive_elements",
                "severity": "high",
                "description": "No interactive elements found - possible content blocking"
            })
        
        # Check for JS blocking
        if page_info.get("js_execution") and "blocked" in str(page_info["js_execution"]):
            issues.append({
                "type": "js_blocked",
                "severity": "critical",
                "description": "JavaScript execution blocked"
            })
        
        return issues
    
    def _generate_recommendations(self, issues: list) -> list:
        """Generate recommendations based on identified issues."""
        
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "redirect":
                recommendations.append({
                    "issue": "redirect",
                    "recommendation": "Implement enhanced redirect handling with navigation tracking",
                    "implementation": "Use page.on('framenavigated') to track redirects"
                })
            
            elif issue["type"] == "anti_bot_scripts":
                recommendations.append({
                    "issue": "anti_bot_scripts",
                    "recommendation": "Block or modify problematic scripts using route interception",
                    "implementation": "Use page.route() to block scripts from detected domains"
                })
            
            elif issue["type"] == "blocking_detected":
                recommendations.append({
                    "issue": "blocking_detected", 
                    "recommendation": "Implement stronger stealth measures and human simulation",
                    "implementation": "Enhance browser fingerprint spoofing and add realistic behaviors"
                })
            
            elif issue["type"] == "no_interactive_elements":
                recommendations.append({
                    "issue": "no_interactive_elements",
                    "recommendation": "Implement multi-layer element extraction with longer wait times",
                    "implementation": "Add fallback extraction methods and extended page stability checks"
                })
            
            elif issue["type"] == "js_blocked":
                recommendations.append({
                    "issue": "js_blocked",
                    "recommendation": "Implement context recovery and alternative extraction methods",
                    "implementation": "Use Playwright selectors as fallback when JS evaluation fails"
                })
        
        return recommendations
    
    def print_investigation_report(self, investigation: dict):
        """Print a formatted investigation report."""
        
        print(f"\n{'='*80}")
        print(f"INVESTIGATION REPORT: {investigation['site']}")
        print("="*80)
        
        # Page Info
        page_info = investigation.get("page_info", {})
        print(f"\n📋 PAGE INFORMATION:")
        print(f"  URL: {investigation['url']}")
        print(f"  Final URL: {page_info.get('current_url', 'N/A')}")
        print(f"  Title: {page_info.get('title', 'N/A')}")
        print(f"  Redirected: {'Yes' if page_info.get('redirected') else 'No'}")
        print(f"  Interactive Elements: {page_info.get('interactive_elements', 0)}")
        
        # Issues Found
        issues = investigation.get("issues_found", [])
        print(f"\n🚨 ISSUES FOUND: {len(issues)}")
        if issues:
            for i, issue in enumerate(issues, 1):
                severity_icon = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🟢"}.get(issue["severity"], "⚪")
                print(f"  {i}. {severity_icon} {issue['type'].upper()}: {issue['description']}")
        else:
            print("  ✅ No issues detected")
        
        # Recommendations
        recommendations = investigation.get("recommendations", [])
        print(f"\n💡 RECOMMENDATIONS: {len(recommendations)}")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec['recommendation']}")
                print(f"     Implementation: {rec['implementation']}")
        else:
            print("  ✅ No specific recommendations needed")

async def investigate_sites(sites: list) -> dict:
    """Investigate multiple sites that have element extraction issues."""
    
    print("🔍 SITE INVESTIGATION SUITE")
    print("="*80)
    print("Investigating sites with zero elements or extraction issues...\n")
    
    investigator = ElementExtractionInvestigator()
    investigations = {}
    
    for url, name in sites:
        investigation = await investigator.investigate_zero_elements(url, name)
        investigations[name] = investigation
        
        # Print individual report
        investigator.print_investigation_report(investigation)
        
        # Delay between investigations
        await asyncio.sleep(2)
    
    return investigations