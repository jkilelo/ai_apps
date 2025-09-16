#!/usr/bin/env python3
"""
Real-World News Monitoring & Summarization Automation

This example demonstrates autonomous news monitoring and analysis:
- Monitor multiple news sources (CNN, BBC, Reuters, TechCrunch)
- Extract breaking news and trending stories
- Generate AI-powered summaries and insights
- Track story development over time
- Categorize news by topics and importance
- Detect bias and sentiment in reporting
- Create personalized news briefings

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended for summarization)
- Working internet connection
- AI Browser v2.0.0 system components

USAGE:
    python examples/real_world_news_monitoring.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re
from urllib.parse import urljoin, urlparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


@dataclass
class NewsArticle:
    """Structured news article data"""
    title: str
    url: str
    source: str
    author: Optional[str] = None
    published_date: Optional[str] = None
    content: str = ""
    summary: str = ""
    category: Optional[str] = None
    importance_score: float = 0.0  # 0-1 scale
    sentiment_score: Optional[float] = None  # -1 to 1 scale
    sentiment_label: Optional[str] = None
    bias_score: Optional[float] = None  # -1 (left bias) to 1 (right bias)
    keywords: List[str] = None
    entities: List[str] = None  # People, places, organizations
    reading_time_minutes: Optional[int] = None
    word_count: Optional[int] = None
    image_url: Optional[str] = None
    extracted_at: str = ""
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.entities is None:
            self.entities = []
        if not self.extracted_at:
            self.extracted_at = datetime.now().isoformat()


@dataclass
class NewsSource:
    """News source configuration"""
    name: str
    base_url: str
    homepage_url: str
    bias_rating: float = 0.0  # -1 (left) to 1 (right), 0 = neutral
    credibility_score: float = 0.8  # 0-1 scale
    primary_categories: List[str] = None
    
    def __post_init__(self):
        if self.primary_categories is None:
            self.primary_categories = ["general"]


class NewsMonitor:
    """AI-powered news monitoring and summarization system"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/news_monitoring")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"news_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Define major news sources
        self.news_sources = [
            NewsSource("CNN", "cnn.com", "https://www.cnn.com", bias_rating=-0.2, credibility_score=0.7),
            NewsSource("BBC", "bbc.com", "https://www.bbc.com/news", bias_rating=0.0, credibility_score=0.9),
            NewsSource("Reuters", "reuters.com", "https://www.reuters.com", bias_rating=0.1, credibility_score=0.9),
            NewsSource("TechCrunch", "techcrunch.com", "https://techcrunch.com", bias_rating=0.0, credibility_score=0.8),
            NewsSource("Associated Press", "apnews.com", "https://apnews.com", bias_rating=0.0, credibility_score=0.9)
        ]
    
    async def monitor_cnn_news(self, category: str = "top") -> List[NewsArticle]:
        """Monitor CNN for latest news"""
        logger.info(f"[TV] Monitoring CNN for {category} news")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        if category.lower() == "tech":
            url = "https://www.cnn.com/business/tech"
        elif category.lower() == "world":
            url = "https://www.cnn.com/world"
        elif category.lower() == "business":
            url = "https://www.cnn.com/business"
        else:
            url = "https://www.cnn.com"
        
        task = f"""
        Go to CNN and extract the latest news articles from the {category} section.
        Find the first 5-7 most prominent articles and extract for each:
        
        1. Article headline/title
        2. Article URL (full link)
        3. Author name if visible
        4. Publication timestamp
        5. Brief description/summary
        6. Article category/section
        7. Any prominent image
        
        Focus on recent articles (last 24-48 hours) and major stories.
        Handle any cookie consent or subscription prompts by dismissing them.
        Extract clear, complete information for each article.
        """
        
        config = TaskConfig(
            task=task,
            url=url,
            headless=True,
            max_steps=15,
            timeout=90000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            articles = await self._parse_news_articles(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'CNN',
                -0.2  # CNN bias rating
            )
            
            logger.info(f"[SUCCESS] Found {len(articles)} CNN articles")
            return articles
            
        except Exception as e:
            logger.error(f"[ERROR] CNN monitoring failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def monitor_bbc_news(self, category: str = "top") -> List[NewsArticle]:
        """Monitor BBC for latest news"""
        logger.info(f"[UK] Monitoring BBC for {category} news")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        if category.lower() == "tech":
            url = "https://www.bbc.com/news/technology"
        elif category.lower() == "world":
            url = "https://www.bbc.com/news/world"
        elif category.lower() == "business":
            url = "https://www.bbc.com/news/business"
        else:
            url = "https://www.bbc.com/news"
        
        task = f"""
        Go to BBC News and extract recent articles from the {category} section.
        Find 5-7 top articles and extract:
        
        1. Article headline
        2. Full article URL
        3. Publication date/time
        4. Article summary or first paragraph
        5. News category
        6. Any byline/author information
        7. Featured image if present
        
        Handle cookie notifications and focus on breaking news and major stories.
        BBC often has clear timestamps and good article organization.
        """
        
        config = TaskConfig(
            task=task,
            url=url,
            headless=True,
            max_steps=15,
            timeout=90000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            articles = await self._parse_news_articles(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'BBC',
                0.0  # BBC neutral bias rating
            )
            
            logger.info(f"[SUCCESS] Found {len(articles)} BBC articles")
            return articles
            
        except Exception as e:
            logger.error(f"[ERROR] BBC monitoring failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def monitor_techcrunch_news(self) -> List[NewsArticle]:
        """Monitor TechCrunch for tech news"""
        logger.info(f"[TECH] Monitoring TechCrunch for tech news")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Go to TechCrunch.com and extract the latest tech articles.
        Find 5-7 recent articles and extract:
        
        1. Article title
        2. Article URL
        3. Author name
        4. Publication date
        5. Article summary/description
        6. Tags or categories
        7. Featured image
        
        Focus on startup news, tech industry updates, and product launches.
        TechCrunch has a clear article structure - extract systematically.
        """
        
        config = TaskConfig(
            task=task,
            url="https://techcrunch.com",
            headless=True,
            max_steps=15,
            timeout=90000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            articles = await self._parse_news_articles(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'TechCrunch',
                0.0  # TechCrunch neutral bias
            )
            
            # Set category for all TechCrunch articles
            for article in articles:
                article.category = "Technology"
            
            logger.info(f"[SUCCESS] Found {len(articles)} TechCrunch articles")
            return articles
            
        except Exception as e:
            logger.error(f"[ERROR] TechCrunch monitoring failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def monitor_reuters_news(self, category: str = "top") -> List[NewsArticle]:
        """Monitor Reuters for latest news"""
        logger.info(f"[NEWS] Monitoring Reuters for {category} news")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        if category.lower() == "business":
            url = "https://www.reuters.com/business/"
        elif category.lower() == "world":
            url = "https://www.reuters.com/world/"
        elif category.lower() == "tech":
            url = "https://www.reuters.com/technology/"
        else:
            url = "https://www.reuters.com"
        
        task = f"""
        Go to Reuters and extract news articles from the {category} section.
        Find 5-7 recent articles and extract:
        
        1. Article headline
        2. Full article URL
        3. Publication timestamp
        4. Article summary/lead
        5. Location/dateline if present
        6. Author/byline
        7. Category/section
        
        Reuters is known for factual, concise reporting. Focus on breaking news
        and significant international/business stories.
        """
        
        config = TaskConfig(
            task=task,
            url=url,
            headless=True,
            max_steps=15,
            timeout=90000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            articles = await self._parse_news_articles(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Reuters',
                0.1  # Slight center-right bias
            )
            
            logger.info(f"[SUCCESS] Found {len(articles)} Reuters articles")
            return articles
            
        except Exception as e:
            logger.error(f"[ERROR] Reuters monitoring failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def _parse_news_articles(self, summary: str, extracted_data: dict, source: str, bias_rating: float) -> List[NewsArticle]:
        """Parse news articles from AI extraction"""
        browser = AIBrowser({"log_level": "INFO"})
        
        parsing_task = f"""
        Parse these news articles from {source} and structure the data:
        
        Raw Data: {summary}
        Additional Data: {json.dumps(extracted_data, default=str)}
        
        Extract individual articles with:
        1. Title/headline
        2. Full URL
        3. Author name
        4. Publication date/time
        5. Article summary or description
        6. Category/section
        7. Any image URLs
        
        Format as structured data for each article found.
        Be thorough and extract complete information.
        """
        
        config = TaskConfig(
            task=parsing_task,
            url="https://www.example.com",  # Static page for parsing
            headless=True,
            max_steps=5,
            timeout=60000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            parsed_summary = result.get('summary', '')
            articles = []
            
            # Split content into articles
            article_sections = self._split_article_content(parsed_summary)
            
            for i, section in enumerate(article_sections[:7]):  # Limit to 7 articles
                article = await self._create_article_object(section, source, bias_rating, i+1)
                if article and len(article.title) > 5:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to parse news articles: {e}")
            return []
        finally:
            await browser.cleanup()
    
    def _split_article_content(self, content: str) -> List[str]:
        """Split content into individual articles"""
        # Try different splitting strategies
        
        # Strategy 1: Numbered articles
        if re.search(r'\n\d+\.', content):
            sections = re.split(r'\n(?=\d+\.)', content)
            return [s.strip() for s in sections if len(s.strip()) > 30]
        
        # Strategy 2: Article indicators
        article_indicators = ['Article:', 'Title:', 'Headline:', 'Story:']
        for indicator in article_indicators:
            if indicator in content:
                sections = content.split('\n\n')
                return [s.strip() for s in sections if indicator in s and len(s.strip()) > 30]
        
        # Strategy 3: Double newlines
        sections = content.split('\n\n')
        return [s.strip() for s in sections if len(s.strip()) > 40]
    
    async def _create_article_object(self, article_text: str, source: str, bias_rating: float, article_num: int) -> Optional[NewsArticle]:
        """Create structured article object from text"""
        try:
            # Extract title (usually first meaningful line)
            lines = [line.strip() for line in article_text.split('\n') if line.strip()]
            title = "Unknown Article"
            
            for line in lines[:3]:
                if len(line) > 10 and not line.lower().startswith(('url:', 'author:', 'date:', 'category:')):
                    title = line.replace('Title:', '').replace('Headline:', '').strip()
                    break
            
            # Extract URL
            url = f"https://{source.lower().replace(' ', '')}.com/article/{article_num}"
            url_match = re.search(r'(?:url|link):\s*(https?://[^\s\n]+)', article_text, re.IGNORECASE)
            if url_match:
                url = url_match.group(1)
            
            # Extract author
            author = None
            author_patterns = [
                r'author:\s*([^\n]+)',
                r'by\s+([^\n,]+)',
                r'byline:\s*([^\n]+)'
            ]
            for pattern in author_patterns:
                match = re.search(pattern, article_text, re.IGNORECASE)
                if match:
                    author = match.group(1).strip()
                    break
            
            # Extract publication date
            published_date = None
            date_patterns = [
                r'date:\s*([^\n]+)',
                r'published:\s*([^\n]+)',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, article_text, re.IGNORECASE)
                if match:
                    published_date = match.group(1).strip()
                    break
            
            # Extract category
            category = None
            category_patterns = [
                r'category:\s*([^\n]+)',
                r'section:\s*([^\n]+)',
                r'topic:\s*([^\n]+)'
            ]
            for pattern in category_patterns:
                match = re.search(pattern, article_text, re.IGNORECASE)
                if match:
                    category = match.group(1).strip()
                    break
            
            # Generate summary from content
            content_lines = [line for line in lines if len(line) > 20]
            content = ' '.join(content_lines[:3])  # Use first few meaningful lines
            
            # Calculate importance score based on length and content
            importance_score = await self._calculate_importance_score(title, content)
            
            # Analyze sentiment
            sentiment_score, sentiment_label = await self._analyze_article_sentiment(content)
            
            article = NewsArticle(
                title=title,
                url=url,
                source=source,
                author=author,
                published_date=published_date,
                content=content[:500],  # First 500 chars
                category=category,
                importance_score=importance_score,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                bias_score=bias_rating  # Source bias
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Failed to create article object: {e}")
            return None
    
    async def _calculate_importance_score(self, title: str, content: str) -> float:
        """Calculate article importance score using AI"""
        if len(content) < 20:
            return 0.3  # Low importance for very short content
        
        # Keywords that indicate high importance
        high_importance_keywords = [
            'breaking', 'urgent', 'crisis', 'war', 'death', 'killed', 'explosion',
            'president', 'prime minister', 'government', 'congress', 'senate',
            'billion', 'million', 'major', 'significant', 'historic', 'first time',
            'emergency', 'disaster', 'attack', 'terrorism', 'earthquake', 'hurricane'
        ]
        
        text_lower = (title + ' ' + content).lower()
        importance_indicators = sum(1 for keyword in high_importance_keywords if keyword in text_lower)
        
        # Base score calculation
        base_score = 0.5
        importance_boost = min(importance_indicators * 0.15, 0.4)  # Max boost of 0.4
        
        # Length factor (longer articles often more important)
        length_factor = min(len(content) / 1000, 0.1)  # Max boost of 0.1
        
        final_score = min(base_score + importance_boost + length_factor, 1.0)
        return final_score
    
    async def _analyze_article_sentiment(self, content: str) -> Tuple[Optional[float], Optional[str]]:
        """Analyze sentiment of news article"""
        if len(content) < 20:
            return None, None
        
        # Simple keyword-based sentiment analysis
        positive_keywords = ['success', 'growth', 'positive', 'good', 'win', 'victory', 'celebrate']
        negative_keywords = ['crisis', 'problem', 'death', 'war', 'attack', 'failure', 'loss', 'concern']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_keywords if word in content_lower)
        negative_count = sum(1 for word in negative_keywords if word in content_lower)
        
        if positive_count > negative_count:
            sentiment_score = min(positive_count * 0.2, 1.0)
            sentiment_label = "positive"
        elif negative_count > positive_count:
            sentiment_score = max(-negative_count * 0.2, -1.0)
            sentiment_label = "negative"
        else:
            sentiment_score = 0.0
            sentiment_label = "neutral"
        
        return sentiment_score, sentiment_label
    
    async def generate_news_summary(self, articles: List[NewsArticle], category: str = "") -> Dict[str, Any]:
        """Generate AI-powered news summary and insights"""
        logger.info("[DOCUMENT] Generating comprehensive news summary...")
        
        if not articles:
            return {"error": "No articles to summarize"}
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Prepare articles data for AI analysis
        articles_data = []
        for article in articles[:10]:  # Limit to 10 articles for analysis
            articles_data.append({
                "title": article.title,
                "source": article.source,
                "category": article.category,
                "content": article.content,
                "importance": article.importance_score,
                "sentiment": article.sentiment_label,
                "published": article.published_date
            })
        
        summary_task = f"""
        Analyze these news articles{' about ' + category if category else ''} and create a comprehensive briefing:
        
        Articles: {json.dumps(articles_data, indent=2)}
        
        Create a news briefing that includes:
        1. Executive summary of major stories
        2. Key themes and trends identified
        3. Most important/breaking news highlighted
        4. Geographic or sector analysis if relevant
        5. Potential implications and what to watch
        6. Source credibility and bias assessment
        7. Timeline of events if stories are related
        
        Format as a professional news briefing suitable for executives or decision-makers.
        Focus on actionable insights and key takeaways.
        """
        
        config = TaskConfig(
            task=summary_task,
            url="https://www.example.com",
            headless=True,
            max_steps=8,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Calculate aggregate statistics
            total_articles = len(articles)
            sources = list(set(article.source for article in articles))
            categories = list(set(article.category for article in articles if article.category))
            avg_importance = sum(article.importance_score for article in articles) / total_articles
            
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for article in articles:
                if article.sentiment_label:
                    sentiment_counts[article.sentiment_label] += 1
            
            summary = {
                "briefing_timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "category": category or "General News",
                "ai_summary": result.get('summary', ''),
                "executive_briefing": result.get('extracted_data', {}),
                "statistics": {
                    "total_articles": total_articles,
                    "sources_covered": sources,
                    "categories_covered": categories,
                    "average_importance": avg_importance,
                    "sentiment_distribution": sentiment_counts
                },
                "top_stories": [
                    {
                        "title": article.title,
                        "source": article.source,
                        "importance": article.importance_score,
                        "url": article.url
                    }
                    for article in sorted(articles, key=lambda x: x.importance_score, reverse=True)[:5]
                ],
                "articles_analyzed": [asdict(article) for article in articles]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate news summary: {e}")
            return {"error": str(e)}
        finally:
            await browser.cleanup()
    
    async def comprehensive_news_monitoring(self, categories: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive news monitoring across all sources"""
        logger.info(f"[SEARCH] Starting comprehensive news monitoring")
        
        if not categories:
            categories = ["top", "business", "tech", "world"]
        
        all_articles = []
        source_results = {}
        
        # Monitor different sources and categories
        monitoring_tasks = []
        
        for category in categories[:2]:  # Limit to 2 categories for demo
            monitoring_tasks.extend([
                ("CNN", self.monitor_cnn_news(category)),
                ("BBC", self.monitor_bbc_news(category)),
                ("Reuters", self.monitor_reuters_news(category))
            ])
        
        # Always include TechCrunch for tech news
        monitoring_tasks.append(("TechCrunch", self.monitor_techcrunch_news()))
        
        # Execute monitoring tasks
        for source_name, task in monitoring_tasks:
            try:
                articles = await task
                all_articles.extend(articles)
                source_results[f"{source_name}"] = len(articles)
                logger.info(f"[SUCCESS] {source_name}: {len(articles)} articles")
                
                # Small delay between sources
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"[ERROR] {source_name} monitoring failed: {e}")
                source_results[f"{source_name}"] = 0
        
        # Remove duplicates based on title similarity
        unique_articles = self._deduplicate_articles(all_articles)
        
        # Generate comprehensive summary
        summary = await self.generate_news_summary(unique_articles)
        summary["monitoring_results"] = source_results
        summary["categories_monitored"] = categories
        summary["articles_before_dedup"] = len(all_articles)
        summary["articles_after_dedup"] = len(unique_articles)
        
        # Save results
        await self._save_monitoring_results(summary)
        
        return summary
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article.title.lower()).strip()
            title_words = set(normalized_title.split())
            
            # Check if this title is too similar to existing ones
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                
                # Calculate word overlap
                if title_words and seen_words:
                    overlap = len(title_words.intersection(seen_words))
                    similarity = overlap / min(len(title_words), len(seen_words))
                    
                    if similarity > 0.7:  # 70% word overlap threshold
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(normalized_title)
        
        return unique_articles
    
    async def _save_monitoring_results(self, summary: Dict[str, Any]):
        """Save news monitoring results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"news_monitoring_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str, ensure_ascii=False)
        
        # Save executive briefing
        briefing_file = self.results_dir / f"news_briefing_{timestamp}.txt"
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write("NEWS MONITORING BRIEFING\n")
            f.write("="*50 + "\n\n")
            f.write(f"Date: {summary['briefing_timestamp']}\n")
            f.write(f"Category: {summary['category']}\n")
            f.write(f"Articles Analyzed: {summary['statistics']['total_articles']}\n")
            f.write(f"Sources: {', '.join(summary['statistics']['sources_covered'])}\n\n")
            
            # Executive summary
            if summary.get('ai_summary'):
                f.write("EXECUTIVE SUMMARY:\n")
                f.write("-" * 20 + "\n")
                f.write(summary['ai_summary'][:1000])
                f.write("\n\n")
            
            # Top stories
            f.write("TOP STORIES:\n")
            f.write("-" * 20 + "\n")
            for i, story in enumerate(summary['top_stories'][:5], 1):
                f.write(f"{i}. {story['title']}\n")
                f.write(f"   Source: {story['source']} | Importance: {story['importance']:.2f}\n")
                f.write(f"   URL: {story['url']}\n\n")
            
            # Statistics
            stats = summary['statistics']
            f.write("ANALYSIS STATISTICS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Average Importance Score: {stats['average_importance']:.2f}\n")
            f.write(f"Sentiment Distribution: {stats['sentiment_distribution']}\n")
            f.write(f"Categories Covered: {', '.join(stats['categories_covered'])}\n")
        
        logger.info(f"[DOCUMENT] Monitoring results saved to: {json_file}")
        logger.info(f"[DOCUMENT] Executive briefing saved to: {briefing_file}")


async def demo_news_monitoring():
    """Demonstrate news monitoring capabilities"""
    print("\n" + "="*70)
    print("[NEWS] AI-POWERED NEWS MONITORING & SUMMARIZATION")
    print("="*70)
    print("This demo monitors multiple news sources and generates")
    print("AI-powered summaries and insights using real browser automation.\n")
    
    monitor = NewsMonitor()
    
    # Category selection
    categories = ["top stories", "business", "technology", "world news"]
    
    print("Select news categories to monitor (comma-separated):")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category.title()}")
    
    try:
        category_input = input(f"\nEnter choices (1-{len(categories)}) [1,2]: ").strip()
        
        if category_input:
            try:
                choices = [int(x.strip()) for x in category_input.split(',')]
                selected_categories = []
                for choice in choices:
                    if 1 <= choice <= len(categories):
                        category_name = categories[choice-1].split()[0]  # Get first word
                        selected_categories.append(category_name)
            except ValueError:
                selected_categories = ["top", "business"]  # Default
        else:
            selected_categories = ["top", "business"]  # Default
        
        print(f"\n[MONITOR] Monitoring categories: {', '.join(selected_categories)}")
        print("[SEARCH] Sources: CNN, BBC, Reuters, TechCrunch")
        print("[TIMER]  This may take 6-8 minutes to monitor all sources...\n")
        
        # Run comprehensive monitoring
        results = await monitor.comprehensive_news_monitoring(selected_categories)
        
        if "error" in results:
            print(f"[ERROR] News monitoring failed: {results['error']}")
            return
        
        # Display results
        print("\n" + "="*50)
        print("[STATS] NEWS MONITORING RESULTS")
        print("="*50)
        
        stats = results['statistics']
        print(f"Articles Analyzed: {stats['total_articles']}")
        print(f"Sources Monitored: {', '.join(stats['sources_covered'])}")
        print(f"Categories: {', '.join(stats['categories_covered'])}")
        print(f"Average Importance: {stats['average_importance']:.2f}/1.0")
        
        # Source breakdown
        print(f"\n[NEWS] SOURCE BREAKDOWN:")
        print("-" * 25)
        for source, count in results['monitoring_results'].items():
            print(f"{source}: {count} articles")
        
        # Sentiment analysis
        sentiment = stats['sentiment_distribution']
        total_sentiment = sum(sentiment.values())
        if total_sentiment > 0:
            print(f"\n[SENTIMENT] SENTIMENT ANALYSIS:")
            print("-" * 25)
            for sentiment_type, count in sentiment.items():
                percentage = (count / total_sentiment) * 100
                print(f"{sentiment_type.title()}: {count} articles ({percentage:.1f}%)")
        
        # Top stories
        print(f"\n[TOP] TOP STORIES:")
        print("-" * 25)
        for i, story in enumerate(results['top_stories'][:5], 1):
            print(f"\n{i}. {story['title']}")
            print(f"   Source: {story['source']}")
            print(f"   Importance: {story['importance']:.2f}/1.0")
            print(f"   URL: {story['url']}")
        
        # AI summary preview
        if results.get('ai_summary'):
            print(f"\n[AI] AI BRIEFING PREVIEW:")
            print("-" * 30)
            summary = results['ai_summary']
            # Show first few sentences
            sentences = summary.split('.')[:3]
            for sentence in sentences:
                if sentence.strip():
                    print(f"  {sentence.strip()}.")
            if len(summary.split('.')) > 3:
                print("  ... (see full briefing in output files)")
        
        # Deduplication info
        if results.get('articles_before_dedup') != results.get('articles_after_dedup'):
            before = results['articles_before_dedup']
            after = results['articles_after_dedup']
            duplicates_removed = before - after
            print(f"\n[PROCESS] DUPLICATE REMOVAL:")
            print("-" * 25)
            print(f"Original articles: {before}")
            print(f"After deduplication: {after}")
            print(f"Duplicates removed: {duplicates_removed}")
        
        print(f"\n[STATS] Detailed briefing saved to: examples/outputs/news_monitoring/")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_news_monitoring())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()