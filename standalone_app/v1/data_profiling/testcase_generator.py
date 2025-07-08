"""
Generate test cases for data profiling
"""
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_profiling_testcases(suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate specific test cases from profiling suggestions
    """
    suggestions_text = []
    for idx, suggestion in enumerate(suggestions):
        text = f"{idx + 1}. {suggestion['description']}"
        text += f"\n   Type: {suggestion['suggestion_type']}"
        text += f"\n   Columns: {', '.join(suggestion['columns_involved'])}"
        text += f"\n   Priority: {suggestion['priority']}"
        suggestions_text.append(text)
    
    prompt = f"""Convert the following data profiling suggestions into specific test cases:

{chr(10).join(suggestions_text)}

Generate detailed test cases that can be implemented in PySpark. Each test case should have:
- test_id: string (unique identifier)
- test_name: string
- test_type: string (matching the suggestion_type)
- description: string
- columns: list of column names
- test_logic: string (description of what to test)
- expected_output: string (what kind of results to expect)
- severity: string ("critical", "major", "minor")

Return as a JSON array. Generate 2-3 test cases per suggestion."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data quality testing expert who creates comprehensive test cases for data profiling."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=3000
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
        # Generate fallback test cases
        test_cases = []
        for idx, suggestion in enumerate(suggestions):
            test_cases.extend([
                {
                    "test_id": f"test_{idx}_1",
                    "test_name": f"Null Check for {suggestion['description']}",
                    "test_type": suggestion['suggestion_type'],
                    "description": f"Check for null values in columns: {', '.join(suggestion['columns_involved'])}",
                    "columns": suggestion['columns_involved'],
                    "test_logic": "Count null values and calculate null percentage",
                    "expected_output": "Null count and percentage for each column",
                    "severity": "major"
                },
                {
                    "test_id": f"test_{idx}_2",
                    "test_name": f"Distribution Analysis for {suggestion['description']}",
                    "test_type": suggestion['suggestion_type'],
                    "description": f"Analyze value distribution in columns: {', '.join(suggestion['columns_involved'][:3])}",
                    "columns": suggestion['columns_involved'][:3],
                    "test_logic": "Calculate value frequencies and identify top values",
                    "expected_output": "Frequency distribution of values",
                    "severity": "minor"
                }
            ])
        return test_cases