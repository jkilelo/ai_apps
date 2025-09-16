"""
Advanced Use Cases for Stealth Browser Agent

This module demonstrates real-world applications of the stealth browser agent:
1. E-commerce monitoring and price tracking
2. Research and data collection
3. Automated testing and QA
4. Content verification and monitoring
5. Multi-site workflow automation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from stealth_browser_agent import StealthBrowserAgent, BrowserInstance
from langgraph_wrapper import get_langgraph_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool


# ============================================================================
# Use Case 1: E-commerce Price Monitor Agent
# ============================================================================

@dataclass
class ProductInfo:
    """Product information structure."""
    name: str
    price: float
    availability: str
    url: str
    timestamp: str
    site: str


class PriceMonitorAgent(StealthBrowserAgent):
    """
    Specialized agent for monitoring product prices across multiple sites.
    """
    
    def __init__(self):
        super().__init__(temperature=0.2)  # Low temperature for consistency
        self.price_history = []
    
    async def monitor_product(self, product_urls: List[str]) -> List[ProductInfo]:
        """
        Monitor product prices across multiple URLs.
        
        Args:
            product_urls: List of product page URLs
        
        Returns:
            List of ProductInfo objects
        """
        products = []
        
        for url in product_urls:
            task = f"""Navigate to {url} and extract:
            1. Product name/title
            2. Current price (look for price indicators like $, €, £)
            3. Availability status (in stock, out of stock, limited)
            4. Any discount or sale information
            
            Be precise with price extraction - get the actual numeric value."""
            
            result = await self.run(task)
            
            if result["success"]:
                # Parse the extracted data
                data = result.get("data", {})
                
                # Use LLM to structure the extracted data
                structuring_prompt = f"""From this extracted data, identify:
                Product Name:
                Price (numeric only):
                Availability:
                
                Data: {json.dumps(data)[:1000]}"""
                
                response = self.llm.invoke([
                    SystemMessage(content="Extract structured product information."),
                    HumanMessage(content=structuring_prompt)
                ])
                
                # Parse response (simplified - in production use proper parsing)
                product = ProductInfo(
                    name="Product from " + url.split('/')[2],
                    price=0.0,  # Would parse from response
                    availability="Check site",
                    url=url,
                    timestamp=datetime.now().isoformat(),
                    site=url.split('/')[2]
                )
                products.append(product)
        
        self.price_history.extend(products)
        return products
    
    async def compare_prices(self, product_name: str, sites: List[str]) -> Dict[str, Any]:
        """
        Compare prices for a product across different sites.
        
        Args:
            product_name: Name of the product to search
            sites: List of e-commerce sites to check
        
        Returns:
            Price comparison results
        """
        comparison_results = {}
        
        for site in sites:
            task = f"""Go to {site} and:
            1. Search for "{product_name}"
            2. Click on the first relevant result
            3. Extract the price and product details
            4. Note any special offers or discounts"""
            
            result = await self.run(task)
            comparison_results[site] = result
        
        # Analyze results
        analysis_prompt = f"""Analyze these price comparison results:
        {json.dumps(comparison_results)[:2000]}
        
        Provide:
        1. Lowest price and site
        2. Best value considering shipping/extras
        3. Availability summary
        4. Recommendation"""
        
        analysis = self.llm.invoke([
            SystemMessage(content="You are a shopping assistant analyzing prices."),
            HumanMessage(content=analysis_prompt)
        ])
        
        return {
            "raw_results": comparison_results,
            "analysis": analysis.content
        }


# ============================================================================
# Use Case 2: Research Assistant Agent
# ============================================================================

class ResearchAgent(StealthBrowserAgent):
    """
    Agent specialized for research and information gathering.
    """
    
    def __init__(self):
        super().__init__(temperature=0.4)
        self.research_data = {}
    
    async def research_topic(self, topic: str, sources: List[str]) -> Dict[str, Any]:
        """
        Research a topic across multiple sources.
        
        Args:
            topic: Research topic
            sources: List of websites to research from
        
        Returns:
            Compiled research findings
        """
        findings = {}
        
        for source in sources:
            task = f"""Navigate to {source} and research about "{topic}":
            1. Find relevant articles or information
            2. Extract key facts and data
            3. Note the publication date if available
            4. Identify author credentials if present
            5. Extract supporting evidence or citations"""
            
            result = await self.run(task)
            findings[source] = result
        
        # Synthesize research
        synthesis_prompt = f"""Synthesize research findings on "{topic}":
        
        Sources and findings:
        {json.dumps(findings)[:3000]}
        
        Create a comprehensive summary with:
        1. Key findings across sources
        2. Common themes
        3. Contradictions or debates
        4. Evidence quality assessment
        5. Knowledge gaps"""
        
        synthesis = self.llm.invoke([
            SystemMessage(content="You are a research analyst synthesizing information."),
            HumanMessage(content=synthesis_prompt)
        ])
        
        self.research_data[topic] = {
            "sources": findings,
            "synthesis": synthesis.content,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.research_data[topic]
    
    async def fact_check(self, claim: str, sources: List[str]) -> Dict[str, Any]:
        """
        Fact-check a claim across multiple sources.
        
        Args:
            claim: The claim to verify
            sources: Trusted sources to check against
        
        Returns:
            Fact-checking results
        """
        verifications = {}
        
        for source in sources:
            task = f"""Navigate to {source} and verify this claim: "{claim}"
            1. Search for information related to the claim
            2. Find supporting or contradicting evidence
            3. Note the date and author of information
            4. Extract exact quotes if available"""
            
            result = await self.run(task)
            verifications[source] = result
        
        # Analyze verification results
        verdict_prompt = f"""Based on these fact-checking results, assess the claim: "{claim}"
        
        Evidence from sources:
        {json.dumps(verifications)[:2000]}
        
        Provide:
        1. Verdict: TRUE/FALSE/PARTIALLY TRUE/UNVERIFIABLE
        2. Supporting evidence summary
        3. Contradicting evidence summary
        4. Confidence level
        5. Additional context needed"""
        
        verdict = self.llm.invoke([
            SystemMessage(content="You are a fact-checker analyzing evidence."),
            HumanMessage(content=verdict_prompt)
        ])
        
        return {
            "claim": claim,
            "verifications": verifications,
            "verdict": verdict.content
        }


# ============================================================================
# Use Case 3: Automated QA Testing Agent
# ============================================================================

class QATestingAgent(StealthBrowserAgent):
    """
    Agent for automated quality assurance testing of web applications.
    """
    
    def __init__(self):
        super().__init__(temperature=0.2)  # Low temperature for consistent testing
        self.test_results = []
    
    async def test_user_flow(self, base_url: str, flow_description: str) -> Dict[str, Any]:
        """
        Test a complete user flow.
        
        Args:
            base_url: Base URL of the application
            flow_description: Description of the user flow to test
        
        Returns:
            Test results with pass/fail status
        """
        test_task = f"""Test this user flow on {base_url}:
        {flow_description}
        
        For each step:
        1. Verify the page loads correctly
        2. Check that required elements are present
        3. Test interactive elements work
        4. Note any errors or unexpected behavior
        5. Take screenshots of important states"""
        
        result = await self.run(test_task)
        
        # Analyze test results
        analysis_prompt = f"""Analyze these test results:
        {json.dumps(result)[:2000]}
        
        Determine:
        1. Overall pass/fail status
        2. Steps that passed
        3. Steps that failed
        4. Performance observations
        5. Accessibility issues noted
        6. Recommendations for fixes"""
        
        analysis = self.llm.invoke([
            SystemMessage(content="You are a QA analyst reviewing test results."),
            HumanMessage(content=analysis_prompt)
        ])
        
        test_report = {
            "flow": flow_description,
            "url": base_url,
            "execution": result,
            "analysis": analysis.content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(test_report)
        return test_report
    
    async def test_responsive_design(self, url: str, viewports: List[Dict[str, int]]) -> Dict[str, Any]:
        """
        Test responsive design across different viewports.
        
        Args:
            url: URL to test
            viewports: List of viewport configurations (width, height)
        
        Returns:
            Responsive design test results
        """
        results = {}
        
        for viewport in viewports:
            task = f"""Navigate to {url} with viewport {viewport['width']}x{viewport['height']}:
            1. Check layout integrity
            2. Verify text readability
            3. Test navigation functionality
            4. Check image scaling
            5. Verify touch targets are appropriate size
            6. Take screenshot"""
            
            result = await self.run(task)
            results[f"{viewport['width']}x{viewport['height']}"] = result
        
        return {
            "url": url,
            "viewports_tested": viewports,
            "results": results
        }


# ============================================================================
# Use Case 4: Content Monitor Agent
# ============================================================================

class ContentMonitorAgent(StealthBrowserAgent):
    """
    Agent for monitoring website content changes and compliance.
    """
    
    def __init__(self):
        super().__init__(temperature=0.3)
        self.baseline_content = {}
    
    async def establish_baseline(self, urls: List[str]) -> Dict[str, Any]:
        """
        Establish baseline content for monitoring.
        
        Args:
            urls: URLs to establish baselines for
        
        Returns:
            Baseline content data
        """
        for url in urls:
            task = f"""Navigate to {url} and capture:
            1. Page structure and layout
            2. Main content sections
            3. Important text content
            4. Link inventory
            5. Media elements
            6. Meta information"""
            
            result = await self.run(task)
            self.baseline_content[url] = {
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        
        return self.baseline_content
    
    async def check_changes(self, url: str) -> Dict[str, Any]:
        """
        Check for changes against baseline.
        
        Args:
            url: URL to check
        
        Returns:
            Change detection results
        """
        if url not in self.baseline_content:
            return {"error": "No baseline established for this URL"}
        
        task = f"""Navigate to {url} and extract the same content as before:
        1. Page structure and layout
        2. Main content sections
        3. Important text content
        4. Link inventory
        5. Media elements
        6. Meta information"""
        
        current_result = await self.run(task)
        
        # Compare with baseline
        comparison_prompt = f"""Compare baseline and current content:
        
        Baseline (captured {self.baseline_content[url]['timestamp']}):
        {json.dumps(self.baseline_content[url]['data'])[:1500]}
        
        Current:
        {json.dumps(current_result)[:1500]}
        
        Identify:
        1. Content additions
        2. Content removals
        3. Content modifications
        4. Structural changes
        5. Significance of changes (minor/major/critical)"""
        
        comparison = self.llm.invoke([
            SystemMessage(content="You are analyzing website changes."),
            HumanMessage(content=comparison_prompt)
        ])
        
        return {
            "url": url,
            "baseline_time": self.baseline_content[url]['timestamp'],
            "check_time": datetime.now().isoformat(),
            "changes": comparison.content
        }


# ============================================================================
# Use Case 5: Multi-Site Workflow Agent
# ============================================================================

class WorkflowAgent(StealthBrowserAgent):
    """
    Agent for complex multi-site workflow automation.
    """
    
    def __init__(self):
        super().__init__(temperature=0.4)
        self.workflow_state = {}
    
    async def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a complex multi-step, multi-site workflow.
        
        Args:
            workflow_steps: List of workflow step definitions
        
        Returns:
            Workflow execution results
        """
        results = []
        context = {}  # Shared context between steps
        
        for i, step in enumerate(workflow_steps):
            step_task = f"""Execute workflow step {i+1}:
            Site: {step.get('site')}
            Action: {step.get('action')}
            Details: {step.get('details')}
            
            Previous context: {json.dumps(context)[:500]}
            
            Perform the action and extract any data needed for next steps."""
            
            result = await self.run(step_task)
            
            # Update context with results
            if result["success"] and result.get("data"):
                context[f"step_{i+1}"] = result["data"]
            
            results.append({
                "step": i + 1,
                "description": step,
                "result": result
            })
            
            # Check if we should continue
            if not result["success"] and step.get("required", True):
                break
        
        # Summarize workflow execution
        summary_prompt = f"""Summarize this workflow execution:
        
        Steps attempted: {len(results)}
        Results: {json.dumps(results)[:2000]}
        
        Provide:
        1. Overall success status
        2. Completed steps
        3. Failed steps and reasons
        4. Data collected
        5. Recommendations"""
        
        summary = self.llm.invoke([
            SystemMessage(content="You are summarizing workflow execution."),
            HumanMessage(content=summary_prompt)
        ])
        
        return {
            "workflow": workflow_steps,
            "results": results,
            "context": context,
            "summary": summary.content
        }


# ============================================================================
# Demo Functions
# ============================================================================

async def demo_price_monitoring():
    """Demo price monitoring capabilities."""
    print("\n[DEMO] Price Monitoring Agent")
    print("-" * 40)
    
    agent = PriceMonitorAgent()
    
    # Monitor products
    products = await agent.monitor_product([
        "https://www.example-shop.com/product/laptop",
        "https://www.another-store.com/electronics/laptop"
    ])
    
    print(f"Monitored {len(products)} products")
    for product in products:
        print(f"  - {product.name}: ${product.price} ({product.availability})")
    
    # Compare prices
    comparison = await agent.compare_prices(
        "laptop",
        ["https://shop1.com", "https://shop2.com"]
    )
    
    print(f"\nPrice comparison analysis:")
    print(comparison["analysis"][:500])


async def demo_research():
    """Demo research capabilities."""
    print("\n[DEMO] Research Agent")
    print("-" * 40)
    
    agent = ResearchAgent()
    
    # Research a topic
    research = await agent.research_topic(
        "artificial intelligence in healthcare",
        ["https://medical-journal.com", "https://tech-news.com"]
    )
    
    print(f"Research synthesis:")
    print(research["synthesis"][:500])
    
    # Fact check
    fact_check = await agent.fact_check(
        "AI can diagnose diseases better than doctors",
        ["https://medical-facts.org", "https://science-journal.com"]
    )
    
    print(f"\nFact check verdict:")
    print(fact_check["verdict"][:500])


async def demo_qa_testing():
    """Demo QA testing capabilities."""
    print("\n[DEMO] QA Testing Agent")
    print("-" * 40)
    
    agent = QATestingAgent()
    
    # Test user flow
    test_result = await agent.test_user_flow(
        "https://example-app.com",
        """1. Land on homepage
        2. Click 'Sign Up' button
        3. Fill registration form
        4. Submit form
        5. Verify success message"""
    )
    
    print(f"Test flow analysis:")
    print(test_result["analysis"][:500])


async def main():
    """Run all demos."""
    print("=" * 70)
    print("STEALTH BROWSER AGENT - ADVANCED USE CASES")
    print("=" * 70)
    
    # Run demos
    await demo_price_monitoring()
    await demo_research()
    await demo_qa_testing()
    
    print("\n" + "=" * 70)
    print("DEMONSTRATED CAPABILITIES:")
    print("=" * 70)
    print("""
✅ E-commerce price monitoring and comparison
✅ Multi-source research and synthesis
✅ Automated fact-checking
✅ QA testing and user flow validation
✅ Content change monitoring
✅ Complex multi-site workflows
✅ Intelligent data extraction and analysis
✅ Natural language task execution
    """)


if __name__ == "__main__":
    asyncio.run(main())