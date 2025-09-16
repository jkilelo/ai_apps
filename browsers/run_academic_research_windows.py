#!/usr/bin/env python3
"""
Windows-compatible Academic Research Example
Real-world example with live LLM integration
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger without emojis for Windows compatibility
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


class WindowsCompatibleAcademicDemo:
    """Windows-compatible academic research demo"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/academic_research")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"academic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def search_academic_papers(self, research_topic: str) -> Dict[str, Any]:
        """Search for academic papers with live LLM integration"""
        logger.info(f"Searching Google Scholar for: {research_topic}")
        
        browser = AIBrowser({"log_level": "INFO"})
        start_time = asyncio.get_event_loop().time()
        
        try:
            task = f"""
            Go to Google Scholar (scholar.google.com) and search for '{research_topic}'.
            Extract information from the first 5-8 relevant academic papers:
            1. Paper title and authors
            2. Publication year and venue
            3. Abstract or summary text
            4. Citation count if available
            5. Publisher/journal information
            6. DOI or paper URL if available
            
            Focus on recent and highly-cited papers.
            Handle any consent forms, cookies, or region selections automatically.
            Provide systematic extraction of academic information.
            """
            
            config = TaskConfig(
                task=task,
                url="https://scholar.google.com",
                headless=True,
                max_steps=18,  # More steps for academic search complexity
                timeout=120000,  # Extended timeout for comprehensive search
                screenshot_on_error=True
            )
            
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "research_topic": research_topic,
                "status": result.get('status', 'unknown'),
                "summary": result.get('summary', 'No summary available'),
                "extracted_data": result.get('extracted_data', {}),
                "final_url": result.get('final_url', ''),
                "response_time_ms": response_time,
                "success": result.get('status') == 'completed'
            }
            
        except Exception as e:
            logger.error(f"Academic search failed: {e}")
            return {
                "research_topic": research_topic,
                "status": "failed",
                "error": str(e),
                "success": False
            }
        finally:
            await browser.cleanup()
    
    def extract_academic_insights(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract academic insights from the search results"""
        if not result.get('success'):
            return {"error": "Search failed"}
        
        summary = result.get('summary', '')
        
        # Simple extraction patterns for academic info
        insights = {
            "research_topic": result.get('research_topic', ''),
            "papers_found": len(summary.split('\n')) if summary else 0,
            "key_findings": [],
            "recent_papers": [],
            "high_impact_papers": []
        }
        
        # Extract key information from summary
        lines = summary.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 30:  # Meaningful content
                # Look for paper titles (usually longer lines)
                if any(word in line.lower() for word in ['paper', 'study', 'research', 'analysis']):
                    if len(line) > 50:
                        insights["key_findings"].append(line[:200])  # First 200 chars
                
                # Look for recent years
                if any(year in line for year in ['2023', '2024', '2025']):
                    insights["recent_papers"].append(line[:150])
                
                # Look for citation indicators
                if any(indicator in line.lower() for indicator in ['cited', 'citations', 'references']):
                    insights["high_impact_papers"].append(line[:150])
        
        # Limit results to prevent overflow
        insights["key_findings"] = insights["key_findings"][:5]
        insights["recent_papers"] = insights["recent_papers"][:3]
        insights["high_impact_papers"] = insights["high_impact_papers"][:3]
        
        return insights
    
    async def run_demo(self):
        """Run the Windows-compatible academic research demo"""
        print("\n" + "="*70)
        print("AI-POWERED ACADEMIC RESEARCH - Windows Compatible")
        print("="*70)
        print("This demo showcases academic paper search with live LLM integration")
        print("Demonstrates real-world browser automation for research purposes")
        print()
        
        # Research topics for demonstration
        research_topics = [
            "machine learning browser automation 2024",
            "artificial intelligence web scraping",
            "automated testing playwright selenium",
            "natural language processing web data extraction"
        ]
        
        print("Select a research topic:")
        for i, topic in enumerate(research_topics, 1):
            print(f"{i}. {topic}")
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
            
            print(f"\nResearch Topic: {topic}")
            print("Running live academic search with AI analysis...")
            print("This will take 3-4 minutes for comprehensive research...")
            print()
            
            # Run the academic search with real LLM calls
            result = await self.search_academic_papers(topic)
            
            # Extract insights
            insights = self.extract_academic_insights(result)
            
            # Display results
            print("="*70)
            print("ACADEMIC RESEARCH RESULTS")
            print("="*70)
            
            print(f"Research Topic: {result['research_topic']}")
            print(f"Status: {result['status']}")
            print(f"Response Time: {result.get('response_time_ms', 0):.0f}ms")
            print(f"Success: {result.get('success', False)}")
            print()
            
            if result.get('success'):
                print("EXTRACTED ACADEMIC INFORMATION:")
                print("-" * 40)
                
                summary = result.get('summary', '')
                if summary:
                    # Show preview of findings
                    print("Research Summary:")
                    for line in summary.split('\n')[:12]:
                        if line.strip() and len(line.strip()) > 10:
                            print(f"  {line.strip()}")
                    print()
                
                # Show insights if available
                if not insights.get('error'):
                    if insights.get('key_findings'):
                        print("Key Findings:")
                        for finding in insights['key_findings'][:3]:
                            print(f"  - {finding}")
                        print()
                    
                    if insights.get('recent_papers'):
                        print("Recent Papers Found:")
                        for paper in insights['recent_papers'][:2]:
                            print(f"  - {paper}")
                        print()
                
                # Show final URL
                if result.get('final_url'):
                    print(f"Research conducted at: {result['final_url']}")
                
                print("SUCCESS: Live academic research with AI analysis completed!")
                
            else:
                print("FAILED: Could not complete the academic research")
                if result.get('error'):
                    print(f"Error: {result['error']}")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Combine results and insights
            full_results = {
                "search_results": result,
                "academic_insights": insights,
                "session_metadata": {
                    "timestamp": timestamp,
                    "session_id": self.session_id,
                    "demo_version": "windows_compatible"
                }
            }
            
            results_file = self.results_dir / f"academic_research_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(full_results, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"\nDetailed results saved to: {results_file}")
            print("="*70)
            
            return result
            
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            return None
        except Exception as e:
            print(f"\nDemo failed: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    """Main entry point for academic research demo"""
    try:
        demo = WindowsCompatibleAcademicDemo()
        result = await demo.run_demo()
        
        if result and result.get('success'):
            print("\nACADEMIC RESEARCH DEMO COMPLETED SUCCESSFULLY!")
            print("The AI Browser v2.0.0 successfully conducted academic research!")
        else:
            print("\nACADEMIC RESEARCH DEMO ENCOUNTERED ISSUES:")
            print("Check the error details above and system configuration.")
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())