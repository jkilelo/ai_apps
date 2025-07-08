"""
Python code generator for web automation
"""
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_python_code(test_description: str, gherkin_tests: List[Dict[str, Any]]) -> str:
    """
    Generate Python Playwright code from Gherkin tests
    """
    # Format Gherkin tests for the prompt
    gherkin_formatted = []
    for test in gherkin_tests:
        scenario = f"Feature: {test.get('feature', 'Test')}\n"
        scenario += f"  Scenario: {test.get('scenario', 'Test scenario')}\n"
        for given in test.get('given', []):
            scenario += f"    Given {given}\n"
        for when in test.get('when', []):
            scenario += f"    When {when}\n"
        for then in test.get('then', []):
            scenario += f"    Then {then}\n"
        gherkin_formatted.append(scenario)
    
    gherkin_text = "\n\n".join(gherkin_formatted)
    
    prompt = f"""Generate Python Playwright code for the following Gherkin test scenarios:

{gherkin_text}

Additional context: {test_description}

Generate complete, runnable Python code using Playwright that:
1. Uses async/await pattern
2. Includes proper error handling
3. Takes screenshots at key points
4. Includes assertions for the "Then" steps
5. Uses page.wait_for_load_state() appropriately
6. Returns a summary of test results

The code should be production-ready and follow best practices."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Python Playwright automation expert. Generate clean, efficient, and well-documented test automation code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000
    )
    
    code = response.choices[0].message.content
    
    # Extract code block if wrapped in markdown
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    
    return code.strip()