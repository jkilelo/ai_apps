"""
Python code executor for web automation
"""
import asyncio
import tempfile
import os
import sys
import subprocess
import traceback
from typing import Optional


async def execute_python_code(code: str) -> str:
    """
    Execute Python code safely and return the results
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Add necessary imports and wrapper
        wrapped_code = f"""
import asyncio
import sys
from playwright.async_api import async_playwright
import traceback

async def main():
    try:
{chr(10).join('        ' + line for line in code.split(chr(10)))}
    except Exception as e:
        print(f"Error during execution: {{str(e)}}")
        traceback.print_exc()
        return {{"status": "error", "message": str(e)}}

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"Execution result: {{result}}")
"""
        f.write(wrapped_code)
        temp_path = f.name
    
    try:
        # Execute the code
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        output = []
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Errors:\n{result.stderr}")
        
        if result.returncode == 0:
            return "\n".join(output) if output else "Code executed successfully with no output."
        else:
            return f"Execution failed with return code {result.returncode}\n" + "\n".join(output)
            
    except subprocess.TimeoutExpired:
        return "Execution timed out after 60 seconds"
    except Exception as e:
        return f"Execution error: {str(e)}\n{traceback.format_exc()}"
    finally:
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass