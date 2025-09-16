#!/usr/bin/env python3
"""
Real-World Job Application Automation

This example demonstrates autonomous job search and application capabilities:
- Search major job boards (LinkedIn, Indeed, Glassdoor)
- Analyze job postings and requirements
- Match skills with job requirements
- Generate tailored cover letters and applications
- Track application status and follow-ups
- Handle dynamic forms and multi-step processes
- Store job data in memory for tracking

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended for best results)
- Working internet connection
- AI Browser v2.0.0 system components
- User profile data (resume, skills, preferences)

USAGE:
    python examples/real_world_job_automation.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


@dataclass
class UserProfile:
    """User profile for job applications"""
    name: str
    email: str
    phone: str
    location: str
    skills: List[str]
    experience_years: int
    current_role: str
    linkedin_url: str = ""
    portfolio_url: str = ""
    preferred_salary_min: Optional[int] = None
    preferred_salary_max: Optional[int] = None
    work_authorization: str = "Authorized to work"
    remote_preference: str = "Open to remote/hybrid/onsite"
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class JobPosting:
    """Structured job posting information"""
    title: str
    company: str
    location: str
    salary_range: Optional[str] = None
    job_type: str = "Full-time"  # Full-time, Part-time, Contract, etc.
    remote_option: bool = False
    requirements: List[str] = None
    responsibilities: List[str] = None
    benefits: List[str] = None
    posted_date: Optional[str] = None
    application_deadline: Optional[str] = None
    job_url: str = ""
    source: str = ""
    job_id: str = ""
    description: str = ""
    skill_match_score: float = 0.0
    extracted_at: str = ""
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.responsibilities is None:
            self.responsibilities = []
        if self.benefits is None:
            self.benefits = []
        if not self.extracted_at:
            self.extracted_at = datetime.now().isoformat()
        if not self.job_id:
            self.job_id = f"{self.source}_{hash(self.job_url)}_{int(datetime.now().timestamp())}"


class JobSearchAgent:
    """AI-powered job search and application automation"""
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.results_dir = Path("examples/outputs/job_automation")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"job_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.applications_log = []
    
    async def search_linkedin_jobs(self, job_query: str, location: str = "") -> List[JobPosting]:
        """Search jobs on LinkedIn"""
        logger.info(f"[JOB] Searching LinkedIn for: {job_query}")
        
        if not location:
            location = self.user_profile.location
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Go to LinkedIn.com and search for jobs with these parameters:
        - Job title/keywords: '{job_query}'
        - Location: '{location}'
        
        Find the first 3-5 relevant job postings and extract for each:
        1. Job title and company name
        2. Location and remote work options
        3. Salary range if available
        4. Job type (full-time, part-time, contract)
        5. Key requirements and qualifications
        6. Job responsibilities and description
        7. Benefits mentioned
        8. Posted date and application deadline
        9. Direct application link/URL
        
        Handle login prompts by clicking "Not now" or similar to browse publicly.
        Focus on jobs that match the user's profile.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.linkedin.com/jobs",
            headless=True,
            max_steps=20,
            timeout=120000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse LinkedIn job results
            jobs = self._parse_job_listings(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'LinkedIn',
                result.get('final_url', '')
            )
            
            logger.info(f"[SUCCESS] Found {len(jobs)} LinkedIn jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"[ERROR] LinkedIn search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def search_indeed_jobs(self, job_query: str, location: str = "") -> List[JobPosting]:
        """Search jobs on Indeed"""
        logger.info(f"[SEARCH] Searching Indeed for: {job_query}")
        
        if not location:
            location = self.user_profile.location
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Go to Indeed.com and search for jobs:
        - Keywords: '{job_query}'
        - Location: '{location}'
        
        Find 3-5 relevant job postings and extract:
        1. Job title and company
        2. Location and work arrangement
        3. Salary information if shown
        4. Job type and employment terms
        5. Required skills and experience
        6. Job description highlights
        7. Company benefits
        8. How long ago posted
        9. Application process/link
        
        Look for "Easy Apply" options and well-matched positions.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.indeed.com",
            headless=True,
            max_steps=20,
            timeout=120000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse Indeed job results
            jobs = self._parse_job_listings(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Indeed',
                result.get('final_url', '')
            )
            
            logger.info(f"[SUCCESS] Found {len(jobs)} Indeed jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"[ERROR] Indeed search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def search_glassdoor_jobs(self, job_query: str, location: str = "") -> List[JobPosting]:
        """Search jobs on Glassdoor"""
        logger.info(f"[COMPANY] Searching Glassdoor for: {job_query}")
        
        if not location:
            location = self.user_profile.location
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Go to Glassdoor.com and search for jobs:
        - Job title: '{job_query}'
        - Location: '{location}'
        
        Find 3-5 job postings and extract:
        1. Position title and company name
        2. Location and remote work policy
        3. Estimated salary range
        4. Company rating and size
        5. Required qualifications
        6. Role responsibilities
        7. Company benefits and culture
        8. When posted
        9. Application method
        
        Focus on companies with good ratings and clear job descriptions.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.glassdoor.com/Job/index.htm",
            headless=True,
            max_steps=20,
            timeout=120000,
            screenshot_on_error=True
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse Glassdoor job results
            jobs = self._parse_job_listings(
                result.get('summary', ''),
                result.get('extracted_data', {}),
                'Glassdoor',
                result.get('final_url', '')
            )
            
            logger.info(f"[SUCCESS] Found {len(jobs)} Glassdoor jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"[ERROR] Glassdoor search failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    def _parse_job_listings(self, summary: str, extracted_data: dict, source: str, url: str) -> List[JobPosting]:
        """Parse job listings from AI response"""
        jobs = []
        
        # Try to split the summary into individual job entries
        # Look for common patterns that indicate separate jobs
        job_sections = []
        
        if "Job 1:" in summary or "1." in summary:
            # Numbered format
            sections = re.split(r'\n(?=(?:Job\s+)?\d+[.:\)])', summary)
            job_sections = [s.strip() for s in sections if s.strip()]
        elif "\n\n" in summary:
            # Double line break format
            job_sections = [s.strip() for s in summary.split('\n\n') if len(s.strip()) > 50]
        else:
            # Single entry
            job_sections = [summary]
        
        for i, section in enumerate(job_sections[:5]):  # Limit to 5 jobs
            if len(section) < 30:  # Skip very short sections
                continue
                
            job = self._parse_single_job(section, source, url, i+1)
            if job:
                jobs.append(job)
        
        return jobs
    
    def _parse_single_job(self, job_text: str, source: str, base_url: str, job_number: int) -> Optional[JobPosting]:
        """Parse a single job posting from text"""
        try:
            # Extract job title (usually first meaningful line)
            lines = [line.strip() for line in job_text.split('\n') if line.strip()]
            title = "Unknown Position"
            company = "Unknown Company"
            
            # Try to find title and company
            for line in lines[:3]:
                if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator']):
                    title = line
                    break
            
            # Look for company name
            for line in lines:
                if any(word in line.lower() for word in ['company:', 'at ', 'inc', 'corp', 'llc']):
                    company = line.replace('Company:', '').replace('at ', '').strip()
                    break
            
            # Extract location
            location = "Remote/Flexible"
            location_patterns = [
                r'Location:\s*([^,\n]+)',
                r'([A-Za-z\s]+,\s*[A-Z]{2})',
                r'(Remote|Hybrid|On-site)',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, job_text, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    break
            
            # Extract salary if mentioned
            salary_range = None
            salary_patterns = [
                r'\$(\d{2,3}),?(\d{3})\s*-\s*\$(\d{2,3}),?(\d{3})',
                r'\$(\d{2,3})k?\s*-\s*\$?(\d{2,3})k',
                r'(\d{2,3}),?(\d{3})\s*-\s*(\d{2,3}),?(\d{3})\s*per year'
            ]
            for pattern in salary_patterns:
                match = re.search(pattern, job_text, re.IGNORECASE)
                if match:
                    salary_range = match.group(0)
                    break
            
            # Check for remote work
            remote_option = any(word in job_text.lower() for word in ['remote', 'work from home', 'wfh', 'telecommute'])
            
            # Extract requirements
            requirements = []
            req_section = re.search(r'(?:requirements?|qualifications?|skills?):(.*?)(?:\n\n|\n[A-Z]|$)', job_text, re.IGNORECASE | re.DOTALL)
            if req_section:
                req_text = req_section.group(1)
                # Split by bullet points or line breaks
                requirements = [req.strip('•-* ').strip() for req in req_text.split('\n') if req.strip()]
                requirements = [req for req in requirements if len(req) > 5][:10]  # Limit to 10
            
            # Calculate skill match score
            skill_match_score = self._calculate_skill_match(job_text, self.user_profile.skills)
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                salary_range=salary_range,
                remote_option=remote_option,
                requirements=requirements,
                job_url=f"{base_url}#job{job_number}",
                source=source,
                description=job_text[:500],  # First 500 chars
                skill_match_score=skill_match_score
            )
            
        except Exception as e:
            logger.error(f"Failed to parse job posting: {e}")
            return None
    
    def _calculate_skill_match(self, job_text: str, user_skills: List[str]) -> float:
        """Calculate how well user skills match job requirements"""
        if not user_skills:
            return 0.0
        
        job_text_lower = job_text.lower()
        matched_skills = 0
        
        for skill in user_skills:
            if skill.lower() in job_text_lower:
                matched_skills += 1
        
        return matched_skills / len(user_skills)
    
    async def generate_cover_letter(self, job: JobPosting) -> str:
        """Generate tailored cover letter using AI"""
        logger.info(f"[WRITING] Generating cover letter for: {job.title} at {job.company}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        task = f"""
        Write a professional, tailored cover letter for this job application:
        
        User Profile:
        - Name: {self.user_profile.name}
        - Current Role: {self.user_profile.current_role}
        - Experience: {self.user_profile.experience_years} years
        - Key Skills: {', '.join(self.user_profile.skills)}
        - Location: {self.user_profile.location}
        
        Job Details:
        - Position: {job.title}
        - Company: {job.company}
        - Location: {job.location}
        - Requirements: {', '.join(job.requirements[:5])}
        - Job Description: {job.description}
        
        Create a cover letter that:
        1. Addresses the specific company and position
        2. Highlights relevant experience and skills
        3. Shows understanding of job requirements
        4. Demonstrates enthusiasm and cultural fit
        5. Is professional but personable
        6. Is 250-400 words in length
        
        Format as a proper business letter with date, company address, greeting, body paragraphs, and professional closing.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.example.com",  # Static page for text generation
            headless=True,
            max_steps=5,
            timeout=60000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            cover_letter = result.get('summary', '')
            if not cover_letter or len(cover_letter) < 100:
                # Fallback basic cover letter
                cover_letter = self._generate_basic_cover_letter(job)
            
            return cover_letter
            
        except Exception as e:
            logger.error(f"[ERROR] Cover letter generation failed: {e}")
            return self._generate_basic_cover_letter(job)
        finally:
            await browser.cleanup()
    
    def _generate_basic_cover_letter(self, job: JobPosting) -> str:
        """Generate basic cover letter template"""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job.title} position at {job.company}. With {self.user_profile.experience_years} years of experience in {self.user_profile.current_role} and expertise in {', '.join(self.user_profile.skills[:3])}, I am confident I would be a valuable addition to your team.

My background includes:
• {self.user_profile.experience_years} years of professional experience
• Strong skills in {', '.join(self.user_profile.skills[:5])}
• Proven track record in {self.user_profile.current_role}

I am particularly drawn to this opportunity at {job.company} because of your reputation for innovation and excellence. The {job.title} role aligns perfectly with my career goals and expertise.

I would welcome the opportunity to discuss how my skills and experience can contribute to your team's success. Thank you for considering my application.

Sincerely,
{self.user_profile.name}
{self.user_profile.email}
{self.user_profile.phone}"""
    
    async def comprehensive_job_search(self, job_query: str, location: str = "") -> Dict[str, Any]:
        """Run comprehensive job search across all platforms"""
        logger.info(f"[TARGET] Starting comprehensive job search for: {job_query}")
        
        # Search all platforms concurrently
        search_tasks = [
            self.search_linkedin_jobs(job_query, location),
            self.search_indeed_jobs(job_query, location),
            self.search_glassdoor_jobs(job_query, location)
        ]
        
        try:
            job_results = await asyncio.wait_for(
                asyncio.gather(*search_tasks, return_exceptions=True),
                timeout=400  # 6-7 minutes total
            )
            
            # Combine all jobs
            all_jobs = []
            platform_success = {}
            
            for i, result in enumerate(job_results):
                platform = ['LinkedIn', 'Indeed', 'Glassdoor'][i]
                if isinstance(result, list):
                    all_jobs.extend(result)
                    platform_success[platform] = len(result)
                else:
                    platform_success[platform] = 0
                    logger.error(f"{platform} search failed: {result}")
            
            # Sort jobs by skill match score
            all_jobs.sort(key=lambda x: x.skill_match_score, reverse=True)
            
            # Generate analysis
            analysis = await self._analyze_job_market(all_jobs, job_query)
            
            search_results = {
                "query": job_query,
                "location": location or self.user_profile.location,
                "search_timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "total_jobs_found": len(all_jobs),
                "platform_results": platform_success,
                "jobs": [asdict(job) for job in all_jobs],
                "market_analysis": analysis,
                "top_matches": [asdict(job) for job in all_jobs[:5]],  # Top 5 matches
                "user_profile": self.user_profile.to_dict()
            }
            
            # Save results
            await self._save_job_search_results(search_results)
            
            return search_results
            
        except asyncio.TimeoutError:
            logger.error("[ERROR] Job search timed out")
            return {"error": "Search timed out", "query": job_query}
        except Exception as e:
            logger.error(f"[ERROR] Job search failed: {e}")
            return {"error": str(e), "query": job_query}
    
    async def _analyze_job_market(self, jobs: List[JobPosting], query: str) -> Dict[str, Any]:
        """Analyze job market trends and insights"""
        if not jobs:
            return {"error": "No jobs to analyze"}
        
        # Basic statistics
        total_jobs = len(jobs)
        remote_jobs = sum(1 for job in jobs if job.remote_option)
        avg_match_score = sum(job.skill_match_score for job in jobs) / total_jobs
        
        # Company analysis
        companies = {}
        for job in jobs:
            companies[job.company] = companies.get(job.company, 0) + 1
        
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Location analysis
        locations = {}
        for job in jobs:
            locations[job.location] = locations.get(job.location, 0) + 1
        
        top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Skill requirements analysis
        all_requirements = []
        for job in jobs:
            all_requirements.extend([req.lower() for req in job.requirements])
        
        skill_counts = {}
        for req in all_requirements:
            for skill in self.user_profile.skills:
                if skill.lower() in req:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        in_demand_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_jobs_analyzed": total_jobs,
            "remote_jobs_percentage": (remote_jobs / total_jobs) * 100 if total_jobs > 0 else 0,
            "average_skill_match": avg_match_score,
            "top_hiring_companies": top_companies,
            "popular_locations": top_locations,
            "in_demand_user_skills": in_demand_skills,
            "best_matches": [f"{job.title} at {job.company}" for job in jobs[:3]],
            "market_insights": f"Found {total_jobs} {query} positions. {remote_jobs} offer remote work. Average skill match: {avg_match_score:.1%}"
        }
    
    async def _save_job_search_results(self, results: Dict[str, Any]):
        """Save job search results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"job_search_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        # Save human-readable report
        report_file = self.results_dir / f"job_search_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("JOB SEARCH REPORT\n")
            f.write("="*50 + "\n\n")
            f.write(f"Search Query: {results['query']}\n")
            f.write(f"Location: {results['location']}\n")
            f.write(f"Search Date: {results['search_timestamp']}\n")
            f.write(f"Total Jobs Found: {results['total_jobs_found']}\n\n")
            
            # Platform breakdown
            f.write("PLATFORM RESULTS:\n")
            f.write("-" * 20 + "\n")
            for platform, count in results['platform_results'].items():
                f.write(f"{platform}: {count} jobs\n")
            
            # Market analysis
            if 'market_analysis' in results:
                analysis = results['market_analysis']
                f.write(f"\nMARKET ANALYSIS:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Remote Jobs: {analysis.get('remote_jobs_percentage', 0):.1f}%\n")
                f.write(f"Avg Skill Match: {analysis.get('average_skill_match', 0):.1%}\n")
                
                if analysis.get('top_hiring_companies'):
                    f.write(f"\nTop Hiring Companies:\n")
                    for company, count in analysis['top_hiring_companies']:
                        f.write(f"  {company}: {count} jobs\n")
            
            # Top job matches
            f.write(f"\nTOP JOB MATCHES:\n")
            f.write("-" * 20 + "\n")
            for i, job in enumerate(results.get('top_matches', [])[:5], 1):
                f.write(f"\n{i}. {job['title']} at {job['company']}\n")
                f.write(f"   Location: {job['location']}\n")
                f.write(f"   Match Score: {job['skill_match_score']:.1%}\n")
                if job['salary_range']:
                    f.write(f"   Salary: {job['salary_range']}\n")
                f.write(f"   Source: {job['source']}\n")
        
        logger.info(f"[FILE] Results saved to: {json_file}")
        logger.info(f"[FILE] Report saved to: {report_file}")


async def demo_job_automation():
    """Demonstrate job automation capabilities"""
    print("\n" + "="*70)
    print("[*] AI-POWERED JOB SEARCH & APPLICATION AUTOMATION")
    print("="*70)
    print("This demo will search job boards and analyze opportunities using")
    print("AI reasoning and real browser automation.\n")
    
    # Get user profile information
    print("First, let's create your job search profile:")
    print("(Press Enter to use defaults for demo)")
    
    name = input("Full Name [John Doe]: ").strip() or "John Doe"
    email = input("Email [john.doe@email.com]: ").strip() or "john.doe@email.com"
    phone = input("Phone [+1-555-123-4567]: ").strip() or "+1-555-123-4567"
    location = input("Location [San Francisco, CA]: ").strip() or "San Francisco, CA"
    current_role = input("Current Role [Software Engineer]: ").strip() or "Software Engineer"
    experience_years = input("Years of Experience [5]: ").strip() or "5"
    
    try:
        experience_years = int(experience_years)
    except ValueError:
        experience_years = 5
    
    # Skills input
    skills_input = input("Key Skills (comma separated) [Python, JavaScript, React]: ").strip()
    if skills_input:
        skills = [skill.strip() for skill in skills_input.split(',')]
    else:
        skills = ["Python", "JavaScript", "React", "SQL", "AWS", "Docker", "Git"]
    
    # Create user profile
    user_profile = UserProfile(
        name=name,
        email=email,
        phone=phone,
        location=location,
        skills=skills,
        experience_years=experience_years,
        current_role=current_role,
        linkedin_url="https://linkedin.com/in/johndoe",
        work_authorization="Authorized to work in the US",
        remote_preference="Open to remote/hybrid/onsite"
    )
    
    agent = JobSearchAgent(user_profile)
    
    # Job search queries
    job_queries = [
        "Software Engineer",
        "Full Stack Developer",
        "Python Developer",
        "DevOps Engineer",
        "Data Scientist"
    ]
    
    print(f"\nSelect a job type to search:")
    for i, query in enumerate(job_queries, 1):
        print(f"{i}. {query}")
    print(f"{len(job_queries) + 1}. Custom job search")
    
    try:
        choice = input(f"\nEnter choice (1-{len(job_queries) + 1}): ").strip()
        
        if choice == str(len(job_queries) + 1):
            query = input("Enter job title/keywords: ").strip()
            if not query:
                query = job_queries[0]  # Default
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(job_queries):
                    query = job_queries[choice_idx]
                else:
                    query = job_queries[0]  # Default
            except ValueError:
                query = job_queries[0]  # Default
        
        print(f"\n[SEARCH] Searching for: {query}")
        print(f"[LOCATION] Location: {user_profile.location}")
        print("[TIME]  This may take 5-7 minutes to search all job boards...\n")
        
        # Run comprehensive job search
        results = await agent.comprehensive_job_search(query, user_profile.location)
        
        if "error" in results:
            print(f"[ERROR] Job search failed: {results['error']}")
            return
        
        # Display results summary
        print("\n" + "="*50)
        print("[TARGET] JOB SEARCH RESULTS SUMMARY")
        print("="*50)
        
        print(f"Search Query: {results['query']}")
        print(f"Total Jobs Found: {results['total_jobs_found']}")
        print(f"Platforms Searched: {list(results['platform_results'].keys())}")
        
        # Platform breakdown
        print(f"\n[STATS] PLATFORM BREAKDOWN:")
        print("-" * 25)
        for platform, count in results['platform_results'].items():
            print(f"{platform}: {count} jobs")
        
        # Market analysis
        if 'market_analysis' in results:
            analysis = results['market_analysis']
            print(f"\n[INSIGHTS] MARKET INSIGHTS:")
            print("-" * 25)
            print(f"Remote Jobs Available: {analysis.get('remote_jobs_percentage', 0):.1f}%")
            print(f"Average Skill Match: {analysis.get('average_skill_match', 0):.1%}")
            print(f"Market Summary: {analysis.get('market_insights', 'N/A')}")
            
            if analysis.get('top_hiring_companies'):
                print(f"\n[COMPANY] TOP HIRING COMPANIES:")
                print("-" * 25)
                for company, count in analysis['top_hiring_companies'][:3]:
                    print(f"• {company}: {count} openings")
        
        # Show top matches
        print(f"\n[TOP] TOP JOB MATCHES FOR YOU:")
        print("-" * 30)
        for i, job in enumerate(results.get('top_matches', [])[:5], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Match Score: {job['skill_match_score']:.1%}")
            print(f"   Source: {job['source']}")
            if job['salary_range']:
                print(f"   Salary: {job['salary_range']}")
            if job['remote_option']:
                print(f"   [REMOTE] Remote Work Available")
        
        # Offer to generate cover letter for top match
        if results.get('top_matches'):
            top_job_data = results['top_matches'][0]
            top_job = JobPosting(**top_job_data)
            
            generate_letter = input(f"\n[WRITING]  Generate cover letter for top match? (y/n) [y]: ").strip().lower()
            if generate_letter in ['', 'y', 'yes']:
                print(f"\n[GENERATING] Generating cover letter for: {top_job.title} at {top_job.company}")
                cover_letter = await agent.generate_cover_letter(top_job)
                
                # Save cover letter
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                letter_file = agent.results_dir / f"cover_letter_{timestamp}.txt"
                with open(letter_file, 'w', encoding='utf-8') as f:
                    f.write(cover_letter)
                
                print(f"\n[FILE] Cover letter generated and saved to: {letter_file}")
                print("\n" + "="*40)
                print("COVER LETTER PREVIEW:")
                print("="*40)
                # Show first few lines
                for line in cover_letter.split('\n')[:10]:
                    if line.strip():
                        print(line)
                if len(cover_letter.split('\n')) > 10:
                    print("... (see full letter in file)")
        
        print(f"\n[STATS] Detailed results saved to: examples/outputs/job_automation/")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_job_automation())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()