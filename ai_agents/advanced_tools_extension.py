"""
Advanced Custom Tools Extension for Browser-Use
Extends the custom tools framework with more sophisticated capabilities
"""

import asyncio
import json
import hashlib
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from custom_tools import CustomToolsManager


class SecurityScannerParams(BaseModel):
    """Parameters for security scanning"""
    scan_depth: str = Field(
        default="basic",
        description="Scan depth: basic, moderate, deep"
    )
    check_types: List[str] = Field(
        default=["xss", "csrf", "headers"],
        description="Types of security checks to perform"
    )


class DataExtractorParams(BaseModel):
    """Parameters for structured data extraction"""
    extraction_type: str = Field(
        default="auto",
        description="Type of data to extract: auto, table, json-ld, microdata, prices, emails, phones"
    )
    output_format: str = Field(
        default="json",
        description="Output format: json, csv, table"
    )


class AccessibilityAuditorParams(BaseModel):
    """Parameters for accessibility auditing"""
    wcag_level: str = Field(
        default="AA",
        description="WCAG compliance level to check: A, AA, AAA"
    )
    include_warnings: bool = Field(
        default=True,
        description="Include warnings in addition to errors"
    )


class SEOAnalyzerParams(BaseModel):
    """Parameters for SEO analysis"""
    check_categories: List[str] = Field(
        default=["meta", "headings", "images", "links"],
        description="SEO categories to analyze"
    )
    include_recommendations: bool = Field(
        default=True,
        description="Include SEO improvement recommendations"
    )


class InteractionRecorderParams(BaseModel):
    """Parameters for recording user interactions"""
    record_duration: int = Field(
        default=30,
        description="Duration to record interactions (seconds)"
    )
    capture_screenshots: bool = Field(
        default=False,
        description="Capture screenshots of interactions"
    )


class StateComparatorParams(BaseModel):
    """Parameters for comparing page states"""
    comparison_type: str = Field(
        default="visual",
        description="Type of comparison: visual, dom, content"
    )
    highlight_differences: bool = Field(
        default=True,
        description="Highlight differences in the output"
    )


class AdvancedToolsExtension:
    """Extension class for advanced browser-use tools"""

    def __init__(self, manager: CustomToolsManager):
        """
        Initialize advanced tools extension

        Args:
            manager: CustomToolsManager instance to extend
        """
        self.manager = manager
        self._register_advanced_tools()

    def _register_advanced_tools(self):
        """Register all advanced tools"""

        # Tool 1: Security Scanner
        @self.manager.tools.registry.action(
            'Perform security scan on the current page to identify vulnerabilities',
            param_model=SecurityScannerParams
        )
        async def security_scanner(params: SecurityScannerParams, browser_session):
            """Comprehensive security scanning tool"""

            security_checks_js = """
            (function() {
                const results = {
                    url: window.location.href,
                    timestamp: new Date().toISOString(),
                    vulnerabilities: [],
                    warnings: [],
                    info: [],
                    score: 100
                };

                // Check for XSS vulnerabilities
                if (""" + str('xss' in params.check_types).lower() + """) {
                    // Check for inline scripts
                    const inlineScripts = document.querySelectorAll('script:not([src])');
                    if (inlineScripts.length > 0) {
                        results.warnings.push({
                            type: 'XSS',
                            severity: 'medium',
                            message: `Found ${inlineScripts.length} inline scripts`,
                            recommendation: 'Move inline scripts to external files with CSP'
                        });
                        results.score -= 5;
                    }

                    // Check for dangerous event handlers
                    const dangerousHandlers = ['onclick', 'onmouseover', 'onerror', 'onload'];
                    let handlerCount = 0;
                    dangerousHandlers.forEach(handler => {
                        const elements = document.querySelectorAll(`[${handler}]`);
                        handlerCount += elements.length;
                    });
                    if (handlerCount > 0) {
                        results.vulnerabilities.push({
                            type: 'XSS',
                            severity: 'high',
                            message: `Found ${handlerCount} inline event handlers`,
                            recommendation: 'Use addEventListener instead of inline handlers'
                        });
                        results.score -= 10;
                    }
                }

                // Check for CSRF protection
                if (""" + str('csrf' in params.check_types).lower() + """) {
                    const forms = document.querySelectorAll('form');
                    let unprotectedForms = 0;
                    forms.forEach(form => {
                        const csrfToken = form.querySelector('[name*="csrf"], [name*="token"], [name*="_token"]');
                        if (!csrfToken && form.method.toLowerCase() === 'post') {
                            unprotectedForms++;
                        }
                    });
                    if (unprotectedForms > 0) {
                        results.vulnerabilities.push({
                            type: 'CSRF',
                            severity: 'high',
                            message: `Found ${unprotectedForms} forms without CSRF protection`,
                            recommendation: 'Add CSRF tokens to all POST forms'
                        });
                        results.score -= 15;
                    }
                }

                // Check security headers
                if (""" + str('headers' in params.check_types).lower() + """) {
                    // Check for HTTPS
                    if (window.location.protocol !== 'https:') {
                        results.vulnerabilities.push({
                            type: 'Transport',
                            severity: 'critical',
                            message: 'Site not using HTTPS',
                            recommendation: 'Enable HTTPS for all pages'
                        });
                        results.score -= 20;
                    }

                    // Check for mixed content
                    const insecureResources = document.querySelectorAll('[src^="http:"], [href^="http:"]');
                    if (insecureResources.length > 0) {
                        results.warnings.push({
                            type: 'Mixed Content',
                            severity: 'medium',
                            message: `Found ${insecureResources.length} insecure resources`,
                            recommendation: 'Use HTTPS for all resources'
                        });
                        results.score -= 5;
                    }
                }

                // Additional checks based on scan depth
                const depth = '""" + params.scan_depth + """';
                if (depth === 'moderate' || depth === 'deep') {
                    // Check for sensitive data in URLs
                    const urlParams = new URLSearchParams(window.location.search);
                    const sensitiveParams = ['password', 'pwd', 'token', 'api_key', 'secret'];
                    sensitiveParams.forEach(param => {
                        if (urlParams.has(param)) {
                            results.vulnerabilities.push({
                                type: 'Data Exposure',
                                severity: 'high',
                                message: `Sensitive parameter "${param}" found in URL`,
                                recommendation: 'Never pass sensitive data in URLs'
                            });
                            results.score -= 10;
                        }
                    });
                }

                if (depth === 'deep') {
                    // Check for autocomplete on sensitive fields
                    const sensitiveFields = document.querySelectorAll('input[type="password"], input[name*="card"], input[name*="cvv"]');
                    let autocompleteIssues = 0;
                    sensitiveFields.forEach(field => {
                        if (field.autocomplete !== 'off' && field.autocomplete !== 'new-password') {
                            autocompleteIssues++;
                        }
                    });
                    if (autocompleteIssues > 0) {
                        results.warnings.push({
                            type: 'Privacy',
                            severity: 'medium',
                            message: `${autocompleteIssues} sensitive fields allow autocomplete`,
                            recommendation: 'Disable autocomplete on sensitive fields'
                        });
                        results.score -= 3;
                    }
                }

                results.score = Math.max(0, results.score);
                return results;
            })();
            """

            result = await browser_session.evaluate(security_checks_js)

            # Generate security report HTML
            severity_colors = {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#28a745'
            }

            vulnerabilities_html = ''.join([
                f'<div class="issue critical"><strong>{v["type"]}</strong>: {v["message"]}<br><em>Fix: {v["recommendation"]}</em></div>'
                for v in result.get('vulnerabilities', [])
            ])

            warnings_html = ''.join([
                f'<div class="issue warning"><strong>{w["type"]}</strong>: {w["message"]}<br><em>Fix: {w["recommendation"]}</em></div>'
                for w in result.get('warnings', [])
            ])

            score_color = '#28a745' if result['score'] >= 80 else '#ffc107' if result['score'] >= 60 else '#dc3545'

            report_html = f"""
            <html>
            <head>
                <title>Security Scan Report</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: #1a1a2e; color: #eee; }}
                    .container {{ max-width: 1000px; margin: 0 auto; }}
                    h1 {{ color: #f39c12; text-align: center; }}
                    .score-card {{ background: #16213e; padding: 30px; border-radius: 10px; text-align: center; margin: 20px 0; }}
                    .score {{ font-size: 72px; font-weight: bold; color: {score_color}; }}
                    .score-label {{ font-size: 18px; color: #aaa; }}
                    .issues {{ background: #0f3460; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                    .issue {{ margin: 10px 0; padding: 15px; border-radius: 5px; }}
                    .issue.critical {{ background: rgba(220, 53, 69, 0.2); border-left: 4px solid #dc3545; }}
                    .issue.warning {{ background: rgba(255, 193, 7, 0.2); border-left: 4px solid #ffc107; }}
                    em {{ color: #4CAF50; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔒 Security Scan Report</h1>
                    <div class="score-card">
                        <div class="score">{result['score']}</div>
                        <div class="score-label">Security Score</div>
                    </div>
                    <div class="issues">
                        <h2>⚠️ Vulnerabilities ({len(result.get('vulnerabilities', []))})</h2>
                        {vulnerabilities_html or '<p style="color: #4CAF50;">No critical vulnerabilities found!</p>'}
                    </div>
                    <div class="issues">
                        <h2>⚡ Warnings ({len(result.get('warnings', []))})</h2>
                        {warnings_html or '<p style="color: #4CAF50;">No warnings!</p>'}
                    </div>
                </div>
            </body>
            </html>
            """

            await browser_session.evaluate(f"document.body.innerHTML = `{report_html}`;")
            return result

        # Tool 2: Structured Data Extractor
        @self.manager.tools.registry.action(
            'Extract structured data from the page (tables, JSON-LD, prices, contacts)',
            param_model=DataExtractorParams
        )
        async def extract_structured_data(params: DataExtractorParams, browser_session):
            """Extract structured data from web pages"""

            extraction_js = """
            (function() {
                const result = {
                    url: window.location.href,
                    timestamp: new Date().toISOString(),
                    data: {},
                    metadata: {}
                };

                const extractionType = '""" + params.extraction_type + """';

                // Auto-detect or specific extraction
                if (extractionType === 'auto' || extractionType === 'table') {
                    // Extract tables
                    const tables = document.querySelectorAll('table');
                    result.data.tables = [];
                    tables.forEach((table, index) => {
                        const tableData = [];
                        const rows = table.querySelectorAll('tr');
                        rows.forEach(row => {
                            const rowData = [];
                            const cells = row.querySelectorAll('td, th');
                            cells.forEach(cell => {
                                rowData.push(cell.textContent.trim());
                            });
                            if (rowData.length > 0) {
                                tableData.push(rowData);
                            }
                        });
                        if (tableData.length > 0) {
                            result.data.tables.push({
                                index: index,
                                rows: tableData.length,
                                columns: tableData[0]?.length || 0,
                                data: tableData
                            });
                        }
                    });
                    result.metadata.tableCount = result.data.tables.length;
                }

                if (extractionType === 'auto' || extractionType === 'json-ld') {
                    // Extract JSON-LD structured data
                    const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                    result.data.jsonLd = [];
                    jsonLdScripts.forEach(script => {
                        try {
                            const data = JSON.parse(script.textContent);
                            result.data.jsonLd.push(data);
                        } catch (e) {
                            console.error('Failed to parse JSON-LD:', e);
                        }
                    });
                    result.metadata.jsonLdCount = result.data.jsonLd.length;
                }

                if (extractionType === 'auto' || extractionType === 'prices') {
                    // Extract prices
                    const pricePatterns = [
                        /\$[\d,]+\.?\d*/g,
                        /€[\d,]+\.?\d*/g,
                        /£[\d,]+\.?\d*/g,
                        /[\d,]+\.?\d*\s*(USD|EUR|GBP)/gi
                    ];
                    result.data.prices = [];
                    const textContent = document.body.innerText;
                    pricePatterns.forEach(pattern => {
                        const matches = textContent.match(pattern) || [];
                        result.data.prices.push(...matches);
                    });
                    result.data.prices = [...new Set(result.data.prices)]; // Remove duplicates
                    result.metadata.priceCount = result.data.prices.length;
                }

                if (extractionType === 'auto' || extractionType === 'emails') {
                    // Extract email addresses
                    const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
                    const emails = document.body.innerHTML.match(emailPattern) || [];
                    result.data.emails = [...new Set(emails)];
                    result.metadata.emailCount = result.data.emails.length;
                }

                if (extractionType === 'auto' || extractionType === 'phones') {
                    // Extract phone numbers
                    const phonePatterns = [
                        /\+?1?\s*\(?[\d]{3}\)?[\s.-]?[\d]{3}[\s.-]?[\d]{4}/g,
                        /\+[\d]{1,3}[\s.-]?[\d]{2,4}[\s.-]?[\d]{6,10}/g
                    ];
                    result.data.phones = [];
                    const textContent = document.body.innerText;
                    phonePatterns.forEach(pattern => {
                        const matches = textContent.match(pattern) || [];
                        result.data.phones.push(...matches);
                    });
                    result.data.phones = [...new Set(result.data.phones)];
                    result.metadata.phoneCount = result.data.phones.length;
                }

                return result;
            })();
            """

            result = await browser_session.evaluate(extraction_js)

            # Format output based on requested format
            if params.output_format == "json":
                output = json.dumps(result, indent=2)
            elif params.output_format == "csv":
                # Simple CSV for prices/emails/phones
                lines = ["Type,Value"]
                for key in ['prices', 'emails', 'phones']:
                    if key in result['data']:
                        for value in result['data'][key]:
                            lines.append(f"{key},{value}")
                output = '\n'.join(lines)
            else:  # table format
                output = result

            # Display extraction results
            summary_html = f"""
            <html>
            <head>
                <title>Data Extraction Results</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: #f8f9fa; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                    .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .stat-value {{ font-size: 36px; font-weight: bold; color: #3498db; }}
                    .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
                    pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 Data Extraction Results</h1>
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-value">{result['metadata'].get('tableCount', 0)}</div>
                            <div class="stat-label">Tables Found</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{result['metadata'].get('priceCount', 0)}</div>
                            <div class="stat-label">Prices Found</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{result['metadata'].get('emailCount', 0)}</div>
                            <div class="stat-label">Emails Found</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{result['metadata'].get('phoneCount', 0)}</div>
                            <div class="stat-label">Phone Numbers</div>
                        </div>
                    </div>
                    <h2>Extracted Data ({params.output_format} format)</h2>
                    <pre>{json.dumps(result['data'], indent=2)[:2000]}...</pre>
                </div>
            </body>
            </html>
            """

            await browser_session.evaluate(f"document.body.innerHTML = `{summary_html}`;")
            return result

        # Tool 3: Accessibility Auditor
        @self.manager.tools.registry.action(
            'Perform comprehensive accessibility audit based on WCAG guidelines',
            param_model=AccessibilityAuditorParams
        )
        async def accessibility_audit(params: AccessibilityAuditorParams, browser_session):
            """Comprehensive accessibility auditing"""

            audit_js = """
            (function() {
                const results = {
                    url: window.location.href,
                    timestamp: new Date().toISOString(),
                    wcagLevel: '""" + params.wcag_level + """',
                    errors: [],
                    warnings: [],
                    passed: [],
                    score: 100
                };

                // Check images for alt text
                const images = document.querySelectorAll('img');
                let missingAlt = 0;
                images.forEach(img => {
                    if (!img.alt && !img.getAttribute('aria-label')) {
                        missingAlt++;
                        results.errors.push({
                            element: 'img',
                            issue: 'Missing alt text',
                            wcag: '1.1.1',
                            level: 'A',
                            impact: 'critical'
                        });
                    }
                });
                if (missingAlt > 0) {
                    results.score -= missingAlt * 2;
                }

                // Check heading hierarchy
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                let lastLevel = 0;
                let hierarchyIssues = 0;
                headings.forEach(heading => {
                    const level = parseInt(heading.tagName[1]);
                    if (level > lastLevel + 1 && lastLevel !== 0) {
                        hierarchyIssues++;
                        results.warnings.push({
                            element: heading.tagName.toLowerCase(),
                            issue: 'Skipped heading level',
                            wcag: '1.3.1',
                            level: 'A',
                            impact: 'moderate'
                        });
                    }
                    lastLevel = level;
                });
                if (hierarchyIssues > 0) {
                    results.score -= hierarchyIssues;
                }

                // Check form labels
                const inputs = document.querySelectorAll('input, select, textarea');
                let unlabeled = 0;
                inputs.forEach(input => {
                    if (input.type === 'hidden') return;
                    const label = document.querySelector(`label[for="${input.id}"]`);
                    if (!label && !input.getAttribute('aria-label') && !input.placeholder) {
                        unlabeled++;
                        results.errors.push({
                            element: input.tagName.toLowerCase(),
                            issue: 'Missing label',
                            wcag: '1.3.1',
                            level: 'A',
                            impact: 'critical'
                        });
                    }
                });
                if (unlabeled > 0) {
                    results.score -= unlabeled * 3;
                }

                // Check color contrast (simplified check)
                const textElements = document.querySelectorAll('p, span, div, a, button');
                let contrastIssues = 0;
                textElements.forEach(el => {
                    const style = window.getComputedStyle(el);
                    const bgColor = style.backgroundColor;
                    const color = style.color;

                    // Simple check for very light text on white or very dark text on black
                    if (bgColor === 'rgb(255, 255, 255)' && color === 'rgb(255, 255, 255)') {
                        contrastIssues++;
                    }
                });
                if (contrastIssues > 0) {
                    results.warnings.push({
                        element: 'text',
                        issue: `${contrastIssues} potential color contrast issues`,
                        wcag: '1.4.3',
                        level: 'AA',
                        impact: 'serious'
                    });
                    results.score -= 5;
                }

                // Check for keyboard accessibility
                const interactiveElements = document.querySelectorAll('a, button, input, select, textarea');
                let keyboardIssues = 0;
                interactiveElements.forEach(el => {
                    if (el.tabIndex < -1) {
                        keyboardIssues++;
                        results.errors.push({
                            element: el.tagName.toLowerCase(),
                            issue: 'Element not keyboard accessible',
                            wcag: '2.1.1',
                            level: 'A',
                            impact: 'critical'
                        });
                    }
                });
                if (keyboardIssues > 0) {
                    results.score -= keyboardIssues * 2;
                }

                // Additional checks for AA and AAA levels
                if (params.wcag_level === 'AA' || params.wcag_level === 'AAA') {
                    // Check for focus indicators
                    const focusableElements = document.querySelectorAll('a, button, input, select, textarea');
                    focusableElements.forEach(el => {
                        const style = window.getComputedStyle(el, ':focus');
                        if (style.outline === 'none' && !style.boxShadow) {
                            results.warnings.push({
                                element: el.tagName.toLowerCase(),
                                issue: 'Missing focus indicator',
                                wcag: '2.4.7',
                                level: 'AA',
                                impact: 'moderate'
                            });
                        }
                    });
                }

                results.score = Math.max(0, results.score);
                results.totalIssues = results.errors.length + results.warnings.length;

                return results;
            })();
            """

            result = await browser_session.evaluate(audit_js)

            # Generate accessibility report
            errors_html = ''.join([
                f'<div class="issue error"><strong>{e["element"]}</strong>: {e["issue"]} (WCAG {e["wcag"]} Level {e["level"]})</div>'
                for e in result.get('errors', [])
            ])

            warnings_html = ''.join([
                f'<div class="issue warning"><strong>{w["element"]}</strong>: {w["issue"]} (WCAG {w["wcag"]} Level {w["level"]})</div>'
                for w in result.get('warnings', [])
            ]) if params.include_warnings else ''

            score_color = '#28a745' if result['score'] >= 90 else '#ffc107' if result['score'] >= 70 else '#dc3545'

            report_html = f"""
            <html>
            <head>
                <title>Accessibility Audit Report</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                    .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; }}
                    h1 {{ color: #333; text-align: center; }}
                    .score-display {{ text-align: center; margin: 30px 0; }}
                    .score-circle {{ display: inline-block; width: 150px; height: 150px; border-radius: 50%; background: {score_color}; color: white; line-height: 150px; font-size: 48px; font-weight: bold; }}
                    .issues {{ margin: 20px 0; }}
                    .issue {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
                    .issue.error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
                    .issue.warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>♿ Accessibility Audit Report</h1>
                    <p style="text-align: center;">WCAG {params.wcag_level} Compliance Check</p>
                    <div class="score-display">
                        <div class="score-circle">{result['score']}%</div>
                    </div>
                    <div class="issues">
                        <h2>❌ Errors ({len(result.get('errors', []))})</h2>
                        {errors_html or '<p style="color: green;">No errors found!</p>'}
                    </div>
                    {('<div class="issues"><h2>⚠️ Warnings (' + str(len(result.get('warnings', []))) + ')</h2>' + (warnings_html or '<p style="color: green;">No warnings!</p>') + '</div>') if params.include_warnings else ''}
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p><strong>Total Issues:</strong> {result['totalIssues']}</p>
                        <p><strong>Tested:</strong> {result['url']}</p>
                        <p><strong>Time:</strong> {result['timestamp']}</p>
                    </div>
                </div>
            </body>
            </html>
            """

            await browser_session.evaluate(f"document.body.innerHTML = `{report_html}`;")
            return result

        # Tool 4: SEO Analyzer
        @self.manager.tools.registry.action(
            'Analyze page SEO and provide optimization recommendations',
            param_model=SEOAnalyzerParams
        )
        async def seo_analyzer(params: SEOAnalyzerParams, browser_session):
            """SEO analysis and recommendations"""

            seo_js = """
            (function() {
                const results = {
                    url: window.location.href,
                    timestamp: new Date().toISOString(),
                    score: 100,
                    issues: [],
                    recommendations: [],
                    metadata: {}
                };

                // Check meta tags
                if (""" + str('meta' in params.check_categories).lower() + """) {
                    const title = document.querySelector('title');
                    if (!title || !title.textContent) {
                        results.issues.push('Missing page title');
                        results.score -= 15;
                    } else {
                        results.metadata.title = title.textContent;
                        if (title.textContent.length < 30) {
                            results.recommendations.push('Title too short (recommended: 30-60 characters)');
                            results.score -= 5;
                        } else if (title.textContent.length > 60) {
                            results.recommendations.push('Title too long (recommended: 30-60 characters)');
                            results.score -= 3;
                        }
                    }

                    const metaDesc = document.querySelector('meta[name="description"]');
                    if (!metaDesc) {
                        results.issues.push('Missing meta description');
                        results.score -= 10;
                    } else {
                        results.metadata.description = metaDesc.content;
                        if (metaDesc.content.length < 120) {
                            results.recommendations.push('Meta description too short (recommended: 120-160 characters)');
                            results.score -= 3;
                        } else if (metaDesc.content.length > 160) {
                            results.recommendations.push('Meta description too long (recommended: 120-160 characters)');
                            results.score -= 2;
                        }
                    }

                    const viewport = document.querySelector('meta[name="viewport"]');
                    if (!viewport) {
                        results.issues.push('Missing viewport meta tag (mobile optimization)');
                        results.score -= 10;
                    }
                }

                // Check headings
                if (""" + str('headings' in params.check_categories).lower() + """) {
                    const h1s = document.querySelectorAll('h1');
                    if (h1s.length === 0) {
                        results.issues.push('No H1 tag found');
                        results.score -= 15;
                    } else if (h1s.length > 1) {
                        results.recommendations.push(`Multiple H1 tags found (${h1s.length}). Use only one H1 per page.`);
                        results.score -= 5;
                    }
                    results.metadata.h1Count = h1s.length;

                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    results.metadata.totalHeadings = headings.length;
                }

                // Check images
                if (""" + str('images' in params.check_categories).lower() + """) {
                    const images = document.querySelectorAll('img');
                    let missingAlt = 0;
                    let largImages = 0;
                    images.forEach(img => {
                        if (!img.alt) missingAlt++;
                        // Check for large images (simplified)
                        if (img.naturalWidth > 1920 || img.naturalHeight > 1080) {
                            largImages++;
                        }
                    });
                    if (missingAlt > 0) {
                        results.issues.push(`${missingAlt} images missing alt text`);
                        results.score -= missingAlt * 2;
                    }
                    if (largImages > 0) {
                        results.recommendations.push(`${largImages} images are very large. Consider optimizing.`);
                        results.score -= largImages;
                    }
                    results.metadata.totalImages = images.length;
                    results.metadata.imagesWithoutAlt = missingAlt;
                }

                // Check links
                if (""" + str('links' in params.check_categories).lower() + """) {
                    const links = document.querySelectorAll('a');
                    let nofollow = 0;
                    let external = 0;
                    let broken = 0;
                    links.forEach(link => {
                        if (link.rel && link.rel.includes('nofollow')) nofollow++;
                        if (link.hostname && link.hostname !== window.location.hostname) external++;
                        if (!link.href || link.href === '#') broken++;
                    });
                    results.metadata.totalLinks = links.length;
                    results.metadata.nofollowLinks = nofollow;
                    results.metadata.externalLinks = external;
                    if (broken > 0) {
                        results.issues.push(`${broken} broken or empty links found`);
                        results.score -= broken * 2;
                    }
                }

                // Add recommendations if requested
                if (""" + str(params.include_recommendations).lower() + """) {
                    // Check for schema markup
                    const jsonLd = document.querySelector('script[type="application/ld+json"]');
                    if (!jsonLd) {
                        results.recommendations.push('Add structured data (Schema.org) for better search results');
                    }

                    // Check for Open Graph tags
                    const ogTitle = document.querySelector('meta[property="og:title"]');
                    if (!ogTitle) {
                        results.recommendations.push('Add Open Graph tags for better social media sharing');
                    }

                    // Check page speed indicators
                    const scripts = document.querySelectorAll('script');
                    if (scripts.length > 15) {
                        results.recommendations.push(`Too many scripts (${scripts.length}). Consider combining or lazy loading.`);
                    }
                }

                results.score = Math.max(0, results.score);
                return results;
            })();
            """

            result = await browser_session.evaluate(seo_js)

            # Generate SEO report
            issues_html = ''.join([f'<li class="issue">{issue}</li>' for issue in result.get('issues', [])])
            recommendations_html = ''.join([f'<li class="recommendation">{rec}</li>' for rec in result.get('recommendations', [])])

            score_color = '#28a745' if result['score'] >= 80 else '#ffc107' if result['score'] >= 60 else '#dc3545'

            report_html = f"""
            <html>
            <head>
                <title>SEO Analysis Report</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: #f5f7fa; }}
                    .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #2c3e50; text-align: center; }}
                    .score {{ text-align: center; margin: 30px 0; }}
                    .score-value {{ font-size: 72px; font-weight: bold; color: {score_color}; }}
                    .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
                    .issue {{ color: #e74c3c; margin: 5px 0; }}
                    .recommendation {{ color: #f39c12; margin: 5px 0; }}
                    .metadata {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
                    .meta-item {{ padding: 10px; background: white; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔍 SEO Analysis Report</h1>
                    <div class="score">
                        <div class="score-value">{result['score']}%</div>
                        <p>SEO Score</p>
                    </div>

                    <div class="section">
                        <h2>❌ Issues Found ({len(result.get('issues', []))})</h2>
                        <ul>{issues_html or '<li style="color: green;">No critical issues found!</li>'}</ul>
                    </div>

                    {('<div class="section"><h2>💡 Recommendations (' + str(len(result.get('recommendations', []))) + ')</h2><ul>' + (recommendations_html or '<li style="color: green;">No additional recommendations!</li>') + '</ul></div>') if params.include_recommendations else ''}

                    <div class="section">
                        <h2>📊 Page Metadata</h2>
                        <div class="metadata">
                            <div class="meta-item"><strong>Title:</strong> {result['metadata'].get('title', 'N/A')[:60]}...</div>
                            <div class="meta-item"><strong>Description:</strong> {result['metadata'].get('description', 'N/A')[:100]}...</div>
                            <div class="meta-item"><strong>H1 Tags:</strong> {result['metadata'].get('h1Count', 0)}</div>
                            <div class="meta-item"><strong>Total Headings:</strong> {result['metadata'].get('totalHeadings', 0)}</div>
                            <div class="meta-item"><strong>Images:</strong> {result['metadata'].get('totalImages', 0)}</div>
                            <div class="meta-item"><strong>Links:</strong> {result['metadata'].get('totalLinks', 0)}</div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            await browser_session.evaluate(f"document.body.innerHTML = `{report_html}`;")
            return result

        print("Advanced tools registered successfully!")

    def get_advanced_tools_list(self) -> List[Dict[str, str]]:
        """Get list of all advanced tools"""
        return [
            {
                "name": "security_scanner",
                "description": "Perform security vulnerability scanning"
            },
            {
                "name": "extract_structured_data",
                "description": "Extract structured data (tables, JSON-LD, prices, emails, phones)"
            },
            {
                "name": "accessibility_audit",
                "description": "Perform WCAG accessibility audit"
            },
            {
                "name": "seo_analyzer",
                "description": "Analyze SEO and provide recommendations"
            }
        ]


# Example usage
if __name__ == "__main__":
    import asyncio
    from browser_use import ChatGoogle
    from browser_use.agent.service import Agent

    async def demo_advanced_tools():
        """Demonstrate advanced tools"""

        # Create custom tools manager
        manager = CustomToolsManager(include_defaults=True)

        # Extend with advanced tools
        advanced = AdvancedToolsExtension(manager)

        # Create LLM
        from dotenv import load_dotenv
        load_dotenv()

        llm = ChatGoogle(model="gemini-2.0-flash-exp")

        # Run comprehensive website analysis
        task = """
        Navigate to example.com and perform a comprehensive analysis:
        1. Run a security scan with moderate depth
        2. Extract all structured data from the page
        3. Perform an accessibility audit for WCAG AA compliance
        4. Analyze SEO and provide recommendations
        5. Use count_tools to show how many tools we have available
        """

        print("Running comprehensive website analysis with advanced tools...")
        agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
        await agent.run()
        await agent.close()

    asyncio.run(demo_advanced_tools())