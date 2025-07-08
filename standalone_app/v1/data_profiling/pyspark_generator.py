"""
Generate PySpark code for data profiling and DQ testing
"""
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_pyspark_code(test_cases: List[Dict[str, Any]]) -> str:
    """
    Generate PySpark code for profiling test cases
    """
    test_cases_text = []
    for tc in test_cases:
        text = f"Test: {tc['test_name']}"
        text += f"\n  Type: {tc['test_type']}"
        text += f"\n  Logic: {tc['test_logic']}"
        text += f"\n  Columns: {', '.join(tc['columns'])}"
        test_cases_text.append(text)
    
    prompt = f"""Generate PySpark code for the following data profiling test cases:

{chr(10).join(test_cases_text)}

Generate complete PySpark code that:
1. Creates a SparkSession
2. Loads data (assume it's available as 'df' DataFrame)
3. Implements each test case
4. Collects results in a structured format
5. Prints results in a readable format
6. Includes error handling

The code should be production-ready and follow PySpark best practices.
Return only the Python code, no explanations."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a PySpark expert who writes efficient data profiling code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000
    )
    
    code = response.choices[0].message.content
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    
    return code.strip()


async def generate_pyspark_dq_code(dq_tests: List[Dict[str, Any]]) -> str:
    """
    Generate PySpark code for data quality tests
    """
    tests_text = []
    for test in dq_tests:
        text = f"Test: {test.get('test_name', 'DQ Test')}"
        text += f"\n  Rule: {test.get('rule', '')}"
        text += f"\n  Columns: {test.get('columns', [])}"
        text += f"\n  Threshold: {test.get('threshold', 'N/A')}"
        tests_text.append(text)
    
    prompt = f"""Generate PySpark code for the following data quality tests:

{chr(10).join(tests_text)}

Generate PySpark code that:
1. Implements each DQ test as a separate function
2. Returns pass/fail status with details
3. Calculates quality scores
4. Handles edge cases
5. Provides actionable insights

The code should follow data quality best practices.
Return only the Python code."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data quality expert who writes comprehensive DQ testing code in PySpark."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000
    )
    
    code = response.choices[0].message.content
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    
    return code.strip()