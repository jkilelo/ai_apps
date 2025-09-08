#!/usr/bin/env python3
"""
Fixed Academic Research Assistant with Enhanced Anti-Detection
This version includes better handling for Google Scholar's anti-bot measures
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re
from urllib.parse import quote
import random
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


@dataclass
class AcademicPaper:
    """Structured academic paper data"""
    title: str
    authors: List[str]
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    abstract: str = ""
    citation_count: Optional[int] = None
    h_index: Optional[int] = None
    doi: Optional[str] = None
    url: str = ""
    pdf_url: Optional[str] = None
    keywords: List[str] = None
    research_area: Optional[str] = None
    impact_factor: Optional[float] = None
    cited_by_url: Optional[str] = None
    related_articles_url: Optional[str] = None
    bibtex: Optional[str] = None
    source: str = "Google Scholar"
    relevance_score: float = 0.0
    extracted_at: str = ""
    
    def __post_init__(self):
        if self.authors is None:
            self.authors = []
        if self.keywords is None:
            self.keywords = []
        if not self.extracted_at:
            self.extracted_at = datetime.now().isoformat()


class FixedAcademicResearchAssistant:
    """AI-powered academic research automation with enhanced anti-detection"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/academic_research")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"academic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_google_scholar_with_fallback(self, query: str, max_papers: int = 10) -> List[AcademicPaper]:
        """Search Google Scholar with multiple fallback strategies"""
        logger.info(f"[ACADEMIC] Starting enhanced search for: {query}")
        
        # First attempt: Direct Google Scholar with stealth
        papers = await self.search_google_scholar_stealth(query, max_papers)
        
        if not papers:
            logger.warning("[FALLBACK] Google Scholar blocked, trying alternative approach...")
            # Second attempt: Use regular Google with 'site:scholar.google.com' operator
            papers = await self.search_via_google(query, max_papers)
        
        if not papers:
            logger.warning("[FALLBACK] Trying semantic scholar as alternative...")
            # Third attempt: Use Semantic Scholar as fallback
            papers = await self.search_semantic_scholar(query, max_papers)
        
        return papers
    
    async def search_google_scholar_stealth(self, query: str, max_papers: int = 10) -> List[AcademicPaper]:
        """Search Google Scholar with enhanced stealth measures"""
        logger.info(f"[STEALTH] Attempting Google Scholar search with anti-detection measures")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Use more natural search pattern
        search_url = f"https://scholar.google.com"
        
        task = f"""
        IMPORTANT: Act like a human researcher browsing Google Scholar naturally.
        
        1. First, navigate to the Google Scholar homepage
        2. Wait 2-3 seconds (simulate reading the page)
        3. Look for the search box carefully
        4. Click on the search box to focus it
        5. Type the search query slowly and naturally: '{query}'
        6. Press Enter to search
        7. Wait for results to load completely
        
        If you see "Loading..." or "The system can't perform the operation now":
        - This means Google has detected automation
        - Try refreshing the page once
        - If it persists, note this as a blocking message
        
        If search results appear successfully:
        - Extract information from the first {max_papers} papers
        - For each paper, collect:
          * Complete paper title
          * All listed authors 
          * Publication year
          * Journal/Conference name
          * Number of citations ("Cited by X")
          * Any available links
        
        Move the mouse naturally between actions.
        Scroll slowly when viewing results.
        Take your time - don't rush through the page.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=False,  # Run with GUI for better success rate
            max_steps=25,
            timeout=180000,  # 3 minutes timeout
            screenshot_on_error=True,
            viewport_width=1920,
            viewport_height=1080
        )
        
        try:
            # Add random initial delay
            await asyncio.sleep(random.uniform(2, 4))
            
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Check if we got blocked
            summary = result.get('summary', '')
            if 'loading' in summary.lower() or "can't perform" in summary.lower() or 'blocked' in summary.lower():
                logger.warning("[BLOCKED] Google Scholar detected automation")
                return []
            
            papers = await self._parse_academic_papers(
                summary,
                result.get('extracted_data', {}),
                query
            )
            
            logger.info(f"[SUCCESS] Found {len(papers)} papers via Google Scholar")
            return papers
            
        except Exception as e:
            logger.error(f"[ERROR] Google Scholar search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def search_via_google(self, query: str, max_papers: int = 10) -> List[AcademicPaper]:
        """Search for academic papers using regular Google"""
        logger.info(f"[FALLBACK] Using Google search for academic papers")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Use Google with academic search operators
        search_query = f'{query} site:scholar.google.com OR site:researchgate.net OR site:arxiv.org OR filetype:pdf'
        search_url = f"https://www.google.com/search?q={quote(search_query)}"
        
        task = f"""
        Search Google for academic papers about '{query}'.
        
        Look for:
        1. Links to Google Scholar papers
        2. ResearchGate publications
        3. ArXiv papers
        4. Direct PDF links to academic papers
        
        For each result (up to {max_papers}):
        - Extract the paper title
        - Extract author names if visible
        - Note the source website
        - Get the URL
        - Extract any visible metadata (year, journal, citations)
        
        Focus on academic sources only.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=15,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            papers = await self._parse_google_results(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                query
            )
            
            logger.info(f"[SUCCESS] Found {len(papers)} papers via Google")
            return papers
            
        except Exception as e:
            logger.error(f"[ERROR] Google search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def search_semantic_scholar(self, query: str, max_papers: int = 10) -> List[AcademicPaper]:
        """Search Semantic Scholar as an alternative to Google Scholar"""
        logger.info(f"[ALTERNATIVE] Using Semantic Scholar for: {query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        search_url = f"https://www.semanticscholar.org/search?q={quote(query)}"
        
        task = f"""
        Search Semantic Scholar for papers about '{query}'.
        
        Extract from the first {max_papers} papers:
        1. Paper title
        2. All author names
        3. Publication year
        4. Venue/Journal
        5. Citation count
        6. Abstract if visible
        7. Paper URL
        8. PDF link if available
        
        Semantic Scholar is more bot-friendly, so extraction should work well.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=15,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            papers = await self._parse_semantic_scholar(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                query
            )
            
            logger.info(f"[SUCCESS] Found {len(papers)} papers via Semantic Scholar")
            return papers
            
        except Exception as e:
            logger.error(f"[ERROR] Semantic Scholar search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def _parse_academic_papers(self, summary: str, extracted_data: dict, query: str) -> List[AcademicPaper]:
        """Parse academic papers from AI extraction"""
        papers = []
        
        # Simple parsing based on common patterns
        lines = summary.split('\n')
        current_paper = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for paper titles (usually longer lines with capital letters)
            if len(line) > 30 and line[0].isupper() and current_paper is None:
                current_paper = AcademicPaper(
                    title=line,
                    authors=[],
                    source="Google Scholar"
                )
            
            # Look for author names
            elif current_paper and ('et al' in line or ',' in line) and len(line) < 100:
                # This might be an author line
                authors = re.split(r'[,;&]', line)
                current_paper.authors = [a.strip() for a in authors if a.strip()]
            
            # Look for citation count
            elif current_paper and 'cited by' in line.lower():
                match = re.search(r'cited by (\d+)', line.lower())
                if match:
                    current_paper.citation_count = int(match.group(1))
            
            # Look for year
            elif current_paper and re.search(r'\b(19|20)\d{2}\b', line):
                match = re.search(r'\b(19|20)\d{2}\b', line)
                if match:
                    current_paper.publication_year = int(match.group(0))
            
            # When we have enough info, save the paper
            if current_paper and (current_paper.authors or current_paper.publication_year):
                papers.append(current_paper)
                current_paper = None
                
                if len(papers) >= 10:  # Limit to prevent too many results
                    break
        
        # Add last paper if exists
        if current_paper:
            papers.append(current_paper)
        
        return papers
    
    async def _parse_google_results(self, summary: str, extracted_data: dict, query: str) -> List[AcademicPaper]:
        """Parse papers from Google search results"""
        papers = []
        
        # Extract paper information from Google results
        # This is a simplified parser - could be enhanced with better patterns
        sections = summary.split('\n\n')
        
        for section in sections:
            if 'pdf' in section.lower() or 'scholar' in section.lower() or 'arxiv' in section.lower():
                # This might be an academic result
                lines = section.split('\n')
                if lines:
                    title = lines[0].strip()
                    if len(title) > 20:  # Reasonable title length
                        paper = AcademicPaper(
                            title=title,
                            authors=[],
                            source="Google Search"
                        )
                        
                        # Try to extract more info from remaining lines
                        for line in lines[1:]:
                            if re.search(r'\b(19|20)\d{2}\b', line):
                                match = re.search(r'\b(19|20)\d{2}\b', line)
                                if match:
                                    paper.publication_year = int(match.group(0))
                        
                        papers.append(paper)
        
        return papers[:10]  # Limit results
    
    async def _parse_semantic_scholar(self, summary: str, extracted_data: dict, query: str) -> List[AcademicPaper]:
        """Parse papers from Semantic Scholar results"""
        # Similar to Google Scholar parser but adapted for Semantic Scholar format
        return await self._parse_academic_papers(summary, extracted_data, query)
    
    def save_results(self, papers: List[AcademicPaper], query: str):
        """Save research results to file"""
        output_file = self.results_dir / f"{self.session_id}_{query[:30].replace(' ', '_')}.json"
        
        data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_papers": len(papers),
            "papers": [asdict(p) for p in papers]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[SAVED] Results saved to {output_file}")
        return output_file
    
    def display_results(self, papers: List[AcademicPaper]):
        """Display research results in a formatted way"""
        print("\n" + "="*80)
        print("ACADEMIC RESEARCH RESULTS")
        print("="*80)
        
        for i, paper in enumerate(papers, 1):
            print(f"\n[{i}] {paper.title}")
            if paper.authors:
                print(f"    Authors: {', '.join(paper.authors[:3])}")
                if len(paper.authors) > 3:
                    print(f"             ... and {len(paper.authors)-3} more")
            if paper.publication_year:
                print(f"    Year: {paper.publication_year}")
            if paper.journal:
                print(f"    Journal: {paper.journal}")
            if paper.citation_count:
                print(f"    Citations: {paper.citation_count}")
            print(f"    Source: {paper.source}")
            if paper.url:
                print(f"    URL: {paper.url}")
        
        print("\n" + "="*80)


async def main():
    """Run the academic research demo"""
    assistant = FixedAcademicResearchAssistant()
    
    print("\n" + "="*60)
    print("  FIXED ACADEMIC RESEARCH ASSISTANT")
    print("  AI-Powered Literature Search with Anti-Detection")
    print("="*60)
    
    print("\nThis enhanced version includes:")
    print("- Multiple fallback strategies if Google Scholar blocks")
    print("- Enhanced stealth measures for Google Scholar")
    print("- Alternative sources (Semantic Scholar, Google)")
    print("- Better error handling and recovery")
    
    print("\nExample queries:")
    print("1. Machine learning in healthcare")
    print("2. Climate change impacts on agriculture")
    print("3. Quantum computing algorithms")
    print("4. COVID-19 vaccine effectiveness")
    print("5. Artificial intelligence ethics")
    print("6. Custom query")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    queries = {
        "1": "machine learning healthcare diagnosis treatment",
        "2": "climate change agriculture food security",
        "3": "quantum computing algorithms optimization",
        "4": "COVID-19 vaccine effectiveness variants",
        "5": "artificial intelligence ethics bias fairness",
    }
    
    if choice == "6":
        query = input("Enter your research query: ").strip()
    elif choice in queries:
        query = queries[choice]
    else:
        print("Invalid choice. Using default query.")
        query = "artificial intelligence applications"
    
    max_papers = input("\nNumber of papers to retrieve (default 5): ").strip()
    max_papers = int(max_papers) if max_papers.isdigit() else 5
    
    print(f"\n[START] Searching for: '{query}'")
    print("[INFO] This may take 1-3 minutes depending on anti-bot measures...")
    
    # Run the search with fallback strategies
    papers = await assistant.search_google_scholar_with_fallback(query, max_papers)
    
    if papers:
        # Display results
        assistant.display_results(papers)
        
        # Save to file
        output_file = assistant.save_results(papers, query)
        print(f"\n[COMPLETE] Found {len(papers)} papers")
        print(f"[SAVED] Results saved to: {output_file}")
    else:
        print("\n[WARNING] No papers found. All search methods were blocked or failed.")
        print("Suggestions:")
        print("- Try running with headless=False to see what's happening")
        print("- Use a VPN or different network")
        print("- Try again later when rate limits reset")
        print("- Consider using academic APIs directly (requires API keys)")
    
    print("\n[DONE] Academic research session complete")


if __name__ == "__main__":
    asyncio.run(main())