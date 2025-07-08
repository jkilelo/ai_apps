"""
Gherkin test generator for web automation
"""
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI
import json

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_gherkin_tests(scenario_description: str, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate Gherkin tests based on scenario and extracted elements
    """
    # Create a prompt with elements context
    elements_summary = "\n".join([
        f"- {elem['type']}: {elem.get('text', '')} (selector: {elem.get('selector', '')})"
        for elem in elements[:20]  # Limit to first 20 elements
    ])
    
    prompt = f"""Generate Gherkin test scenarios for the following web automation task:
    
Task Description: {scenario_description}

Available elements on the page:
{elements_summary}

Please generate 3-5 comprehensive Gherkin scenarios in JSON format.
Each scenario should have:
- feature: string
- scenario: string
- given: list of strings
- when: list of strings
- then: list of strings

Return only valid JSON array."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a test automation expert who writes clear, concise Gherkin scenarios."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    try:
        # Parse the response as JSON
        content = response.choices[0].message.content
        # Extract JSON from the response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        gherkin_tests = json.loads(content.strip())
        return gherkin_tests
    except:
        # Fallback to default structure
        return [{
            "feature": "Web Automation Test",
            "scenario": scenario_description,
            "given": ["I am on the webpage"],
            "when": ["I interact with the page elements"],
            "then": ["I should see the expected results"]
        }]