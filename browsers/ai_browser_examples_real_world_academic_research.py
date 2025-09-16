#!/usr/bin/env python3
"""
Real-World Academic Research Assistant Automation

This example demonstrates autonomous academic research capabilities:
- Search Google Scholar for academic papers
- Extract paper details, citations, and abstracts
- Analyze research trends and citation patterns
- Generate literature reviews and bibliographies
- Track author networks and research impact
- Create structured research databases
- Export to academic formats (BibTeX, APA, etc.)

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended for text analysis)
- Working internet connection
- AI Browser v2.0.0 system components

USAGE:
    python examples/real_world_academic_research.py
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


class AcademicResearchAssistant:
    """AI-powered academic research automation"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/academic_research")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"academic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_google_scholar(self, query: str, max_papers: int = 10) -> List[AcademicPaper]:
        """Search Google Scholar for academic papers"""
        logger.info(f"[ACADEMIC] Searching Google Scholar for: {query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        search_url = f"https://scholar.google.com/scholar?q={quote(query)}"
        
        task = f"""
        Go to Google Scholar and search for academic papers on '{query}'.
        Extract information from the first {max_papers} papers:
        
        For each paper, collect:
        1. Complete paper title
        2. Authors (all listed authors)
        3. Publication year
        4. Journal/Conference name
        5. Abstract or summary text
        6. Number of citations ("Cited by X")
        7. DOI if available
        8. PDF link if available
        9. "Cited by" link URL
        10. "Related articles" link
        11. Any visible keywords or subject areas
        
        Focus on well-cited, recent papers from reputable sources.
        Handle any CAPTCHA or access restrictions gracefully.
        Extract complete bibliographic information for each paper.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=20,
            timeout=120000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            papers = await self._parse_academic_papers(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                query
            )
            
            logger.info(f"[SUCCESS] Found {len(papers)} academic papers")
            return papers
            
        except Exception as e:
            logger.error(f"[ERROR] Google Scholar search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def _parse_academic_papers(self, summary: str, extracted_data: dict, query: str) -> List[AcademicPaper]:
        """Parse academic papers from AI extraction"""
        browser = AIBrowser({"log_level": "INFO"})
        
        parsing_task = f"""
        Parse these academic papers from Google Scholar and structure the data:
        
        Search Query: {query}
        Raw Data: {summary}
        Additional Data: {json.dumps(extracted_data, default=str)}
        
        Extract individual papers with:
        1. Paper title (complete and accurate)
        2. Author list (all authors mentioned)
        3. Publication year (as integer)
        4. Journal/venue name
        5. Abstract or description
        6. Citation count (number after "Cited by")
        7. URLs for paper, citations, related articles
        8. DOI if mentioned
        
        Format as structured data for each paper found.
        Calculate relevance score based on citations and recency.
        """
        
        config = TaskConfig(
            task=parsing_task,
            url="https://www.example.com",
            headless=True,
            max_steps=5,
            timeout=60000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            parsed_summary = result.get('summary', '')
            papers = []
            
            # Split content into papers
            paper_sections = self._split_paper_content(parsed_summary)
            
            for i, section in enumerate(paper_sections[:12]):  # Limit to 12 papers
                paper = await self._create_paper_object(section, query, i+1)
                if paper and len(paper.title) > 10:
                    papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"Failed to parse academic papers: {e}")
            return []
        finally:
            await browser.cleanup()
    
    def _split_paper_content(self, content: str) -> List[str]:
        """Split content into individual papers"""
        # Strategy 1: Numbered papers
        if re.search(r'\n\d+\.', content):
            sections = re.split(r'\n(?=\d+\.)', content)
            return [s.strip() for s in sections if len(s.strip()) > 30]
        
        # Strategy 2: Paper indicators
        paper_indicators = ['Paper:', 'Title:', 'Authors:', 'Citation']
        for indicator in paper_indicators:
            if indicator in content:
                sections = content.split('\n\n')
                return [s.strip() for s in sections if indicator in s and len(s.strip()) > 40]
        
        # Strategy 3: Double newlines
        sections = content.split('\n\n')
        return [s.strip() for s in sections if len(s.strip()) > 50]
    
    async def _create_paper_object(self, paper_text: str, query: str, paper_num: int) -> Optional[AcademicPaper]:
        """Create structured paper object from text"""
        try:
            # Extract title
            lines = [line.strip() for line in paper_text.split('\n') if line.strip()]
            title = "Unknown Title"
            
            for line in lines[:3]:
                if len(line) > 15 and not line.lower().startswith(('author', 'year', 'journal', 'cited')):
                    title = line.replace('Title:', '').replace('Paper:', '').strip()
                    if len(title) > 5:
                        break
            
            # Extract authors
            authors = []
            author_patterns = [
                r'Authors?:\s*([^\n]+)',
                r'By:\s*([^\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*)*)'
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, paper_text, re.IGNORECASE)
                if match:
                    author_string = match.group(1)
                    # Split by common separators
                    authors = [author.strip() for author in re.split(r'[,;&]|and\s+', author_string)]
                    authors = [a for a in authors if len(a) > 2 and a.count(' ') <= 3]  # Filter reasonable names
                    break
            
            # Extract publication year
            publication_year = None
            year_patterns = [
                r'Year:\s*(\d{4})',
                r'(\d{4})',
                r'Published:?\s*(\d{4})'
            ]
            
            for pattern in year_patterns:
                match = re.search(pattern, paper_text)
                if match:
                    try:
                        year = int(match.group(1))
                        if 1900 <= year <= datetime.now().year:
                            publication_year = year
                            break
                    except ValueError:
                        continue
            
            # Extract journal
            journal = None
            journal_patterns = [
                r'Journal:\s*([^\n]+)',
                r'Published in:\s*([^\n]+)',
                r'Conference:\s*([^\n]+)'
            ]
            
            for pattern in journal_patterns:
                match = re.search(pattern, paper_text, re.IGNORECASE)
                if match:
                    journal = match.group(1).strip()
                    break
            
            # Extract citation count
            citation_count = None
            citation_patterns = [
                r'Cited by\s+(\d+)',
                r'Citations?:\s*(\d+)',
                r'(\d+)\s*citations?'
            ]
            
            for pattern in citation_patterns:
                match = re.search(pattern, paper_text, re.IGNORECASE)
                if match:
                    try:
                        citation_count = int(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Extract abstract
            abstract = ""
            abstract_patterns = [
                r'Abstract:\s*([^\n]{50,})',
                r'Summary:\s*([^\n]{50,})'
            ]
            
            for pattern in abstract_patterns:
                match = re.search(pattern, paper_text, re.IGNORECASE | re.DOTALL)
                if match:
                    abstract = match.group(1)[:500]  # Limit to 500 chars
                    break
            
            if not abstract:
                # Use first substantial line as abstract
                for line in lines:
                    if len(line) > 50 and not any(keyword in line.lower() for keyword in ['title', 'author', 'year', 'journal']):
                        abstract = line[:300]
                        break
            
            # Extract DOI
            doi = None
            doi_match = re.search(r'DOI:\s*([^\s\n]+)', paper_text, re.IGNORECASE)
            if doi_match:
                doi = doi_match.group(1)
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(title, abstract, query, citation_count, publication_year)
            
            # Generate BibTeX if we have enough info
            bibtex = self._generate_bibtex(title, authors, journal, publication_year, doi)
            
            return AcademicPaper(
                title=title,
                authors=authors,
                publication_year=publication_year,
                journal=journal,
                abstract=abstract,
                citation_count=citation_count,
                doi=doi,
                url=f"https://scholar.google.com/paper/{paper_num}",
                bibtex=bibtex,
                relevance_score=relevance_score,
                keywords=self._extract_keywords(title + " " + abstract)
            )
            
        except Exception as e:
            logger.error(f"Failed to create paper object: {e}")
            return None
    
    def _calculate_relevance_score(self, title: str, abstract: str, query: str, citations: Optional[int], year: Optional[int]) -> float:
        """Calculate relevance score for a paper"""
        score = 0.0
        
        # Query term matching
        query_terms = query.lower().split()
        text_to_search = (title + " " + abstract).lower()
        
        term_matches = sum(1 for term in query_terms if term in text_to_search)
        if query_terms:
            query_match_score = term_matches / len(query_terms)
            score += query_match_score * 40  # Max 40 points for query matching
        
        # Citation count scoring
        if citations:
            citation_score = min(citations / 100, 1.0) * 30  # Max 30 points for citations
            score += citation_score
        
        # Recency scoring
        if year:
            current_year = datetime.now().year
            age = current_year - year
            recency_score = max(0, (10 - age) / 10) * 20  # Max 20 points for recent papers
            score += recency_score
        
        # Quality indicators
        if any(word in text_to_search for word in ['novel', 'breakthrough', 'significant', 'important']):
            score += 5
        
        # Title relevance bonus
        title_lower = title.lower()
        if any(term in title_lower for term in query_terms):
            score += 5
        
        return min(score, 100.0)  # Cap at 100
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract potential keywords from text"""
        # Simple keyword extraction based on common academic terms
        text_lower = text.lower()
        potential_keywords = []
        
        # Look for method/technique keywords
        method_terms = ['algorithm', 'method', 'approach', 'technique', 'framework', 'model', 'system']
        for term in method_terms:
            if term in text_lower:
                potential_keywords.append(term)
        
        # Look for domain-specific terms (basic implementation)
        if 'machine learning' in text_lower:
            potential_keywords.append('machine learning')
        if 'artificial intelligence' in text_lower:
            potential_keywords.append('artificial intelligence')
        if 'neural network' in text_lower:
            potential_keywords.append('neural networks')
        
        return potential_keywords[:5]  # Limit to 5 keywords
    
    def _generate_bibtex(self, title: str, authors: List[str], journal: Optional[str], year: Optional[int], doi: Optional[str]) -> Optional[str]:
        """Generate BibTeX entry for the paper"""
        if not title or not authors:
            return None
        
        # Create citation key
        first_author = authors[0].split()[-1] if authors else "Unknown"
        year_str = str(year) if year else "YYYY"
        key = f"{first_author.lower()}{year_str}"
        
        # Format authors for BibTeX
        author_str = " and ".join(authors) if len(authors) <= 3 else f"{authors[0]} and others"
        
        # Build BibTeX entry
        bibtex_lines = [
            f"@article{{{key},",
            f"  author = {{{author_str}}}",
            f"  title = {{{title}}}",
        ]
        
        if journal:
            bibtex_lines.append(f"  journal = {{{journal}}}")
        
        if year:
            bibtex_lines.append(f"  year = {{{year}}}")
        
        if doi:
            bibtex_lines.append(f"  doi = {{{doi}}}")
        
        bibtex_lines.append("}")
        
        return ",\n".join(bibtex_lines)
    
    async def generate_literature_review(self, papers: List[AcademicPaper], topic: str) -> Dict[str, Any]:
        """Generate AI-powered literature review"""
        logger.info("[REVIEW] Generating literature review and analysis...")
        
        if not papers:
            return {"error": "No papers available for review"}
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Prepare papers data for analysis
        papers_summary = []
        for paper in papers[:10]:  # Limit to top 10 papers
            papers_summary.append({
                "title": paper.title,
                "authors": paper.authors[:3],  # Top 3 authors
                "year": paper.publication_year,
                "journal": paper.journal,
                "abstract": paper.abstract[:300],  # First 300 chars
                "citations": paper.citation_count,
                "relevance": paper.relevance_score
            })
        
        review_task = f"""
        Write a comprehensive literature review on '{topic}' based on these academic papers:
        
        Papers: {json.dumps(papers_summary, indent=2, default=str)}
        
        Create a structured literature review including:
        1. Introduction to the research area
        2. Key themes and research directions identified
        3. Chronological development of the field
        4. Major contributions and breakthrough papers
        5. Current state of research and recent advances
        6. Research gaps and future opportunities
        7. Methodological approaches used
        8. Conclusion and synthesis
        
        Write in academic style with proper structure and flow.
        Reference specific papers and authors in your analysis.
        Identify trends, conflicts, and consensus in the literature.
        """
        
        config = TaskConfig(
            task=review_task,
            url="https://www.example.com",
            headless=True,
            max_steps=8,
            timeout=120000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Analyze citation patterns
            citation_analysis = self._analyze_citation_patterns(papers)
            
            # Identify research trends
            research_trends = self._identify_research_trends(papers)
            
            literature_review = {
                "topic": topic,
                "review_text": result.get('summary', ''),
                "papers_analyzed": len(papers),
                "citation_analysis": citation_analysis,
                "research_trends": research_trends,
                "bibliography": self._create_bibliography(papers),
                "generated_at": datetime.now().isoformat()
            }
            
            return literature_review
            
        except Exception as e:
            logger.error(f"Failed to generate literature review: {e}")
            return {"error": str(e)}
        finally:
            await browser.cleanup()
    
    def _analyze_citation_patterns(self, papers: List[AcademicPaper]) -> Dict[str, Any]:
        """Analyze citation patterns in the papers"""
        cited_papers = [p for p in papers if p.citation_count is not None]
        
        if not cited_papers:
            return {"error": "No citation data available"}
        
        citations = [p.citation_count for p in cited_papers]
        
        analysis = {
            "total_papers_with_citations": len(cited_papers),
            "total_citations": sum(citations),
            "average_citations": sum(citations) / len(citations),
            "max_citations": max(citations),
            "min_citations": min(citations),
            "highly_cited_threshold": sum(citations) / len(citations) * 2,  # 2x average
            "highly_cited_papers": [
                {"title": p.title, "citations": p.citation_count}
                for p in cited_papers
                if p.citation_count > (sum(citations) / len(citations) * 2)
            ][:5]
        }
        
        return analysis
    
    def _identify_research_trends(self, papers: List[AcademicPaper]) -> Dict[str, Any]:
        """Identify research trends from papers"""
        trends = {}
        
        # Temporal analysis
        papers_with_years = [p for p in papers if p.publication_year]
        if papers_with_years:
            years = [p.publication_year for p in papers_with_years]
            year_distribution = {}
            for year in years:
                year_distribution[year] = year_distribution.get(year, 0) + 1
            
            trends["temporal_distribution"] = year_distribution
            trends["publication_span"] = f"{min(years)}-{max(years)}"
            trends["recent_papers"] = len([y for y in years if y >= 2020])
        
        # Author analysis
        all_authors = []
        for paper in papers:
            all_authors.extend(paper.authors)
        
        author_counts = {}
        for author in all_authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        prolific_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        trends["prolific_authors"] = prolific_authors
        
        # Journal analysis
        journals = [p.journal for p in papers if p.journal]
        journal_counts = {}
        for journal in journals:
            journal_counts[journal] = journal_counts.get(journal, 0) + 1
        
        top_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        trends["top_journals"] = top_journals
        
        return trends
    
    def _create_bibliography(self, papers: List[AcademicPaper]) -> List[Dict[str, Any]]:
        """Create formatted bibliography"""
        bibliography = []
        
        for paper in papers:
            entry = {
                "apa_format": self._format_apa_citation(paper),
                "bibtex": paper.bibtex,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.publication_year,
                "journal": paper.journal,
                "citations": paper.citation_count
            }
            bibliography.append(entry)
        
        return sorted(bibliography, key=lambda x: x.get("citations", 0), reverse=True)
    
    def _format_apa_citation(self, paper: AcademicPaper) -> str:
        """Format paper in APA style"""
        try:
            # Format authors
            if not paper.authors:
                authors_str = "Unknown Author"
            elif len(paper.authors) == 1:
                authors_str = paper.authors[0]
            elif len(paper.authors) == 2:
                authors_str = f"{paper.authors[0]} & {paper.authors[1]}"
            else:
                authors_str = f"{paper.authors[0]} et al."
            
            # Build citation
            citation = authors_str
            
            if paper.publication_year:
                citation += f" ({paper.publication_year})"
            
            citation += f". {paper.title}"
            
            if paper.journal:
                citation += f". *{paper.journal}*"
            
            if paper.doi:
                citation += f". https://doi.org/{paper.doi}"
            
            return citation
            
        except Exception:
            return f"{paper.title} - Citation formatting error"
    
    async def comprehensive_academic_research(self, research_topic: str, max_papers: int = 20) -> Dict[str, Any]:
        """Run comprehensive academic research"""
        logger.info(f"[RESEARCH] Starting comprehensive academic research on: {research_topic}")
        
        # Search for papers
        papers = await self.search_google_scholar(research_topic, max_papers)
        
        if not papers:
            return {"error": "No papers found", "topic": research_topic}
        
        # Sort papers by relevance score
        papers.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Generate literature review
        literature_review = await self.generate_literature_review(papers, research_topic)
        
        # Compile comprehensive results
        research_results = {
            "research_topic": research_topic,
            "research_timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "total_papers_found": len(papers),
            "papers": [asdict(p) for p in papers],
            "literature_review": literature_review,
            "top_papers": [
                {
                    "title": p.title,
                    "authors": p.authors,
                    "year": p.publication_year,
                    "citations": p.citation_count,
                    "relevance_score": p.relevance_score,
                    "journal": p.journal
                }
                for p in papers[:10]  # Top 10 most relevant
            ],
            "research_summary": self._create_research_summary(papers, literature_review)
        }
        
        # Save results
        await self._save_research_results(research_results)
        
        return research_results
    
    def _create_research_summary(self, papers: List[AcademicPaper], literature_review: Dict[str, Any]) -> str:
        """Create executive summary of research findings"""
        if not papers:
            return "No papers found for analysis."
        
        total_papers = len(papers)
        total_citations = sum(p.citation_count or 0 for p in papers)
        avg_citations = total_citations / total_papers if total_papers > 0 else 0
        
        papers_with_years = [p for p in papers if p.publication_year]
        year_span = ""
        if papers_with_years:
            min_year = min(p.publication_year for p in papers_with_years)
            max_year = max(p.publication_year for p in papers_with_years)
            year_span = f"spanning {min_year}-{max_year}"
        
        summary_lines = [
            f"Academic Research Summary",
            f"Total Papers Analyzed: {total_papers} {year_span}",
            f"Total Citations: {total_citations:,}",
            f"Average Citations per Paper: {avg_citations:.1f}",
            "",
            f"Top Paper: {papers[0].title}" if papers else "No top paper identified",
            f"Most Cited: {max(papers, key=lambda x: x.citation_count or 0).title}" if papers else "",
        ]
        
        if literature_review.get("research_trends"):
            trends = literature_review["research_trends"]
            if trends.get("prolific_authors"):
                top_author = trends["prolific_authors"][0][0]
                summary_lines.append(f"Prolific Author: {top_author}")
        
        return "\n".join(summary_lines)
    
    async def _save_research_results(self, results: Dict[str, Any]):
        """Save academic research results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"academic_research_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        # Save literature review
        review_file = self.results_dir / f"literature_review_{timestamp}.txt"
        with open(review_file, 'w', encoding='utf-8') as f:
            f.write("ACADEMIC LITERATURE REVIEW\n")
            f.write("="*50 + "\n\n")
            f.write(f"Topic: {results['research_topic']}\n")
            f.write(f"Research Date: {results['research_timestamp']}\n")
            f.write(f"Papers Analyzed: {results['total_papers_found']}\n\n")
            
            # Literature review
            if results['literature_review'].get('review_text'):
                f.write("LITERATURE REVIEW:\n")
                f.write("-" * 20 + "\n")
                f.write(results['literature_review']['review_text'])
                f.write("\n\n")
            
            # Bibliography
            f.write("BIBLIOGRAPHY (Top 10 Papers):\n")
            f.write("-" * 30 + "\n")
            for i, paper in enumerate(results['top_papers'][:10], 1):
                f.write(f"{i}. {paper['title']}\n")
                f.write(f"   Authors: {', '.join(paper['authors'][:3])}\n")
                if paper['year']:
                    f.write(f"   Year: {paper['year']}\n")
                if paper['journal']:
                    f.write(f"   Journal: {paper['journal']}\n")
                if paper['citations']:
                    f.write(f"   Citations: {paper['citations']:,}\n")
                f.write(f"   Relevance: {paper['relevance_score']:.1f}/100\n\n")
        
        # Save BibTeX file
        bibtex_file = self.results_dir / f"bibliography_{timestamp}.bib"
        with open(bibtex_file, 'w', encoding='utf-8') as f:
            f.write(f"% Bibliography for: {results['research_topic']}\n")
            f.write(f"% Generated: {results['research_timestamp']}\n\n")
            
            for paper in results['papers']:
                if paper.get('bibtex'):
                    f.write(paper['bibtex'])
                    f.write("\n\n")
        
        logger.info(f"[SAVED] Research results saved to: {json_file}")
        logger.info(f"[SAVED] Literature review saved to: {review_file}")
        logger.info(f"[SAVED] BibTeX bibliography saved to: {bibtex_file}")


async def demo_academic_research():
    """Demonstrate academic research capabilities"""
    print("\n" + "="*70)
    print("[*] AI-POWERED ACADEMIC RESEARCH ASSISTANT")
    print("="*70)
    print("This demo searches academic databases and generates literature")
    print("reviews using AI reasoning and real browser automation.\n")
    
    assistant = AcademicResearchAssistant()
    
    # Example research topics
    research_topics = [
        "machine learning bias detection",
        "quantum computing algorithms",
        "sustainable energy technologies",
        "natural language processing transformers",
        "computer vision deep learning"
    ]
    
    print("Select a research topic:")
    for i, topic in enumerate(research_topics, 1):
        print(f"{i}. {topic.title()}")
    print(f"{len(research_topics) + 1}. Custom research topic")
    
    try:
        choice = input(f"\nEnter choice (1-{len(research_topics) + 1}): ").strip()
        
        if choice == str(len(research_topics) + 1):
            topic = input("Enter research topic: ").strip()
            if not topic:
                topic = research_topics[0]  # Default
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(research_topics):
                    topic = research_topics[choice_idx]
                else:
                    topic = research_topics[0]  # Default
            except ValueError:
                topic = research_topics[0]  # Default
        
        # Number of papers
        num_papers = input("Number of papers to analyze [15]: ").strip()
        try:
            max_papers = int(num_papers) if num_papers else 15
            max_papers = min(max(max_papers, 5), 25)  # Clamp between 5-25
        except ValueError:
            max_papers = 15
        
        print(f"\n[RESEARCH] Researching: {topic}")
        print(f"[PAPERS] Target papers: {max_papers}")
        print("[TIME] This may take 8-12 minutes to search and analyze papers...\n")
        
        # Run comprehensive research
        results = await assistant.comprehensive_academic_research(topic, max_papers)
        
        if "error" in results:
            print(f"[ERROR] Research failed: {results['error']}")
            return
        
        # Display results
        print("\n" + "="*50)
        print("[RESULTS] ACADEMIC RESEARCH RESULTS")
        print("="*50)
        
        print(f"Research Topic: {results['research_topic']}")
        print(f"Papers Found: {results['total_papers_found']}")
        
        # Citation analysis
        lit_review = results['literature_review']
        if lit_review.get('citation_analysis'):
            cit_analysis = lit_review['citation_analysis']
            print(f"\n[CITATIONS] CITATION ANALYSIS:")
            print("-" * 25)
            print(f"Total Citations: {cit_analysis.get('total_citations', 0):,}")
            print(f"Average Citations: {cit_analysis.get('average_citations', 0):.1f}")
            print(f"Most Cited Paper: {cit_analysis.get('max_citations', 0):,} citations")
        
        # Research trends
        if lit_review.get('research_trends'):
            trends = lit_review['research_trends']
            print(f"\n[TRENDS] RESEARCH TRENDS:")
            print("-" * 25)
            
            if trends.get('temporal_distribution'):
                recent_papers = trends.get('recent_papers', 0)
                total = results['total_papers_found']
                print(f"Recent Papers (2020+): {recent_papers}/{total} ({recent_papers/total*100:.1f}%)")
            
            if trends.get('prolific_authors'):
                top_authors = trends['prolific_authors'][:3]
                print("Top Authors:")
                for author, count in top_authors:
                    print(f"  - {author}: {count} papers")
        
        # Top papers
        print(f"\n[TOP] TOP PAPERS BY RELEVANCE:")
        print("-" * 35)
        for i, paper in enumerate(results['top_papers'][:5], 1):
            print(f"\n{i}. {paper['title']}")
            if paper['authors']:
                authors_display = ', '.join(paper['authors'][:2])
                if len(paper['authors']) > 2:
                    authors_display += " et al."
                print(f"   Authors: {authors_display}")
            
            details = []
            if paper['year']:
                details.append(str(paper['year']))
            if paper['journal']:
                details.append(paper['journal'])
            if details:
                print(f"   Published: {' | '.join(details)}")
            
            if paper['citations']:
                print(f"   Citations: {paper['citations']:,}")
            print(f"   Relevance: {paper['relevance_score']:.1f}/100")
        
        # Literature review preview
        if results['literature_review'].get('review_text'):
            print(f"\n[REVIEW] LITERATURE REVIEW PREVIEW:")
            print("-" * 35)
            review_text = results['literature_review']['review_text']
            # Show first few sentences
            sentences = review_text.split('.')[:3]
            for sentence in sentences:
                if sentence.strip():
                    print(f"  {sentence.strip()}.")
            if len(review_text.split('.')) > 3:
                print("  ... (see full review in output files)")
        
        print(f"\n[FILES] Research files saved to: examples/outputs/academic_research/")
        print("     - Full JSON results")
        print("     - Literature review (TXT)")
        print("     - BibTeX bibliography (.bib)")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_academic_research())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()