#!/usr/bin/env python3
"""
AI-Powered Educational Tutor System

Transforms casual learning conversations into structured educational pathways,
adaptive assessments, and personalized study plans.

Features:
- Natural language understanding of learning goals
- Skill level assessment through conversation
- Dynamic curriculum generation
- Adaptive quiz creation
- Progress tracking and analytics
- Multi-modal learning resources
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, create_model
import json
import random

from html_v3_ai import (
    LLMProvider, ConversationContext, ConversationIntent,
    AIFormChainGenerator
)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_v3 import FormChainEngine, FormStep, FormStepProcessor, FormFieldSpec, FieldType


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    READING = "reading"
    KINESTHETIC = "kinesthetic"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SubjectArea(str, Enum):
    PROGRAMMING = "programming"
    MATHEMATICS = "mathematics"
    LANGUAGE = "language"
    SCIENCE = "science"
    HISTORY = "history"
    BUSINESS = "business"
    ARTS = "arts"


class ContentType(str, Enum):
    VIDEO = "video"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    PROJECT = "project"
    DISCUSSION = "discussion"


class EducationAIProvider(LLMProvider):
    """Education-specific AI provider for personalized learning"""
    
    def __init__(self):
        self.subject_keywords = {
            SubjectArea.PROGRAMMING: ["python", "javascript", "coding", "programming", "software", "web", "app"],
            SubjectArea.MATHEMATICS: ["math", "calculus", "algebra", "statistics", "geometry"],
            SubjectArea.LANGUAGE: ["english", "spanish", "french", "language", "grammar", "writing"],
            SubjectArea.SCIENCE: ["physics", "chemistry", "biology", "science", "experiment"],
            SubjectArea.BUSINESS: ["business", "marketing", "finance", "management", "entrepreneurship"]
        }
        
        self.skill_indicators = {
            "beginner": ["new", "beginner", "start", "basics", "introduction", "never", "first time"],
            "intermediate": ["some experience", "familiar", "used before", "intermediate"],
            "advanced": ["experienced", "advanced", "professional", "years of"]
        }
        
        self.learning_resources = {
            SubjectArea.PROGRAMMING: {
                "python": {
                    SkillLevel.BEGINNER: [
                        {"title": "Python Basics", "type": ContentType.VIDEO, "duration": "2 hours"},
                        {"title": "Your First Python Program", "type": ContentType.INTERACTIVE, "duration": "30 min"},
                        {"title": "Python Syntax Guide", "type": ContentType.ARTICLE, "duration": "45 min"}
                    ],
                    SkillLevel.INTERMEDIATE: [
                        {"title": "Object-Oriented Python", "type": ContentType.VIDEO, "duration": "3 hours"},
                        {"title": "Web Development with Flask", "type": ContentType.PROJECT, "duration": "1 week"},
                        {"title": "Python Data Structures", "type": ContentType.INTERACTIVE, "duration": "2 hours"}
                    ]
                }
            }
        }
        
        self.assessment_templates = {
            "multiple_choice": {
                "format": "Select the best answer",
                "points": 1,
                "time_limit": 60
            },
            "coding_challenge": {
                "format": "Write code to solve the problem",
                "points": 5,
                "time_limit": 300
            },
            "essay": {
                "format": "Explain in your own words",
                "points": 3,
                "time_limit": 180
            }
        }
    
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze educational conversation for learning goals"""
        
        messages_text = " ".join([m["content"].lower() for m in context.messages])
        
        # Extract learning entities
        entities = {
            "subjects": [],
            "specific_topics": [],
            "skill_level": SkillLevel.BEGINNER,
            "learning_goals": [],
            "time_commitment": None,
            "preferred_style": None,
            "previous_experience": []
        }
        
        # Detect subjects
        for subject, keywords in self.subject_keywords.items():
            if any(keyword in messages_text for keyword in keywords):
                entities["subjects"].append(subject)
        
        # Extract specific topics
        if "python" in messages_text:
            entities["specific_topics"].append("Python")
        if "machine learning" in messages_text or "ml" in messages_text:
            entities["specific_topics"].append("Machine Learning")
        if "web development" in messages_text:
            entities["specific_topics"].append("Web Development")
        
        # Assess skill level
        for level, indicators in self.skill_indicators.items():
            if any(indicator in messages_text for indicator in indicators):
                entities["skill_level"] = SkillLevel(level)
                break
        
        # Extract learning goals
        if "job" in messages_text or "career" in messages_text:
            entities["learning_goals"].append("career_advancement")
        if "hobby" in messages_text or "fun" in messages_text:
            entities["learning_goals"].append("personal_interest")
        if "exam" in messages_text or "certification" in messages_text:
            entities["learning_goals"].append("certification")
        
        # Time commitment
        import re
        time_match = re.search(r'(\d+)\s*hours?\s*(?:per|a)\s*(?:week|day)', messages_text)
        if time_match:
            entities["time_commitment"] = f"{time_match.group(1)} hours"
        
        # Learning style preferences
        if "watch" in messages_text or "video" in messages_text:
            entities["preferred_style"] = LearningStyle.VISUAL
        elif "read" in messages_text or "book" in messages_text:
            entities["preferred_style"] = LearningStyle.READING
        elif "hands-on" in messages_text or "practice" in messages_text:
            entities["preferred_style"] = LearningStyle.KINESTHETIC
        
        # Generate learning path
        learning_path = self._generate_learning_path(entities)
        
        return {
            "intent": ConversationIntent.EDUCATIONAL,
            "entities": entities,
            "learning_path": learning_path,
            "recommendations": self._get_initial_recommendations(entities)
        }
    
    async def generate_form_schema(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate educational assessment form"""
        
        analysis = await self.analyze_conversation(context)
        entities = analysis["entities"]
        
        fields = []
        
        # Learning goals
        fields.append({
            "name": "learning_objectives",
            "type": "textarea",
            "label": "What do you want to achieve?",
            "placeholder": "E.g., Build a web app, Get a job as a developer, Learn for fun",
            "default": " ".join(context.messages[-1]["content"][:100] + "..."),
            "required": True
        })
        
        # Current knowledge assessment
        if entities["specific_topics"]:
            fields.append({
                "name": "self_assessment",
                "type": "section",
                "label": "Current Knowledge",
                "fields": [
                    {
                        "name": f"knowledge_{topic.lower().replace(' ', '_')}",
                        "type": "range",
                        "label": f"How well do you know {topic}?",
                        "min": 0,
                        "max": 10,
                        "default": 0 if entities["skill_level"] == SkillLevel.BEGINNER else 5,
                        "help_text": "0 = No knowledge, 10 = Expert"
                    } for topic in entities["specific_topics"][:3]
                ]
            })
        
        # Learning preferences
        fields.extend([
            {
                "name": "preferred_learning_style",
                "type": "checkbox_group",
                "label": "How do you prefer to learn?",
                "options": [
                    {"value": "videos", "label": "Video tutorials"},
                    {"value": "reading", "label": "Articles and documentation"},
                    {"value": "interactive", "label": "Interactive exercises"},
                    {"value": "projects", "label": "Hands-on projects"},
                    {"value": "mentorship", "label": "1-on-1 guidance"}
                ],
                "default": ["videos", "interactive"] if entities.get("preferred_style") == LearningStyle.VISUAL else ["reading"],
                "required": True
            },
            {
                "name": "time_availability",
                "type": "select",
                "label": "How much time can you dedicate?",
                "options": [
                    "Less than 5 hours/week",
                    "5-10 hours/week",
                    "10-20 hours/week",
                    "More than 20 hours/week"
                ],
                "default": entities.get("time_commitment", "5-10 hours/week"),
                "required": True
            }
        ])
        
        # Experience and background
        fields.append({
            "name": "background",
            "type": "textarea",
            "label": "Tell us about your background",
            "placeholder": "Previous experience, related skills, current job/studies...",
            "required": False
        })
        
        # Learning pace
        fields.append({
            "name": "learning_pace",
            "type": "radio",
            "label": "Preferred learning pace",
            "options": [
                {"value": "intensive", "label": "Intensive (Fast-paced, challenging)"},
                {"value": "moderate", "label": "Moderate (Balanced approach)"},
                {"value": "relaxed", "label": "Relaxed (Take your time)"}
            ],
            "default": "moderate",
            "required": True
        })
        
        # Quick skill test option
        if entities["specific_topics"]:
            fields.append({
                "name": "take_assessment",
                "type": "boolean",
                "label": "Would you like to take a quick skill assessment?",
                "default": True,
                "help_text": "5-minute test to better personalize your learning path"
            })
        
        return {
            "title": "Let's Create Your Personalized Learning Path",
            "description": f"Based on your interest in {', '.join(entities['specific_topics'])}, let's customize your journey",
            "fields": fields,
            "learning_path_preview": analysis["learning_path"]
        }
    
    async def process_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """Process educational form responses"""
        
        context.messages.append({"role": "user", "content": user_input})
        
        # Generate personalized curriculum
        curriculum = self._generate_curriculum(context)
        
        # Create assessment if requested
        assessment = None
        if "assessment" in user_input.lower():
            assessment = self._create_adaptive_assessment(context.entities)
        
        return {
            "updated_context": context,
            "curriculum": curriculum,
            "assessment": assessment,
            "next_steps": self._get_learning_next_steps(context.entities)
        }
    
    def _generate_learning_path(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured learning path"""
        
        skill_level = entities.get("skill_level", SkillLevel.BEGINNER)
        topics = entities.get("specific_topics", ["General Programming"])
        
        # Create learning modules
        modules = []
        
        if skill_level == SkillLevel.BEGINNER:
            modules.extend([
                {
                    "week": 1,
                    "title": "Foundations",
                    "topics": ["Basic concepts", "Environment setup", "First program"],
                    "estimated_hours": 10
                },
                {
                    "week": 2,
                    "title": "Core Concepts",
                    "topics": ["Variables and data types", "Control structures", "Functions"],
                    "estimated_hours": 12
                }
            ])
        
        # Add topic-specific modules
        for topic in topics[:2]:
            modules.append({
                "week": len(modules) + 1,
                "title": f"{topic} Essentials",
                "topics": [f"{topic} basics", f"{topic} best practices", f"Building with {topic}"],
                "estimated_hours": 15
            })
        
        # Calculate total duration
        total_weeks = len(modules)
        total_hours = sum(m["estimated_hours"] for m in modules)
        
        return {
            "duration": f"{total_weeks} weeks",
            "total_hours": total_hours,
            "modules": modules,
            "milestones": [
                {"week": 2, "achievement": "Complete basics"},
                {"week": 4, "achievement": "Build first project"},
                {"week": 6, "achievement": "Portfolio ready"}
            ]
        }
    
    def _get_initial_recommendations(self, entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get initial learning recommendations"""
        
        recommendations = []
        
        # Based on skill level
        if entities["skill_level"] == SkillLevel.BEGINNER:
            recommendations.append({
                "type": "foundation",
                "title": "Start with the Basics",
                "description": "Build a strong foundation before moving to advanced topics",
                "priority": "high"
            })
        
        # Based on goals
        if "career_advancement" in entities.get("learning_goals", []):
            recommendations.append({
                "type": "career",
                "title": "Focus on Practical Skills",
                "description": "Prioritize skills that are in high demand in the job market",
                "priority": "high"
            })
        
        # Learning style recommendations
        if entities.get("preferred_style") == LearningStyle.VISUAL:
            recommendations.append({
                "type": "resources",
                "title": "Video-First Approach",
                "description": "We'll prioritize video content and visual demonstrations",
                "priority": "medium"
            })
        
        # Time-based recommendations
        if entities.get("time_commitment") and "20" in str(entities["time_commitment"]):
            recommendations.append({
                "type": "pace",
                "title": "Accelerated Learning Path",
                "description": "With your time commitment, you can complete the program faster",
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_curriculum(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate detailed curriculum"""
        
        entities = context.entities or {}
        skill_level = entities.get("skill_level", SkillLevel.BEGINNER)
        topics = entities.get("specific_topics", ["Programming"])
        
        curriculum = {
            "title": f"{topics[0] if topics else 'Programming'} Learning Path",
            "level": skill_level.value,
            "duration": "12 weeks",
            "modules": []
        }
        
        # Week 1-4: Foundations
        curriculum["modules"].append({
            "phase": "Foundation",
            "weeks": "1-4",
            "courses": [
                {
                    "title": f"Introduction to {topics[0]}",
                    "type": ContentType.VIDEO,
                    "duration": "6 hours",
                    "topics": ["Basic syntax", "Development environment", "Core concepts"]
                },
                {
                    "title": "Hands-on Practice",
                    "type": ContentType.INTERACTIVE,
                    "duration": "8 hours",
                    "topics": ["Coding exercises", "Mini projects", "Debugging skills"]
                }
            ],
            "assessment": "Foundation Skills Test"
        })
        
        # Week 5-8: Intermediate
        curriculum["modules"].append({
            "phase": "Skill Building",
            "weeks": "5-8",
            "courses": [
                {
                    "title": "Intermediate Concepts",
                    "type": ContentType.VIDEO,
                    "duration": "10 hours",
                    "topics": ["Advanced features", "Best practices", "Design patterns"]
                },
                {
                    "title": "Real-World Project",
                    "type": ContentType.PROJECT,
                    "duration": "20 hours",
                    "topics": ["Project planning", "Implementation", "Testing"]
                }
            ],
            "assessment": "Project Review"
        })
        
        # Week 9-12: Advanced
        curriculum["modules"].append({
            "phase": "Mastery",
            "weeks": "9-12",
            "courses": [
                {
                    "title": "Advanced Topics",
                    "type": ContentType.VIDEO,
                    "duration": "12 hours",
                    "topics": ["Performance optimization", "Architecture", "Industry practices"]
                },
                {
                    "title": "Capstone Project",
                    "type": ContentType.PROJECT,
                    "duration": "30 hours",
                    "topics": ["Full application", "Documentation", "Deployment"]
                }
            ],
            "assessment": "Final Certification"
        })
        
        return curriculum
    
    def _create_adaptive_assessment(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Create adaptive assessment based on skill level"""
        
        skill_level = entities.get("skill_level", SkillLevel.BEGINNER)
        topics = entities.get("specific_topics", ["Programming"])
        
        questions = []
        
        # Beginner questions
        if skill_level == SkillLevel.BEGINNER:
            questions.extend([
                {
                    "type": "multiple_choice",
                    "question": f"What is a variable in {topics[0] if topics else 'programming'}?",
                    "options": [
                        "A container for storing data",
                        "A type of function",
                        "A programming language",
                        "An error message"
                    ],
                    "correct": 0,
                    "points": 1
                },
                {
                    "type": "true_false",
                    "question": "Functions help organize code into reusable blocks",
                    "correct": True,
                    "points": 1
                }
            ])
        
        # Intermediate questions
        elif skill_level == SkillLevel.INTERMEDIATE:
            questions.extend([
                {
                    "type": "coding",
                    "question": "Write a function that reverses a string",
                    "starter_code": "def reverse_string(s):\n    # Your code here\n    pass",
                    "test_cases": [
                        {"input": "hello", "output": "olleh"},
                        {"input": "Python", "output": "nohtyP"}
                    ],
                    "points": 5
                }
            ])
        
        return {
            "title": f"{skill_level.value.title()} Skills Assessment",
            "time_limit": "15 minutes",
            "questions": questions,
            "passing_score": 70,
            "adaptive": True
        }
    
    def _get_learning_next_steps(self, entities: Dict[str, Any]) -> List[str]:
        """Get next steps for learning journey"""
        
        steps = []
        
        # Immediate actions
        steps.append("Set up your development environment")
        steps.append("Join the online learning community")
        steps.append("Schedule your first study session")
        
        # Based on goals
        if "career_advancement" in entities.get("learning_goals", []):
            steps.append("Update LinkedIn with learning goals")
            steps.append("Research job requirements in your area")
        
        if entities.get("skill_level") == SkillLevel.BEGINNER:
            steps.append("Complete the 'Getting Started' tutorial")
        
        return steps[:5]


class AdaptiveLearningEngine:
    """Engine for adaptive learning experiences"""
    
    def __init__(self, ai_provider: EducationAIProvider):
        self.ai_provider = ai_provider
        self.student_progress = {}
    
    async def create_study_session(
        self,
        student_id: str,
        topic: str,
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """Create personalized study session"""
        
        # Get or create student profile
        if student_id not in self.student_progress:
            self.student_progress[student_id] = {
                "completed_topics": [],
                "skill_scores": {},
                "learning_pace": 1.0,
                "preferred_content": []
            }
        
        profile = self.student_progress[student_id]
        
        # Generate session content
        session = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "topic": topic,
            "duration": duration_minutes,
            "content": await self._generate_session_content(topic, profile, duration_minutes),
            "objectives": self._get_session_objectives(topic, profile),
            "assessment": self._create_session_quiz(topic, profile)
        }
        
        return session
    
    async def _generate_session_content(
        self,
        topic: str,
        profile: Dict[str, Any],
        duration: int
    ) -> List[Dict[str, Any]]:
        """Generate adaptive session content"""
        
        content = []
        remaining_time = duration
        
        # Warm-up (5 minutes)
        if remaining_time >= 5:
            content.append({
                "type": "review",
                "title": "Quick Review",
                "duration": 5,
                "content": "Review of previous concepts",
                "interactive": True
            })
            remaining_time -= 5
        
        # Main content (70% of time)
        main_duration = int(remaining_time * 0.7)
        content.append({
            "type": "lesson",
            "title": f"Today's Topic: {topic}",
            "duration": main_duration,
            "content": "Core learning material",
            "format": "video" if duration > 20 else "text",
            "difficulty": self._adjust_difficulty(profile)
        })
        remaining_time -= main_duration
        
        # Practice (remaining time)
        if remaining_time > 0:
            content.append({
                "type": "practice",
                "title": "Hands-on Practice",
                "duration": remaining_time,
                "exercises": self._generate_exercises(topic, profile),
                "hints_available": True
            })
        
        return content
    
    def _get_session_objectives(self, topic: str, profile: Dict[str, Any]) -> List[str]:
        """Get learning objectives for session"""
        
        base_objectives = [
            f"Understand the fundamentals of {topic}",
            f"Apply {topic} concepts in practice",
            f"Identify common patterns in {topic}"
        ]
        
        # Add personalized objectives
        if not profile["completed_topics"]:
            base_objectives.insert(0, "Build confidence with hands-on practice")
        
        return base_objectives[:3]
    
    def _create_session_quiz(self, topic: str, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create adaptive quiz questions"""
        
        difficulty = self._adjust_difficulty(profile)
        
        questions = [
            {
                "type": "concept_check",
                "question": f"What is the main purpose of {topic}?",
                "difficulty": difficulty,
                "points": 2
            },
            {
                "type": "application",
                "question": f"How would you use {topic} in a real project?",
                "difficulty": difficulty,
                "points": 3
            }
        ]
        
        return questions
    
    def _adjust_difficulty(self, profile: Dict[str, Any]) -> str:
        """Adjust difficulty based on student progress"""
        
        avg_score = sum(profile["skill_scores"].values()) / len(profile["skill_scores"]) if profile["skill_scores"] else 0
        
        if avg_score >= 80:
            return "challenging"
        elif avg_score >= 60:
            return "intermediate"
        else:
            return "beginner"
    
    def _generate_exercises(self, topic: str, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate practice exercises"""
        
        exercises = [
            {
                "title": f"Basic {topic} Exercise",
                "difficulty": "easy",
                "estimated_time": "5 minutes",
                "hints": ["Think about the definition", "Review the examples"]
            },
            {
                "title": f"Apply {topic} Concepts",
                "difficulty": "medium",
                "estimated_time": "10 minutes",
                "hints": ["Break down the problem", "Use what you learned"]
            }
        ]
        
        return exercises


async def demonstrate_education_tutor():
    """Demonstrate the AI-powered education tutor"""
    
    print("🎓 AI-Powered Education Tutor Demo")
    print("="*60)
    
    # Example learning conversations
    conversations = [
        {
            "learner": "career_changer",
            "messages": [
                "I want to learn Python programming to switch careers",
                "I have no coding experience but I'm good with Excel",
                "Can dedicate 10 hours per week, want to be job-ready in 6 months"
            ]
        },
        {
            "learner": "student",
            "messages": [
                "Need help with calculus, struggling with derivatives",
                "I have an exam in 2 weeks",
                "I learn better with visual explanations and practice problems"
            ]
        },
        {
            "learner": "hobbyist",
            "messages": [
                "Want to learn web development for fun",
                "I know some HTML but want to make interactive websites",
                "Maybe 5 hours a week, no rush"
            ]
        }
    ]
    
    ai_provider = EducationAIProvider()
    learning_engine = AdaptiveLearningEngine(ai_provider)
    
    for conv in conversations:
        print(f"\n📚 Learning Path for: {conv['learner']}")
        print("-" * 40)
        
        # Create context
        context = ConversationContext(messages=[
            {"role": "user", "content": msg} for msg in conv["messages"]
        ])
        
        # Analyze learning needs
        analysis = await ai_provider.analyze_conversation(context)
        
        print("\n📊 Learning Analysis:")
        print(f"   Subjects: {', '.join([s.value for s in analysis['entities']['subjects']])}")
        print(f"   Topics: {', '.join(analysis['entities']['specific_topics'])}")
        print(f"   Skill level: {analysis['entities']['skill_level'].value}")
        print(f"   Time commitment: {analysis['entities'].get('time_commitment', 'Not specified')}")
        
        print("\n🎯 Learning Path:")
        path = analysis["learning_path"]
        print(f"   Duration: {path['duration']}")
        print(f"   Total hours: {path['total_hours']}")
        print("   Modules:")
        for module in path["modules"][:3]:
            print(f"   - Week {module['week']}: {module['title']}")
        
        print("\n💡 Recommendations:")
        for rec in analysis["recommendations"][:2]:
            print(f"   [{rec['priority'].upper()}] {rec['title']}")
            print(f"   → {rec['description']}")
        
        # Generate personalized form
        schema = await ai_provider.generate_form_schema(context)
        print(f"\n📝 Generated assessment with {len(schema['fields'])} fields")
        
        # Create study session
        if analysis['entities']['specific_topics']:
            topic = analysis['entities']['specific_topics'][0]
            session = await learning_engine.create_study_session(
                conv['learner'],
                topic,
                30
            )
            
            print(f"\n📖 Study Session Created: {topic}")
            print("   Content:")
            for content in session["content"]:
                print(f"   - {content['title']} ({content['duration']} min)")
    
    print("\n" + "="*60)
    print("🌟 Education Tutor Features:")
    print("- Personalized learning paths")
    print("- Adaptive content difficulty")
    print("- Multi-modal learning resources")
    print("- Progress tracking and analytics")
    print("- Skill assessments and quizzes")
    print("- Study session generation")


if __name__ == "__main__":
    asyncio.run(demonstrate_education_tutor())