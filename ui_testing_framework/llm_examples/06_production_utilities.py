#!/usr/bin/env python3
"""
Production-Ready QA Utilities
=============================

This module provides production-ready utilities for QA teams:
- Test case management and organization
- Automated test reporting
- Test data management and cleanup
- QA metrics and analytics
- Integration with common QA tools

Run directly: python 06_production_utilities.py
"""

import sys
from pathlib import Path
import json
import csv
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm, StrategyType


class TestPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestStatus(Enum):
    DRAFT = "draft"
    READY = "ready"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


@dataclass
class TestCase:
    """Data class representing a test case."""
    id: str
    title: str
    description: str
    steps: List[str]
    expected_result: str
    priority: TestPriority
    status: TestStatus
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    feature: str
    estimated_duration: int  # minutes


class TestCaseManager:
    """Manages test cases with database storage and LLM generation."""
    
    def __init__(self, db_path: str = "test_cases.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for test case storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_cases (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                steps TEXT,  -- JSON array
                expected_result TEXT,
                priority TEXT,
                status TEXT,
                tags TEXT,  -- JSON array
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT,
                feature TEXT,
                estimated_duration INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_test_cases(self, feature_description: str, num_cases: int = 5) -> List[TestCase]:
        """Generate test cases using LLM for a given feature."""
        print(f"🔄 Generating {num_cases} test cases for: {feature_description[:50]}...")
        
        messages = [{
            "role": "user",
            "content": f"""
            Generate {num_cases} comprehensive test cases for this feature:
            
            Feature: {feature_description}
            
            For each test case, provide:
            1. Clear, descriptive title
            2. Brief description of what's being tested
            3. Step-by-step instructions
            4. Expected result
            5. Priority level (critical/high/medium/low)
            6. Relevant tags for categorization
            7. Estimated duration in minutes
            
            Format as JSON array with this structure:
            [
                {{
                    "title": "Test case title",
                    "description": "What this test verifies",
                    "steps": ["Step 1", "Step 2", "Step 3"],
                    "expected_result": "What should happen",
                    "priority": "high",
                    "tags": ["login", "validation"],
                    "estimated_duration": 15
                }}
            ]
            """
        }]
        
        response = query_llm(messages, strategy=StrategyType.SELF_REFINE)
        
        try:
            # Extract JSON from response
            json_start = response.content.find('[')
            json_end = response.content.rfind(']') + 1
            json_data = response.content[json_start:json_end]
            
            test_data = json.loads(json_data)
            test_cases = []
            
            for data in test_data:
                test_id = self._generate_test_id(data['title'])
                test_case = TestCase(
                    id=test_id,
                    title=data['title'],
                    description=data['description'],
                    steps=data['steps'],
                    expected_result=data['expected_result'],
                    priority=TestPriority(data['priority']),
                    status=TestStatus.DRAFT,
                    tags=data['tags'],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    created_by="LLM Generator",
                    feature=feature_description[:100],
                    estimated_duration=data.get('estimated_duration', 10)
                )
                test_cases.append(test_case)
            
            print(f"✅ Generated {len(test_cases)} test cases")
            return test_cases
            
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
            return []
    
    def _generate_test_id(self, title: str) -> str:
        """Generate unique test case ID based on title."""
        hash_input = f"{title}{datetime.now().isoformat()}"
        hash_obj = hashlib.md5(hash_input.encode())
        return f"TC_{hash_obj.hexdigest()[:8].upper()}"
    
    def save_test_case(self, test_case: TestCase):
        """Save test case to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO test_cases VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_case.id,
            test_case.title,
            test_case.description,
            json.dumps(test_case.steps),
            test_case.expected_result,
            test_case.priority.value,
            test_case.status.value,
            json.dumps(test_case.tags),
            test_case.created_at.isoformat(),
            test_case.updated_at.isoformat(),
            test_case.created_by,
            test_case.feature,
            test_case.estimated_duration
        ))
        
        conn.commit()
        conn.close()
    
    def get_test_cases_by_feature(self, feature: str) -> List[TestCase]:
        """Retrieve test cases for a specific feature."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_cases WHERE feature LIKE ?", (f"%{feature}%",))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_test_case(row) for row in rows]
    
    def _row_to_test_case(self, row) -> TestCase:
        """Convert database row to TestCase object."""
        return TestCase(
            id=row[0],
            title=row[1],
            description=row[2],
            steps=json.loads(row[3]),
            expected_result=row[4],
            priority=TestPriority(row[5]),
            status=TestStatus(row[6]),
            tags=json.loads(row[7]),
            created_at=datetime.fromisoformat(row[8]),
            updated_at=datetime.fromisoformat(row[9]),
            created_by=row[10],
            feature=row[11],
            estimated_duration=row[12]
        )
    
    def export_to_csv(self, filename: str, feature_filter: str = None):
        """Export test cases to CSV format."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM test_cases"
        params = []
        
        if feature_filter:
            query += " WHERE feature LIKE ?"
            params.append(f"%{feature_filter}%")
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Test ID', 'Title', 'Description', 'Steps', 'Expected Result',
                'Priority', 'Status', 'Tags', 'Created At', 'Updated At',
                'Created By', 'Feature', 'Estimated Duration (min)'
            ])
            
            # Data rows
            for row in rows:
                writer.writerow(row)
        
        print(f"📄 Exported {len(rows)} test cases to {filename}")


class TestMetricsAnalyzer:
    """Analyzes test execution metrics and generates insights."""
    
    def __init__(self):
        self.metrics = []
    
    def analyze_test_coverage(self, feature_list: List[str], test_manager: TestCaseManager):
        """Analyze test coverage across features."""
        print("📊 ANALYZING TEST COVERAGE")
        print("=" * 30)
        
        coverage_data = {}
        
        for feature in feature_list:
            test_cases = test_manager.get_test_cases_by_feature(feature)
            
            coverage_data[feature] = {
                "total_tests": len(test_cases),
                "by_priority": {
                    "critical": len([tc for tc in test_cases if tc.priority == TestPriority.CRITICAL]),
                    "high": len([tc for tc in test_cases if tc.priority == TestPriority.HIGH]),
                    "medium": len([tc for tc in test_cases if tc.priority == TestPriority.MEDIUM]),
                    "low": len([tc for tc in test_cases if tc.priority == TestPriority.LOW])
                },
                "by_status": {
                    "ready": len([tc for tc in test_cases if tc.status == TestStatus.READY]),
                    "draft": len([tc for tc in test_cases if tc.status == TestStatus.DRAFT]),
                    "in_review": len([tc for tc in test_cases if tc.status == TestStatus.IN_REVIEW])
                },
                "estimated_hours": sum(tc.estimated_duration for tc in test_cases) / 60
            }
        
        # Generate insights using LLM
        coverage_summary = json.dumps(coverage_data, indent=2)
        
        messages = [{
            "role": "user",
            "content": f"""
            Analyze this test coverage data and provide insights:
            
            {coverage_summary}
            
            Provide:
            1. Coverage gaps and recommendations
            2. Testing effort distribution analysis
            3. Priority balancing suggestions
            4. Risk assessment
            5. Actionable improvement suggestions
            
            Focus on practical QA management insights.
            """
        }]
        
        response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT)
        
        print("Coverage Analysis Results:")
        print(response.content)
        print("\n" + "=" * 30 + "\n")
        
        return coverage_data, response.content
    
    def generate_qa_report(self, test_manager: TestCaseManager, days: int = 30):
        """Generate comprehensive QA report for the last N days."""
        print(f"📈 GENERATING QA REPORT - LAST {days} DAYS")
        print("=" * 45)
        
        # Get recent test case data
        conn = sqlite3.connect(test_manager.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute("""
            SELECT feature, COUNT(*), AVG(estimated_duration), priority, status
            FROM test_cases 
            WHERE created_at >= ? 
            GROUP BY feature, priority, status
        """, (cutoff_date,))
        
        data = cursor.fetchall()
        conn.close()
        
        # Create report using LLM
        data_summary = "\n".join([f"Feature: {row[0]}, Tests: {row[1]}, Avg Duration: {row[2]:.1f}min, Priority: {row[3]}, Status: {row[4]}" for row in data])
        
        messages = [{
            "role": "user",
            "content": f"""
            Generate a professional QA report based on this test case data from the last {days} days:
            
            {data_summary}
            
            Include:
            1. Executive Summary
            2. Testing Productivity Metrics
            3. Feature Coverage Analysis
            4. Quality Trends
            5. Resource Utilization
            6. Recommendations for next sprint
            
            Format as a professional report suitable for management review.
            """
        }]
        
        response = query_llm(messages, strategy=StrategyType.SELF_REFINE)
        
        # Save report to file
        report_file = Path(__file__).parent / f"qa_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# QA Report - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(response.content)
        
        print(f"📄 QA report saved to: {report_file}")
        print("\n" + "=" * 45 + "\n")
        
        return response.content


class TestDataManager:
    """Manages test data generation and cleanup."""
    
    def __init__(self):
        self.test_data_cache = {}
    
    def generate_test_data_set(self, data_type: str, count: int, requirements: str):
        """Generate specific type of test data."""
        print(f"🔢 Generating {count} {data_type} test data entries")
        
        messages = [{
            "role": "user",
            "content": f"""
            Generate {count} realistic {data_type} test data entries.
            
            Requirements: {requirements}
            
            Return as JSON array with consistent structure.
            Include both valid and invalid examples where appropriate.
            Make data realistic and varied for thorough testing.
            """
        }]
        
        response = query_llm(messages, strategy=StrategyType.SELF_CONSISTENCY)
        
        try:
            # Extract JSON from response
            json_start = response.content.find('[')
            json_end = response.content.rfind(']') + 1
            json_data = response.content[json_start:json_end]
            
            test_data = json.loads(json_data)
            
            # Cache the data
            cache_key = f"{data_type}_{count}_{hash(requirements)}"
            self.test_data_cache[cache_key] = {
                "data": test_data,
                "generated_at": datetime.now(),
                "data_type": data_type,
                "count": len(test_data)
            }
            
            print(f"✅ Generated {len(test_data)} {data_type} entries")
            return test_data
            
        except Exception as e:
            print(f"❌ Error generating test data: {e}")
            return []
    
    def save_test_data(self, data: List[Dict], filename: str):
        """Save test data to JSON file."""
        file_path = Path(__file__).parent / "test_data" / filename
        file_path.parent.mkdir(exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "count": len(data),
                "data": data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Test data saved to: {file_path}")
    
    def cleanup_expired_data(self, days: int = 7):
        """Clean up test data older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        removed_count = 0
        for key in list(self.test_data_cache.keys()):
            if self.test_data_cache[key]["generated_at"] < cutoff_date:
                del self.test_data_cache[key]
                removed_count += 1
        
        print(f"🧹 Cleaned up {removed_count} expired test data entries")


class QAUtilityRunner:
    """Main runner for all QA utility examples."""
    
    def __init__(self):
        self.test_manager = TestCaseManager()
        self.metrics_analyzer = TestMetricsAnalyzer()
        self.data_manager = TestDataManager()
    
    def demo_test_case_generation(self):
        """Demonstrate test case generation and management."""
        print("🧪 TEST CASE GENERATION DEMO")
        print("=" * 30)
        
        # Generate test cases for different features
        features = [
            "User authentication with multi-factor authentication support",
            "E-commerce product search with advanced filtering options",
            "Real-time chat system with file sharing capabilities"
        ]
        
        for feature in features:
            test_cases = self.test_manager.generate_test_cases(feature, 3)
            
            for test_case in test_cases:
                self.test_manager.save_test_case(test_case)
                print(f"  ✅ Saved: {test_case.title}")
        
        # Export to CSV
        self.test_manager.export_to_csv("generated_test_cases.csv")
        print("\n" + "=" * 30 + "\n")
    
    def demo_metrics_analysis(self):
        """Demonstrate metrics analysis capabilities."""
        features = ["authentication", "search", "chat"]
        coverage_data, insights = self.metrics_analyzer.analyze_test_coverage(
            features, self.test_manager
        )
        
        # Generate QA report
        report = self.metrics_analyzer.generate_qa_report(self.test_manager)
    
    def demo_test_data_generation(self):
        """Demonstrate test data generation."""
        print("🔢 TEST DATA GENERATION DEMO")
        print("=" * 30)
        
        # Generate different types of test data
        data_sets = [
            {
                "type": "user_profiles",
                "count": 10,
                "requirements": "Realistic user profiles with name, email, age, location for registration testing"
            },
            {
                "type": "product_data",
                "count": 15,
                "requirements": "E-commerce products with name, price, category, description, stock quantity"
            },
            {
                "type": "transaction_data",
                "count": 20,
                "requirements": "Financial transactions with amount, currency, timestamp, payment method"
            }
        ]
        
        for data_set in data_sets:
            test_data = self.data_manager.generate_test_data_set(
                data_set["type"],
                data_set["count"], 
                data_set["requirements"]
            )
            
            if test_data:
                self.data_manager.save_test_data(test_data, f"{data_set['type']}.json")
        
        print("\n" + "=" * 30 + "\n")
    
    def run_all_demos(self):
        """Run all utility demonstrations."""
        print("🔧 PRODUCTION QA UTILITIES DEMO")
        print("===============================")
        print("Demonstrating production-ready QA utilities...")
        print()
        
        try:
            self.demo_test_case_generation()
            self.demo_metrics_analysis()
            self.demo_test_data_generation()
            
            print("✅ SUCCESS: All QA utility demos completed!")
            print("📊 Generated test cases, metrics analysis, and test data")
            print("💼 All utilities are production-ready for QA teams")
            print()
            print("Generated Files:")
            print("  📄 generated_test_cases.csv - Exportable test cases")
            print("  📈 qa_report_YYYYMMDD.md - Management report")
            print("  🔢 test_data/ - Generated test data sets")
            print("  🗄️ test_cases.db - SQLite database with test cases")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Run production utilities demo."""
    runner = QAUtilityRunner()
    runner.run_all_demos()


if __name__ == "__main__":
    main()