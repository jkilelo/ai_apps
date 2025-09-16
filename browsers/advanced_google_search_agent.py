"""
Advanced Google Search Agent - Sophisticated search automation with AI reasoning
Demonstrates complex search techniques, operators, and multi-step research workflows
"""

import asyncio
import sys
import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright, Page, Browser
from agents.langgraph_wrapper import get_langgraph_llm
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
import operator

print("=" * 80)
print("ADVANCED GOOGLE SEARCH AGENT")
print(f"Timestamp: {datetime.now()}")
print("=" * 80)


# ============================================================================
# Search Types and Data Models
# ============================================================================

class SearchType(Enum):
    """Types of advanced searches."""
    ACADEMIC = "academic"
    NEWS = "news"
    COMPETITIVE = "competitive"
    TECHNICAL = "technical"
    TREND = "trend"
    SENTIMENT = "sentiment"
    FACT_CHECK = "fact_check"


@dataclass
class SearchResult:
    """Structured search result."""
    title: str
    url: str
    snippet: str
    source: str
    date: Optional[str] = None
    relevance_score: float = 0.0


@dataclass
class ResearchReport:
    """Compiled research report."""
    query: str
    search_type: SearchType
    total_results: int
    key_findings: List[str]
    sources: List[SearchResult]
    summary: str
    confidence_score: float
    timestamp: str


# ============================================================================
# Advanced Search Tools
# ============================================================================

class GoogleSearchTools:
    """Advanced Google search tools."""
    
    def __init__(self, page: Page):
        self.page = page
        self.search_history = []
    
    async def perform_search(self, query: str) -> bool:
        """Execute a Google search."""
        try:
            # Navigate to Google if not already there
            if "google.com" not in self.page.url:
                await self.page.goto("https://www.google.com", wait_until='domcontentloaded')
                await asyncio.sleep(2)
            
            # Find and fill search box
            search_box = await self.page.query_selector('textarea[name="q"], input[name="q"]')
            if search_box:
                await search_box.clear()
                await search_box.fill(query)
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_load_state('networkidle', timeout=10000)
                
                print(f"  [SEARCH] Executed: {query[:100]}...")
                self.search_history.append(query)
                return True
        except Exception as e:
            print(f"  [ERROR] Search failed: {e}")
        return False
    
    async def extract_results(self, limit: int = 10) -> List[SearchResult]:
        """Extract search results from current page."""
        results = []
        try:
            # Wait for results to load
            await self.page.wait_for_selector('div#search', timeout=5000)
            
            # Extract result elements
            result_elements = await self.page.query_selector_all('div.g')
            
            for element in result_elements[:limit]:
                try:
                    # Extract title
                    title_elem = await element.query_selector('h3')
                    title = await title_elem.text_content() if title_elem else ""
                    
                    # Extract URL
                    link_elem = await element.query_selector('a')
                    url = await link_elem.get_attribute('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = await element.query_selector('div[data-sncf="1"], div[data-sncf="2"], span.st')
                    if not snippet_elem:
                        snippet_elem = await element.query_selector('div.VwiC3b')
                    snippet = await snippet_elem.text_content() if snippet_elem else ""
                    
                    # Extract source (domain)
                    source = url.split('/')[2] if url and '/' in url else ""
                    
                    if title and url:
                        results.append(SearchResult(
                            title=title.strip(),
                            url=url,
                            snippet=snippet.strip() if snippet else "",
                            source=source
                        ))
                except:
                    continue
            
            print(f"  [EXTRACT] Found {len(results)} results")
        except Exception as e:
            print(f"  [ERROR] Extraction failed: {e}")
        
        return results
    
    async def apply_search_filters(self, time_range: str = None, site: str = None):
        """Apply advanced search filters."""
        try:
            if time_range:
                # Click on Tools
                tools_button = await self.page.query_selector('div[role="button"]:has-text("Tools")')
                if tools_button:
                    await tools_button.click()
                    await asyncio.sleep(1)
                    
                    # Select time range
                    time_button = await self.page.query_selector('div[aria-label*="time"]')
                    if time_button:
                        await time_button.click()
                        await asyncio.sleep(0.5)
                        
                        # Select specific time range
                        time_option = await self.page.query_selector(f'span:has-text("{time_range}")')
                        if time_option:
                            await time_option.click()
                            await asyncio.sleep(2)
                            print(f"  [FILTER] Applied time filter: {time_range}")
        except Exception as e:
            print(f"  [ERROR] Filter application failed: {e}")
    
    async def search_news(self, query: str) -> List[SearchResult]:
        """Search Google News."""
        try:
            # Click on News tab
            news_tab = await self.page.query_selector('a[href*="/search?"][href*="&tbm=nws"]')
            if not news_tab:
                # Try alternative selector
                news_tab = await self.page.query_selector('div[role="tab"]:has-text("News")')
            
            if news_tab:
                await news_tab.click()
                await self.page.wait_for_load_state('networkidle')
                print(f"  [NEWS] Switched to News search")
                return await self.extract_results()
        except Exception as e:
            print(f"  [ERROR] News search failed: {e}")
        return []
    
    async def search_scholar(self, query: str) -> List[SearchResult]:
        """Search Google Scholar for academic results."""
        try:
            await self.page.goto(f"https://scholar.google.com/scholar?q={query}", wait_until='domcontentloaded')
            await asyncio.sleep(2)
            
            results = []
            articles = await self.page.query_selector_all('div.gs_ri')
            
            for article in articles[:10]:
                try:
                    title_elem = await article.query_selector('h3.gs_rt a')
                    title = await title_elem.text_content() if title_elem else ""
                    url = await title_elem.get_attribute('href') if title_elem else ""
                    
                    snippet_elem = await article.query_selector('div.gs_rs')
                    snippet = await snippet_elem.text_content() if snippet_elem else ""
                    
                    source_elem = await article.query_selector('div.gs_a')
                    source = await source_elem.text_content() if source_elem else ""
                    
                    if title:
                        results.append(SearchResult(
                            title=title.strip(),
                            url=url,
                            snippet=snippet.strip()[:200],
                            source=source.strip()
                        ))
                except:
                    continue
            
            print(f"  [SCHOLAR] Found {len(results)} academic results")
            return results
        except Exception as e:
            print(f"  [ERROR] Scholar search failed: {e}")
        return []


# ============================================================================
# Advanced Search Strategies
# ============================================================================

class SearchStrategies:
    """Advanced search query strategies."""
    
    @staticmethod
    def build_exact_phrase_query(phrase: str) -> str:
        """Build exact phrase search query."""
        return f'"{phrase}"'
    
    @staticmethod
    def build_site_specific_query(query: str, site: str) -> str:
        """Build site-specific search query."""
        return f'{query} site:{site}'
    
    @staticmethod
    def build_exclusion_query(query: str, exclude_terms: List[str]) -> str:
        """Build query with exclusions."""
        exclusions = ' '.join([f'-{term}' for term in exclude_terms])
        return f'{query} {exclusions}'
    
    @staticmethod
    def build_wildcard_query(query: str) -> str:
        """Build query with wildcards."""
        return query.replace(' ', ' * ')
    
    @staticmethod
    def build_or_query(terms: List[str]) -> str:
        """Build OR query for multiple terms."""
        return ' OR '.join(terms)
    
    @staticmethod
    def build_date_range_query(query: str, after: str, before: str = None) -> str:
        """Build query with date range."""
        date_filter = f'after:{after}'
        if before:
            date_filter += f' before:{before}'
        return f'{query} {date_filter}'
    
    @staticmethod
    def build_filetype_query(query: str, filetype: str) -> str:
        """Build query for specific file type."""
        return f'{query} filetype:{filetype}'
    
    @staticmethod
    def build_related_sites_query(url: str) -> str:
        """Find sites related to a URL."""
        return f'related:{url}'
    
    @staticmethod
    def build_competitive_analysis_queries(company: str, competitors: List[str]) -> List[str]:
        """Build queries for competitive analysis."""
        queries = [
            f'"{company}" vs "{competitor}"' for competitor in competitors
        ]
        queries.append(f'"{company}" market share industry analysis')
        queries.append(f'"{company}" competitive advantage')
        queries.append(f'"{company}" SWOT analysis')
        return queries
    
    @staticmethod
    def build_sentiment_queries(topic: str) -> List[str]:
        """Build queries for sentiment analysis."""
        return [
            f'"{topic}" reviews',
            f'"{topic}" complaints',
            f'"{topic}" "love it" OR "hate it"',
            f'"{topic}" problems issues',
            f'"{topic}" satisfaction rating'
        ]


# ============================================================================
# AI-Powered Search Agent
# ============================================================================

class AdvancedSearchAgentState(TypedDict):
    """State for advanced search agent."""
    messages: Annotated[Sequence[Any], operator.add]
    research_goal: str
    search_type: str
    queries_executed: List[str]
    results_collected: List[Dict[str, Any]]
    analysis: str
    report: Optional[Dict[str, Any]]
    complete: bool


class AdvancedGoogleSearchAgent:
    """Advanced Google search agent with AI reasoning."""
    
    def __init__(self):
        print("\n[INIT] Creating Advanced Search Agent...")
        self.llm = get_langgraph_llm(temperature=0.4)
        self.browser = None
        self.page = None
        self.search_tools = None
        self.strategies = SearchStrategies()
        self.graph = self._build_graph()
        print("[INIT] Agent ready")
    
    def _build_graph(self):
        """Build the agent workflow."""
        workflow = StateGraph(AdvancedSearchAgentState)
        
        workflow.add_node("analyze_goal", self._analyze_research_goal)
        workflow.add_node("plan_searches", self._plan_search_queries)
        workflow.add_node("execute_search", self._execute_search)
        workflow.add_node("analyze_results", self._analyze_results)
        workflow.add_node("refine_search", self._refine_search)
        workflow.add_node("compile_report", self._compile_report)
        
        workflow.set_entry_point("analyze_goal")
        workflow.add_edge("analyze_goal", "plan_searches")
        workflow.add_edge("plan_searches", "execute_search")
        workflow.add_edge("execute_search", "analyze_results")
        
        workflow.add_conditional_edges(
            "analyze_results",
            self._should_refine,
            {
                "refine": "refine_search",
                "complete": "compile_report"
            }
        )
        
        workflow.add_edge("refine_search", "execute_search")
        workflow.add_edge("compile_report", END)
        
        return workflow.compile()
    
    async def _analyze_research_goal(self, state: AdvancedSearchAgentState) -> AdvancedSearchAgentState:
        """Analyze the research goal with AI."""
        print("\n[AGENT] Analyzing research goal...")
        
        goal = state["research_goal"]
        
        analysis_prompt = f"""Analyze this research goal and determine the best search strategy:

Research Goal: {goal}

Consider:
1. What type of information is needed (academic, news, technical, competitive, etc.)
2. Key search terms and concepts
3. Potential search operators to use (site:, filetype:, date ranges, etc.)
4. Whether multiple search queries would be beneficial
5. Any specific sources or domains to focus on

Provide a strategic analysis."""
        
        response = self.llm.invoke([
            SystemMessage(content="You are a search strategy expert."),
            HumanMessage(content=analysis_prompt)
        ])
        
        print(f"[AGENT] Strategy: {response.content[:200]}...")
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "analysis": response.content
        }
    
    async def _plan_search_queries(self, state: AdvancedSearchAgentState) -> AdvancedSearchAgentState:
        """Plan specific search queries."""
        print("\n[AGENT] Planning search queries...")
        
        planning_prompt = f"""Based on the research goal and analysis, create specific Google search queries:

Goal: {state['research_goal']}
Analysis: {state['analysis'][:500]}

Generate 3-5 sophisticated search queries using advanced operators like:
- Exact phrases with quotes
- site: for specific domains
- filetype: for documents
- OR for alternatives
- Minus sign for exclusions
- Date ranges with after:/before:

Format each query on a new line starting with QUERY:"""
        
        response = self.llm.invoke([
            SystemMessage(content="You are a Google search expert. Create advanced search queries."),
            HumanMessage(content=planning_prompt)
        ])
        
        # Extract queries from response
        queries = []
        for line in response.content.split('\n'):
            if 'QUERY:' in line:
                query = line.split('QUERY:')[-1].strip()
                queries.append(query)
        
        # If no queries found, create default ones
        if not queries:
            queries = [state['research_goal']]
        
        print(f"[AGENT] Planned {len(queries)} queries")
        for q in queries:
            print(f"  - {q[:80]}...")
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "queries_executed": queries
        }
    
    async def _execute_search(self, state: AdvancedSearchAgentState) -> AdvancedSearchAgentState:
        """Execute the search queries."""
        print("\n[AGENT] Executing searches...")
        
        if not self.search_tools:
            await self._initialize_browser()
        
        all_results = []
        
        for query in state["queries_executed"][:5]:  # Limit to 5 queries
            print(f"\n[SEARCH] Query: {query[:100]}...")
            
            # Perform search
            success = await self.search_tools.perform_search(query)
            
            if success:
                await asyncio.sleep(2)  # Be respectful to Google
                
                # Extract results
                results = await self.search_tools.extract_results(limit=5)
                
                # Store results with query context
                for result in results:
                    all_results.append({
                        "query": query,
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "source": result.source
                    })
        
        print(f"[AGENT] Collected {len(all_results)} total results")
        
        return {
            **state,
            "results_collected": all_results
        }
    
    async def _analyze_results(self, state: AdvancedSearchAgentState) -> AdvancedSearchAgentState:
        """Analyze search results with AI."""
        print("\n[AGENT] Analyzing results...")
        
        if not state["results_collected"]:
            return {**state, "complete": True}
        
        analysis_prompt = f"""Analyze these search results for the research goal:

Goal: {state['research_goal']}

Results:
{json.dumps(state['results_collected'][:10], indent=2)[:3000]}

Provide:
1. Key findings
2. Information gaps
3. Reliability assessment
4. Whether more searching is needed

Respond with SUFFICIENT or NEEDS_MORE and explain."""
        
        response = self.llm.invoke([
            SystemMessage(content="You are analyzing search results for completeness."),
            HumanMessage(content=analysis_prompt)
        ])
        
        print(f"[AGENT] Analysis: {response.content[:200]}...")
        
        # Determine if complete
        complete = "SUFFICIENT" in response.content.upper() or len(state.get("queries_executed", [])) >= 3
        
        return {
            **state,
            "messages": state["messages"] + [response],
            "complete": complete
        }
    
    def _should_refine(self, state: AdvancedSearchAgentState) -> str:
        """Determine if search needs refinement."""
        if state.get("complete"):
            return "complete"
        return "refine"
    
    async def _refine_search(self, state: AdvancedSearchAgentState) -> AdvancedSearchAgentState:
        """Refine search based on initial results."""
        print("\n[AGENT] Refining search strategy...")
        
        refinement_prompt = f"""Based on initial results, create refined search queries:

Initial queries: {state['queries_executed']}
Results found: {len(state['results_collected'])}

Create 2-3 refined queries to fill information gaps.
Use different search operators or approaches.

Format with QUERY:"""
        
        response = self.llm.invoke([
            SystemMessage(content="You are refining search queries based on initial results."),
            HumanMessage(content=refinement_prompt)
        ])
        
        # Extract refined queries
        refined_queries = []
        for line in response.content.split('\n'):
            if 'QUERY:' in line:
                query = line.split('QUERY:')[-1].strip()
                refined_queries.append(query)
        
        print(f"[AGENT] Refined with {len(refined_queries)} new queries")
        
        return {
            **state,
            "queries_executed": state["queries_executed"] + refined_queries,
            "messages": state["messages"] + [response]
        }
    
    async def _compile_report(self, state: AdvancedSearchAgentState) -> AdvancedSearchAgentState:
        """Compile final research report."""
        print("\n[AGENT] Compiling research report...")
        
        report_prompt = f"""Compile a comprehensive research report:

Research Goal: {state['research_goal']}
Queries Executed: {len(state['queries_executed'])}
Results Collected: {len(state['results_collected'])}

Results Summary:
{json.dumps(state['results_collected'][:15], indent=2)[:3000]}

Create a structured report with:
1. Executive Summary
2. Key Findings (bullet points)
3. Detailed Analysis
4. Sources and References
5. Confidence Level (High/Medium/Low)
6. Recommendations for further research"""
        
        response = self.llm.invoke([
            SystemMessage(content="You are compiling a research report from search results."),
            HumanMessage(content=report_prompt)
        ])
        
        # Create structured report
        report = ResearchReport(
            query=state['research_goal'],
            search_type=SearchType.ACADEMIC,
            total_results=len(state['results_collected']),
            key_findings=self._extract_key_findings(response.content),
            sources=[],  # Would convert results to SearchResult objects
            summary=response.content,
            confidence_score=0.8,
            timestamp=datetime.now().isoformat()
        )
        
        print("[AGENT] Report compiled")
        
        return {
            **state,
            "report": {
                "summary": response.content,
                "total_results": len(state['results_collected']),
                "queries": state['queries_executed'],
                "timestamp": datetime.now().isoformat()
            },
            "complete": True
        }
    
    def _extract_key_findings(self, content: str) -> List[str]:
        """Extract key findings from content."""
        findings = []
        for line in content.split('\n'):
            if line.strip().startswith(('-', '•', '*')) and len(line.strip()) > 10:
                findings.append(line.strip()[1:].strip())
        return findings[:5]
    
    async def _initialize_browser(self):
        """Initialize browser and search tools."""
        print("[SETUP] Initializing browser...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = await context.new_page()
        self.search_tools = GoogleSearchTools(self.page)
        print("[SETUP] Browser ready")
    
    async def research(self, goal: str) -> Dict[str, Any]:
        """Execute research with advanced Google searches."""
        initial_state = {
            "messages": [],
            "research_goal": goal,
            "search_type": "",
            "queries_executed": [],
            "results_collected": [],
            "analysis": "",
            "report": None,
            "complete": False
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            return result.get("report", {})
        finally:
            if self.browser:
                await self.browser.close()


# ============================================================================
# Demonstration Functions
# ============================================================================

async def demo_competitive_analysis():
    """Demo competitive analysis search."""
    print("\n" + "=" * 80)
    print("DEMO: Competitive Analysis")
    print("=" * 80)
    
    agent = AdvancedGoogleSearchAgent()
    
    goal = """
    Analyze the competitive landscape for Tesla vs other electric vehicle manufacturers.
    Focus on market share, technology advantages, and recent developments in 2024.
    """
    
    report = await agent.research(goal)
    
    print("\n[REPORT] Competitive Analysis")
    print("-" * 40)
    print(f"Total Results: {report.get('total_results', 0)}")
    print(f"Queries Used: {len(report.get('queries', []))}")
    print("\nSummary:")
    print(report.get('summary', 'No summary')[:1000])


async def demo_academic_research():
    """Demo academic research search."""
    print("\n" + "=" * 80)
    print("DEMO: Academic Research")
    print("=" * 80)
    
    agent = AdvancedGoogleSearchAgent()
    
    goal = """
    Find recent academic research on "machine learning in healthcare" from 2023-2024.
    Look for peer-reviewed papers, particularly from Nature, Science, or IEEE journals.
    Focus on diagnostic applications and clinical trials.
    """
    
    report = await agent.research(goal)
    
    print("\n[REPORT] Academic Research")
    print("-" * 40)
    print(f"Total Results: {report.get('total_results', 0)}")
    print("\nKey Findings:")
    summary = report.get('summary', '')
    if summary:
        print(summary[:1000])


async def demo_trend_analysis():
    """Demo trend analysis search."""
    print("\n" + "=" * 80)
    print("DEMO: Trend Analysis")
    print("=" * 80)
    
    agent = AdvancedGoogleSearchAgent()
    
    goal = """
    Analyze trends in "artificial intelligence adoption" across different industries in 2024.
    Include statistics, growth rates, and expert predictions.
    Compare adoption rates in healthcare, finance, and manufacturing.
    """
    
    report = await agent.research(goal)
    
    print("\n[REPORT] Trend Analysis")
    print("-" * 40)
    print(f"Total Results: {report.get('total_results', 0)}")
    print("\nAnalysis:")
    print(report.get('summary', 'No analysis')[:1000])


async def demo_fact_checking():
    """Demo fact-checking search."""
    print("\n" + "=" * 80)
    print("DEMO: Fact Checking")
    print("=" * 80)
    
    agent = AdvancedGoogleSearchAgent()
    
    goal = """
    Fact-check: "Python is the most popular programming language in 2024"
    Find authoritative sources like Stack Overflow surveys, GitHub statistics, 
    TIOBE index, and developer surveys. Include both supporting and contradicting evidence.
    """
    
    report = await agent.research(goal)
    
    print("\n[REPORT] Fact Check Results")
    print("-" * 40)
    print(report.get('summary', 'No results')[:1000])


async def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("ADVANCED GOOGLE SEARCH AGENT DEMONSTRATIONS")
    print("=" * 80)
    print("\nThis demonstration shows sophisticated search capabilities:")
    print("- Advanced search operators")
    print("- Multi-query research workflows")
    print("- AI-powered result analysis")
    print("- Automatic report generation")
    
    # Run demos
    await demo_competitive_analysis()
    await asyncio.sleep(3)
    
    await demo_academic_research()
    await asyncio.sleep(3)
    
    await demo_trend_analysis()
    await asyncio.sleep(3)
    
    await demo_fact_checking()
    
    print("\n" + "=" * 80)
    print("DEMONSTRATIONS COMPLETE")
    print("=" * 80)
    print("\nCapabilities Demonstrated:")
    print("- Complex multi-query searches")
    print("- Advanced Google operators")
    print("- Intelligent query refinement")
    print("- Comprehensive result analysis")
    print("- Structured report generation")
    print("- Various research types (competitive, academic, trends, fact-checking)")


if __name__ == "__main__":
    print("\nStarting Advanced Google Search Agent...")
    asyncio.run(main())