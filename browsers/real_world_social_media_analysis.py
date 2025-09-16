#!/usr/bin/env python3
"""
Real-World Social Media Content Analysis Automation

This example demonstrates autonomous social media monitoring and analysis:
- Monitor Twitter/X for trending topics and mentions
- Analyze LinkedIn posts for industry insights
- Extract engagement metrics and sentiment analysis
- Track brand mentions and competitor activity
- Generate comprehensive social media reports
- Identify influencers and key conversations
- Store insights in memory for trend analysis

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended for sentiment analysis)
- Working internet connection
- AI Browser v2.0.0 system components
- No API keys required (uses web scraping approach)

USAGE:
    python examples/real_world_social_media_analysis.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
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
class SocialMediaPost:
    """Structured social media post data"""
    content: str
    author: str
    platform: str
    post_url: str = ""
    timestamp: Optional[str] = None
    likes_count: Optional[int] = None
    shares_count: Optional[int] = None
    comments_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    sentiment_score: Optional[float] = None  # -1 to 1 scale
    sentiment_label: Optional[str] = None  # positive, negative, neutral
    hashtags: List[str] = None
    mentions: List[str] = None
    topics: List[str] = None
    language: str = "en"
    extracted_at: str = ""
    
    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.topics is None:
            self.topics = []
        if not self.extracted_at:
            self.extracted_at = datetime.now().isoformat()


@dataclass
class SocialMediaTrend:
    """Trending topic or theme analysis"""
    topic: str
    platform: str
    post_count: int
    total_engagement: int
    sentiment_distribution: Dict[str, int]
    key_influencers: List[str]
    sample_posts: List[str]
    trend_score: float
    first_seen: str
    last_updated: str


class SocialMediaAnalyzer:
    """AI-powered social media monitoring and analysis"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/social_media_analysis")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"social_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def analyze_twitter_topic(self, search_query: str, max_posts: int = 10) -> List[SocialMediaPost]:
        """Analyze Twitter/X posts about a specific topic"""
        logger.info(f"[TWITTER] Analyzing Twitter/X for: {search_query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Use Twitter search (can access without login for basic searches)
        search_url = f"https://twitter.com/search?q={quote(search_query)}&src=typed_query&f=live"
        
        task = f"""
        Go to Twitter/X and search for posts about '{search_query}'.
        Extract information from the first {max_posts} posts you see:
        
        For each post, collect:
        1. Full tweet text content
        2. Author username and display name
        3. Post timestamp (when available)
        4. Like count, retweet count, reply count
        5. Any hashtags used (#example)
        6. Any user mentions (@username)
        7. Post URL or ID if visible
        
        Focus on recent, relevant posts with good engagement.
        Handle any login prompts by dismissing them or using guest access.
        If asked to sign up, look for "Continue without account" options.
        
        Extract the data systematically and be thorough.
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
            
            # Parse Twitter posts
            posts = await self._parse_social_posts(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Twitter',
                search_query
            )
            
            logger.info(f"[SUCCESS] Extracted {len(posts)} Twitter posts")
            return posts
            
        except Exception as e:
            logger.error(f"[ERROR] Twitter analysis failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def analyze_linkedin_content(self, search_query: str, max_posts: int = 10) -> List[SocialMediaPost]:
        """Analyze LinkedIn posts about a specific topic"""
        logger.info(f"[LINKEDIN] Analyzing LinkedIn for: {search_query}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # LinkedIn search approach
        search_url = f"https://www.linkedin.com/search/results/content/?keywords={quote(search_query)}"
        
        task = f"""
        Go to LinkedIn and search for content about '{search_query}'.
        Extract information from {max_posts} relevant posts:
        
        For each post, gather:
        1. Full post content and text
        2. Author name and title/company
        3. Post date/timestamp
        4. Reaction count (likes, celebrates, etc.)
        5. Comment count and share count
        6. Any hashtags in the post
        7. Post URL if accessible
        8. Industry or topic tags
        
        Handle any login requests by looking for "Guest" access or dismiss prompts.
        Focus on professional, industry-relevant content.
        Look for thought leadership posts and industry discussions.
        
        Be thorough in extracting engagement metrics and content details.
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
            
            # Parse LinkedIn posts
            posts = await self._parse_social_posts(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'LinkedIn',
                search_query
            )
            
            logger.info(f"[SUCCESS] Extracted {len(posts)} LinkedIn posts")
            return posts
            
        except Exception as e:
            logger.error(f"[ERROR] LinkedIn analysis failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def analyze_reddit_discussions(self, subreddit: str, search_query: str = "", max_posts: int = 10) -> List[SocialMediaPost]:
        """Analyze Reddit discussions in specific subreddit"""
        logger.info(f"[REDDIT] Analyzing Reddit r/{subreddit} for: {search_query or 'recent posts'}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Reddit URL construction
        if search_query:
            search_url = f"https://www.reddit.com/r/{subreddit}/search/?q={quote(search_query)}&restrict_sr=1&sort=top&t=week"
        else:
            search_url = f"https://www.reddit.com/r/{subreddit}/hot/"
        
        task = f"""
        Go to Reddit and analyze posts in r/{subreddit}{' about "' + search_query + '"' if search_query else ''}.
        Extract data from {max_posts} top posts:
        
        For each post, collect:
        1. Post title and content/description
        2. Author username (u/username)
        3. Post score (upvotes minus downvotes)
        4. Number of comments
        5. Post timestamp/age ("2 hours ago", etc.)
        6. Any awards or special recognition
        7. Post URL for direct link
        8. Flair/category tags if present
        
        Focus on highly upvoted, recent posts with good discussion.
        Handle any age verification or content warnings by proceeding.
        Extract meaningful discussion content, not just titles.
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
            
            # Parse Reddit posts
            posts = await self._parse_social_posts(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Reddit',
                search_query or f"r/{subreddit}"
            )
            
            logger.info(f"[SUCCESS] Extracted {len(posts)} Reddit posts")
            return posts
            
        except Exception as e:
            logger.error(f"[ERROR] Reddit analysis failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def _parse_social_posts(self, summary: str, extracted_data: dict, platform: str, query: str) -> List[SocialMediaPost]:
        """Parse social media posts from AI extraction"""
        browser = AIBrowser({"log_level": "INFO"})
        
        # Use AI to structure the extracted social media data
        parsing_task = f"""
        Parse this social media data from {platform} and extract individual posts:
        
        Raw Data: {summary}
        Additional Data: {json.dumps(extracted_data, default=str)}
        
        Identify individual posts and extract for each:
        1. Post content/text
        2. Author username/name
        3. Engagement metrics (likes, shares, comments)
        4. Timestamp if available
        5. Hashtags (starting with #)
        6. User mentions (starting with @)
        7. URL or post identifier
        
        Format as JSON array with structured post objects.
        Be thorough and accurate. Extract at least 3-5 posts if available.
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
            
            # Process the parsed data
            parsed_summary = result.get('summary', '')
            posts = []
            
            # Try to extract post data from the parsed summary
            post_sections = self._split_post_content(parsed_summary)
            
            for i, section in enumerate(post_sections[:10]):  # Limit to 10 posts
                post = await self._create_post_object(section, platform, query, i+1)
                if post and len(post.content) > 10:  # Valid post with content
                    posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to parse social posts: {e}")
            return []
        finally:
            await browser.cleanup()
    
    def _split_post_content(self, content: str) -> List[str]:
        """Split content into individual posts"""
        # Try different splitting strategies
        
        # Strategy 1: Look for numbered posts
        if re.search(r'\n\d+\.', content):
            sections = re.split(r'\n(?=\d+\.)', content)
            return [s.strip() for s in sections if len(s.strip()) > 20]
        
        # Strategy 2: Look for post indicators
        post_indicators = ['Post:', 'Tweet:', 'Author:', 'Username:', '@', '#']
        for indicator in post_indicators:
            if indicator in content:
                sections = content.split('\n\n')
                return [s.strip() for s in sections if indicator in s and len(s.strip()) > 20]
        
        # Strategy 3: Split by double newlines
        sections = content.split('\n\n')
        return [s.strip() for s in sections if len(s.strip()) > 30]
    
    async def _create_post_object(self, post_content: str, platform: str, query: str, post_num: int) -> Optional[SocialMediaPost]:
        """Create structured post object from text"""
        try:
            # Extract basic info
            content = post_content
            author = "Unknown"
            
            # Try to find author
            author_patterns = [
                r'Author:\s*([^\n]+)',
                r'Username:\s*([^\n]+)',
                r'@(\w+)',
                r'u/(\w+)',  # Reddit
                r'by\s+([^\n]+)'
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, post_content, re.IGNORECASE)
                if match:
                    author = match.group(1).strip()
                    break
            
            # Extract engagement metrics
            likes_count = self._extract_number(post_content, ['like', 'reaction', 'upvote'])
            comments_count = self._extract_number(post_content, ['comment', 'reply'])
            shares_count = self._extract_number(post_content, ['share', 'retweet', 'repost'])
            
            # Extract hashtags
            hashtags = re.findall(r'#(\w+)', post_content)
            
            # Extract mentions
            mentions = re.findall(r'@(\w+)', post_content)
            
            # Generate sentiment analysis
            sentiment_score, sentiment_label = await self._analyze_sentiment(content)
            
            # Clean content (remove metadata)
            content = self._clean_post_content(content)
            
            return SocialMediaPost(
                content=content,
                author=author,
                platform=platform,
                post_url=f"{platform.lower()}/post/{post_num}",
                likes_count=likes_count,
                comments_count=comments_count,
                shares_count=shares_count,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                hashtags=hashtags,
                mentions=mentions
            )
            
        except Exception as e:
            logger.error(f"Failed to create post object: {e}")
            return None
    
    def _extract_number(self, text: str, keywords: List[str]) -> Optional[int]:
        """Extract numeric counts from text"""
        text_lower = text.lower()
        
        for keyword in keywords:
            patterns = [
                rf'{keyword}[s]?:\s*(\d+(?:,\d{{3}})*)',
                rf'(\d+(?:,\d{{3}})*)\s+{keyword}[s]?',
                rf'{keyword}[s]?\s*(\d+(?:,\d{{3}})*)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        return int(match.group(1).replace(',', ''))
                    except ValueError:
                        continue
        
        return None
    
    def _clean_post_content(self, content: str) -> str:
        """Clean post content by removing metadata"""
        # Remove common metadata patterns
        patterns_to_remove = [
            r'Author:\s*[^\n]+',
            r'Username:\s*[^\n]+',
            r'Posted:\s*[^\n]+',
            r'Likes?:\s*\d+',
            r'Comments?:\s*\d+',
            r'Shares?:\s*\d+',
            r'Retweets?:\s*\d+',
            r'\d+\.\s*',  # Numbering
        ]
        
        cleaned = content
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up whitespace
        cleaned = re.sub(r'\n+', '\n', cleaned).strip()
        
        return cleaned
    
    async def _analyze_sentiment(self, text: str) -> tuple[Optional[float], Optional[str]]:
        """Analyze sentiment of social media post"""
        if len(text) < 10:
            return None, None
        
        browser = AIBrowser({"log_level": "INFO"})
        
        sentiment_task = f"""
        Analyze the sentiment of this social media post:
        
        "{text}"
        
        Provide:
        1. Sentiment score from -1.0 (very negative) to +1.0 (very positive)
        2. Sentiment label: "positive", "negative", or "neutral"
        
        Consider context, tone, and emotional indicators.
        Format response as: "Score: X.X, Label: XXXX"
        """
        
        config = TaskConfig(
            task=sentiment_task,
            url="https://www.example.com",
            headless=True,
            max_steps=3,
            timeout=30000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            summary = result.get('summary', '')
            
            # Parse sentiment score and label
            score_match = re.search(r'score:\s*([-+]?\d*\.?\d+)', summary, re.IGNORECASE)
            label_match = re.search(r'label:\s*(positive|negative|neutral)', summary, re.IGNORECASE)
            
            score = None
            if score_match:
                try:
                    score = float(score_match.group(1))
                    score = max(-1.0, min(1.0, score))  # Clamp to valid range
                except ValueError:
                    pass
            
            label = None
            if label_match:
                label = label_match.group(1).lower()
            
            return score, label
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return None, None
        finally:
            await browser.cleanup()
    
    async def generate_social_media_report(self, all_posts: List[SocialMediaPost], query: str) -> Dict[str, Any]:
        """Generate comprehensive social media analysis report"""
        logger.info("[STATS] Generating comprehensive social media report...")
        
        if not all_posts:
            return {"error": "No posts to analyze"}
        
        # Basic statistics
        total_posts = len(all_posts)
        platforms = {}
        sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
        total_engagement = 0
        
        for post in all_posts:
            # Platform distribution
            platforms[post.platform] = platforms.get(post.platform, 0) + 1
            
            # Sentiment distribution
            if post.sentiment_label:
                sentiment_distribution[post.sentiment_label] += 1
            
            # Engagement metrics
            engagement = (post.likes_count or 0) + (post.comments_count or 0) + (post.shares_count or 0)
            total_engagement += engagement
        
        # Extract trending hashtags
        all_hashtags = []
        for post in all_posts:
            all_hashtags.extend(post.hashtags)
        
        hashtag_counts = {}
        for hashtag in all_hashtags:
            hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        trending_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Find top influencers (by engagement)
        author_engagement = {}
        for post in all_posts:
            engagement = (post.likes_count or 0) + (post.comments_count or 0) + (post.shares_count or 0)
            if post.author != "Unknown":
                author_engagement[post.author] = author_engagement.get(post.author, 0) + engagement
        
        top_influencers = sorted(author_engagement.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # AI-powered insights generation
        insights = await self._generate_ai_insights(all_posts, query)
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "search_query": query,
            "summary_statistics": {
                "total_posts_analyzed": total_posts,
                "platforms_covered": list(platforms.keys()),
                "total_engagement": total_engagement,
                "average_engagement": total_engagement / total_posts if total_posts > 0 else 0
            },
            "platform_breakdown": platforms,
            "sentiment_analysis": {
                "distribution": sentiment_distribution,
                "sentiment_percentage": {
                    "positive": (sentiment_distribution["positive"] / total_posts) * 100 if total_posts > 0 else 0,
                    "negative": (sentiment_distribution["negative"] / total_posts) * 100 if total_posts > 0 else 0,
                    "neutral": (sentiment_distribution["neutral"] / total_posts) * 100 if total_posts > 0 else 0
                }
            },
            "trending_hashtags": trending_hashtags,
            "top_influencers": top_influencers,
            "ai_insights": insights,
            "sample_posts": [
                {
                    "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                    "author": post.author,
                    "platform": post.platform,
                    "sentiment": post.sentiment_label,
                    "engagement": (post.likes_count or 0) + (post.comments_count or 0) + (post.shares_count or 0)
                }
                for post in sorted(all_posts, key=lambda x: (x.likes_count or 0) + (x.comments_count or 0) + (x.shares_count or 0), reverse=True)[:5]
            ],
            "posts_data": [asdict(post) for post in all_posts]
        }
        
        return report
    
    async def _generate_ai_insights(self, posts: List[SocialMediaPost], query: str) -> Dict[str, Any]:
        """Generate AI-powered insights from social media posts"""
        browser = AIBrowser({"log_level": "INFO"})
        
        # Prepare posts summary for analysis
        posts_summary = []
        for post in posts[:10]:  # Limit to 10 posts for analysis
            posts_summary.append({
                "platform": post.platform,
                "author": post.author,
                "content": post.content[:300],  # First 300 chars
                "sentiment": post.sentiment_label,
                "engagement": (post.likes_count or 0) + (post.comments_count or 0) + (post.shares_count or 0),
                "hashtags": post.hashtags[:5]  # Top 5 hashtags
            })
        
        insights_task = f"""
        Analyze these social media posts about '{query}' and provide insights:
        
        Posts Data: {json.dumps(posts_summary, indent=2)}
        
        Generate comprehensive insights including:
        1. Key themes and topics discussed
        2. Public sentiment and opinion trends
        3. Influential voices and thought leaders
        4. Emerging concerns or opportunities
        5. Recommendations for engagement strategy
        6. Market intelligence and competitive insights
        7. Content performance patterns
        8. Audience behavior observations
        
        Provide actionable insights that would be valuable for business intelligence.
        """
        
        config = TaskConfig(
            task=insights_task,
            url="https://www.example.com",
            headless=True,
            max_steps=5,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            insights = {
                "ai_analysis": result.get('summary', ''),
                "key_themes": self._extract_themes(result.get('summary', '')),
                "recommendations": self._extract_recommendations(result.get('summary', '')),
                "market_intelligence": result.get('extracted_data', {}),
                "generated_at": datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            return {"error": str(e)}
        finally:
            await browser.cleanup()
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract key themes from AI analysis"""
        themes = []
        
        # Look for theme indicators
        theme_patterns = [
            r'theme[s]?:\s*([^\n.]+)',
            r'topic[s]?:\s*([^\n.]+)',
            r'trend[s]?:\s*([^\n.]+)'
        ]
        
        for pattern in theme_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            themes.extend([theme.strip() for theme in matches])
        
        return themes[:5]  # Top 5 themes
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from AI analysis"""
        recommendations = []
        
        # Look for recommendation sections
        rec_patterns = [
            r'recommendation[s]?:\s*([^\n.]+)',
            r'suggest[s]?:\s*([^\n.]+)',
            r'should:\s*([^\n.]+)'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            recommendations.extend([rec.strip() for rec in matches])
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def comprehensive_social_analysis(self, query: str, platforms: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive social media analysis across multiple platforms"""
        logger.info(f"[SEARCH] Starting comprehensive social media analysis for: {query}")
        
        if not platforms:
            platforms = ["twitter", "linkedin", "reddit"]
        
        all_posts = []
        platform_results = {}
        
        # Analyze each platform
        for platform in platforms:
            try:
                if platform.lower() == "twitter":
                    posts = await self.analyze_twitter_topic(query, max_posts=8)
                elif platform.lower() == "linkedin":
                    posts = await self.analyze_linkedin_content(query, max_posts=8)
                elif platform.lower() == "reddit":
                    # For Reddit, try relevant subreddit based on query
                    subreddit = self._suggest_subreddit(query)
                    posts = await self.analyze_reddit_discussions(subreddit, query, max_posts=8)
                else:
                    continue
                
                all_posts.extend(posts)
                platform_results[platform] = len(posts)
                logger.info(f"[SUCCESS] {platform}: {len(posts)} posts analyzed")
                
                # Small delay between platforms
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"[ERROR] {platform} analysis failed: {e}")
                platform_results[platform] = 0
        
        # Generate comprehensive report
        report = await self.generate_social_media_report(all_posts, query)
        report["platform_results"] = platform_results
        report["analysis_scope"] = platforms
        
        # Save results
        await self._save_analysis_results(report)
        
        return report
    
    def _suggest_subreddit(self, query: str) -> str:
        """Suggest relevant subreddit based on query"""
        query_lower = query.lower()
        
        # Technology topics
        if any(word in query_lower for word in ['ai', 'machine learning', 'programming', 'software', 'tech']):
            return "technology"
        
        # Business topics  
        if any(word in query_lower for word in ['business', 'startup', 'entrepreneur', 'marketing']):
            return "entrepreneur"
        
        # Finance topics
        if any(word in query_lower for word in ['crypto', 'bitcoin', 'investing', 'stocks', 'finance']):
            return "investing"
        
        # Gaming topics
        if any(word in query_lower for word in ['gaming', 'game', 'esports']):
            return "gaming"
        
        # Default to general discussion
        return "todayilearned"
    
    async def _save_analysis_results(self, report: Dict[str, Any]):
        """Save social media analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.results_dir / f"social_media_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        
        # Save human-readable summary
        summary_file = self.results_dir / f"social_media_summary_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("SOCIAL MEDIA ANALYSIS REPORT\n")
            f.write("="*50 + "\n\n")
            f.write(f"Search Query: {report['search_query']}\n")
            f.write(f"Analysis Date: {report['analysis_timestamp']}\n")
            f.write(f"Total Posts: {report['summary_statistics']['total_posts_analyzed']}\n")
            f.write(f"Platforms: {', '.join(report['summary_statistics']['platforms_covered'])}\n\n")
            
            # Sentiment analysis
            sentiment = report['sentiment_analysis']
            f.write("SENTIMENT ANALYSIS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Positive: {sentiment['sentiment_percentage']['positive']:.1f}%\n")
            f.write(f"Negative: {sentiment['sentiment_percentage']['negative']:.1f}%\n")
            f.write(f"Neutral: {sentiment['sentiment_percentage']['neutral']:.1f}%\n\n")
            
            # Trending hashtags
            if report.get('trending_hashtags'):
                f.write("TRENDING HASHTAGS:\n")
                f.write("-" * 20 + "\n")
                for hashtag, count in report['trending_hashtags'][:5]:
                    f.write(f"#{hashtag}: {count} mentions\n")
                f.write("\n")
            
            # Top posts
            f.write("TOP ENGAGING POSTS:\n")
            f.write("-" * 20 + "\n")
            for i, post in enumerate(report['sample_posts'][:3], 1):
                f.write(f"{i}. {post['content'][:100]}...\n")
                f.write(f"   Platform: {post['platform']} | Author: {post['author']}\n")
                f.write(f"   Engagement: {post['engagement']} | Sentiment: {post['sentiment']}\n\n")
            
            # AI insights
            if report['ai_insights'].get('ai_analysis'):
                f.write("AI INSIGHTS:\n")
                f.write("-" * 20 + "\n")
                f.write(report['ai_insights']['ai_analysis'][:1000])
                f.write("\n\n")
        
        logger.info(f"[FILE] Analysis saved to: {json_file}")
        logger.info(f"[FILE] Summary saved to: {summary_file}")


async def demo_social_media_analysis():
    """Demonstrate social media analysis capabilities"""
    print("\n" + "="*70)
    print("[MOBILE] AI-POWERED SOCIAL MEDIA CONTENT ANALYSIS")
    print("="*70)
    print("This demo monitors and analyzes social media content using")
    print("AI reasoning and browser automation across multiple platforms.\n")
    
    analyzer = SocialMediaAnalyzer()
    
    # Example topics to analyze
    analysis_topics = [
        "artificial intelligence",
        "remote work trends",
        "cryptocurrency market",
        "sustainable technology",
        "digital marketing strategies"
    ]
    
    print("Select a topic to analyze:")
    for i, topic in enumerate(analysis_topics, 1):
        print(f"{i}. {topic.title()}")
    print(f"{len(analysis_topics) + 1}. Custom topic")
    
    try:
        choice = input(f"\nEnter choice (1-{len(analysis_topics) + 1}): ").strip()
        
        if choice == str(len(analysis_topics) + 1):
            query = input("Enter topic to analyze: ").strip()
            if not query:
                query = analysis_topics[0]  # Default
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(analysis_topics):
                    query = analysis_topics[choice_idx]
                else:
                    query = analysis_topics[0]  # Default
            except ValueError:
                query = analysis_topics[0]  # Default
        
        # Platform selection
        print(f"\nSelect platforms to analyze (comma-separated):")
        print("Options: twitter, linkedin, reddit")
        platform_input = input("Platforms [twitter,linkedin,reddit]: ").strip()
        
        if platform_input:
            platforms = [p.strip().lower() for p in platform_input.split(',')]
            platforms = [p for p in platforms if p in ['twitter', 'linkedin', 'reddit']]
        else:
            platforms = ['twitter', 'linkedin', 'reddit']
        
        if not platforms:
            platforms = ['twitter']  # Fallback
        
        print(f"\n[SEARCH] Analyzing: {query}")
        print(f"[MOBILE] Platforms: {', '.join(platforms)}")
        print("[TIME] This may take 5-8 minutes depending on platform availability...\n")
        
        # Run comprehensive analysis
        results = await analyzer.comprehensive_social_analysis(query, platforms)
        
        if "error" in results:
            print(f"[ERROR] Analysis failed: {results['error']}")
            return
        
        # Display results
        print("\n" + "="*50)
        print("[STATS] SOCIAL MEDIA ANALYSIS RESULTS")
        print("="*50)
        
        print(f"Topic: {results['search_query']}")
        print(f"Posts Analyzed: {results['summary_statistics']['total_posts_analyzed']}")
        print(f"Total Engagement: {results['summary_statistics']['total_engagement']:,}")
        print(f"Platforms: {', '.join(results['summary_statistics']['platforms_covered'])}")
        
        # Platform breakdown
        print(f"\n[MOBILE] PLATFORM BREAKDOWN:")
        print("-" * 25)
        for platform, count in results['platform_results'].items():
            print(f"{platform.title()}: {count} posts analyzed")
        
        # Sentiment analysis
        sentiment = results['sentiment_analysis']
        print(f"\n[SENTIMENT] SENTIMENT ANALYSIS:")
        print("-" * 25)
        print(f"Positive: {sentiment['sentiment_percentage']['positive']:.1f}%")
        print(f"Negative: {sentiment['sentiment_percentage']['negative']:.1f}%")
        print(f"Neutral: {sentiment['sentiment_percentage']['neutral']:.1f}%")
        
        # Trending hashtags
        if results.get('trending_hashtags'):
            print(f"\n[HASHTAG] TRENDING HASHTAGS:")
            print("-" * 25)
            for hashtag, count in results['trending_hashtags'][:5]:
                print(f"#{hashtag}: {count} mentions")
        
        # Top influencers
        if results.get('top_influencers'):
            print(f"\n[STAR] TOP VOICES:")
            print("-" * 25)
            for author, engagement in results['top_influencers'][:3]:
                print(f"{author}: {engagement:,} total engagement")
        
        # Sample posts
        print(f"\n[CONTENT] TOP ENGAGING POSTS:")
        print("-" * 30)
        for i, post in enumerate(results['sample_posts'][:3], 1):
            print(f"\n{i}. {post['content'][:150]}...")
            print(f"   [USER] {post['author']} on {post['platform']}")
            print(f"   [STATS] {post['engagement']:,} engagement | [SENTIMENT] {post['sentiment']}")
        
        # AI insights preview
        if results['ai_insights'].get('ai_analysis'):
            print(f"\n[AI] AI INSIGHTS PREVIEW:")
            print("-" * 30)
            analysis = results['ai_insights']['ai_analysis']
            # Show first few lines
            for line in analysis.split('\n')[:4]:
                if line.strip():
                    print(f"  {line.strip()}")
            if len(analysis.split('\n')) > 4:
                print("  ... (see full analysis in output files)")
        
        print(f"\n[STATS] Detailed analysis saved to: examples/outputs/social_media_analysis/")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_social_media_analysis())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()