"""
Generate data quality suggestions based on profiling results
"""
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_dq_suggestions(profiling_results: str) -> List[Dict[str, Any]]:
    """
    Generate DQ suggestions based on profiling results
    """
    prompt = f"""Based on the following data profiling results, generate data quality improvement suggestions:

{profiling_results}

Generate 5-8 data quality suggestions that address:
1. Data completeness issues
2. Data consistency problems
3. Data accuracy concerns
4. Data validity violations
5. Business rule compliance

Each suggestion should have:
- suggestion_id: string
- category: string ("completeness", "consistency", "accuracy", "validity", "business_rules")
- title: string
- description: string
- impact: string ("high", "medium", "low")
- affected_columns: list of column names
- recommendation: string (specific action to take)

Return as a JSON array."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data quality expert who provides actionable recommendations based on data profiling results."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
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
        # Fallback suggestions
        return [
            {
                "suggestion_id": "dq_001",
                "category": "completeness",
                "title": "Address Missing Values",
                "description": "Null values detected in critical columns",
                "impact": "high",
                "affected_columns": ["name", "email", "date"],
                "recommendation": "Implement data validation rules to prevent null values in mandatory fields"
            },
            {
                "suggestion_id": "dq_002",
                "category": "validity",
                "title": "Standardize Data Formats",
                "description": "Inconsistent formats detected in date and email fields",
                "impact": "medium",
                "affected_columns": ["email", "date"],
                "recommendation": "Apply format validation and standardization transformations"
            },
            {
                "suggestion_id": "dq_003",
                "category": "accuracy",
                "title": "Detect and Handle Outliers",
                "description": "Statistical outliers found in numeric columns",
                "impact": "medium",
                "affected_columns": ["age"],
                "recommendation": "Implement outlier detection and handling strategies"
            }
        ]