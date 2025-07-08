"""
Generate profiling suggestions for data quality analysis
"""
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_profiling_suggestions(
    database_name: str,
    table_name: str,
    columns: List[str]
) -> List[Dict[str, Any]]:
    """
    Generate data profiling suggestions based on database schema
    """
    columns_text = "\n".join([f"- {col}" for col in columns])
    
    prompt = f"""Generate data profiling suggestions for the following table:

Database: {database_name}
Table: {table_name}
Columns:
{columns_text}

Generate 5-10 comprehensive data profiling suggestions that would help understand:
1. Data quality issues
2. Statistical distributions
3. Patterns and anomalies
4. Data relationships
5. Business rule violations

Return as a JSON array where each suggestion has:
- suggestion_type: string (e.g., "statistical_analysis", "pattern_detection", "anomaly_detection", "relationship_analysis")
- description: string
- columns_involved: list of column names
- priority: string ("high", "medium", "low")
- expected_insights: list of strings

Return only valid JSON."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data quality expert who understands data profiling and analysis."},
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
                "suggestion_type": "statistical_analysis",
                "description": f"Compute basic statistics for all numeric columns in {table_name}",
                "columns_involved": columns,
                "priority": "high",
                "expected_insights": ["min/max values", "mean/median", "standard deviation", "null counts"]
            },
            {
                "suggestion_type": "pattern_detection",
                "description": f"Detect patterns in string columns of {table_name}",
                "columns_involved": [col for col in columns if any(keyword in col.lower() for keyword in ['name', 'id', 'code', 'email', 'phone'])],
                "priority": "medium",
                "expected_insights": ["common patterns", "format violations", "standardization opportunities"]
            },
            {
                "suggestion_type": "anomaly_detection",
                "description": f"Identify outliers and anomalies in {table_name}",
                "columns_involved": columns,
                "priority": "high",
                "expected_insights": ["outlier records", "unusual values", "data quality issues"]
            }
        ]