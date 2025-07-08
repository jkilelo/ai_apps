"""
Generate data quality tests from DQ suggestions
"""
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_dq_tests(suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate specific DQ tests from suggestions
    """
    suggestions_text = []
    for suggestion in suggestions:
        text = f"- {suggestion['title']} ({suggestion['category']})"
        text += f"\n  Impact: {suggestion['impact']}"
        text += f"\n  Columns: {', '.join(suggestion['affected_columns'])}"
        text += f"\n  Recommendation: {suggestion['recommendation']}"
        suggestions_text.append(text)
    
    prompt = f"""Convert the following data quality suggestions into specific, executable tests:

{chr(10).join(suggestions_text)}

Generate DQ tests that can be implemented in PySpark. Each test should have:
- test_id: string
- test_name: string
- test_category: string (matching suggestion category)
- rule: string (specific DQ rule to check)
- columns: list of column names
- threshold: number (acceptance threshold, e.g., 0.95 for 95%)
- severity: string ("critical", "major", "minor")
- expected_action: string (what to do if test fails)

Return as a JSON array. Generate 1-2 tests per suggestion."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data quality testing expert who creates precise, measurable DQ tests."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=2000
    )
    
    try:
        import json
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        return json.loads(content.strip())
    except:
        # Fallback tests
        dq_tests = []
        for idx, suggestion in enumerate(suggestions):
            if suggestion['category'] == 'completeness':
                dq_tests.append({
                    "test_id": f"dq_test_{idx}_1",
                    "test_name": f"Null Check - {suggestion['title']}",
                    "test_category": "completeness",
                    "rule": "Column should have less than 5% null values",
                    "columns": suggestion['affected_columns'],
                    "threshold": 0.95,
                    "severity": "critical" if suggestion['impact'] == 'high' else "major",
                    "expected_action": "Flag records with null values for review"
                })
            elif suggestion['category'] == 'validity':
                dq_tests.append({
                    "test_id": f"dq_test_{idx}_1",
                    "test_name": f"Format Validation - {suggestion['title']}",
                    "test_category": "validity",
                    "rule": "Values should match expected format pattern",
                    "columns": suggestion['affected_columns'],
                    "threshold": 0.98,
                    "severity": "major",
                    "expected_action": "Transform non-conforming values to standard format"
                })
            elif suggestion['category'] == 'accuracy':
                dq_tests.append({
                    "test_id": f"dq_test_{idx}_1",
                    "test_name": f"Range Check - {suggestion['title']}",
                    "test_category": "accuracy",
                    "rule": "Values should be within expected range",
                    "columns": suggestion['affected_columns'],
                    "threshold": 0.99,
                    "severity": "minor",
                    "expected_action": "Flag outliers for manual review"
                })
        
        return dq_tests