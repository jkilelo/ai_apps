"""
Execute PySpark code for data profiling
"""
import subprocess
import tempfile
import os
import sys
import asyncio


async def execute_pyspark_code(code: str) -> str:
    """
    Execute PySpark code and return results
    """
    # Check if PySpark container is available
    pyspark_container_check = subprocess.run(
        ["docker", "ps", "-q", "-f", "name=pyspark-notebook"],
        capture_output=True,
        text=True
    )
    
    if not pyspark_container_check.stdout.strip():
        return "Error: PySpark container is not running. Please start the PySpark container first."
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Add necessary imports and wrapper
        wrapped_code = f"""
from pyspark.sql import SparkSession
import json
import traceback

def main():
    spark = None
    try:
        # Initialize Spark
        spark = SparkSession.builder \\
            .appName("DataProfilingV1") \\
            .config("spark.sql.adaptive.enabled", "true") \\
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \\
            .getOrCreate()
        
        # Set log level
        spark.sparkContext.setLogLevel("WARN")
        
        # Create sample data if no real data is available
        data = [
            (1, "John Doe", 25, "john@email.com", "2024-01-01"),
            (2, "Jane Smith", 30, "jane@email.com", "2024-01-02"),
            (3, "Bob Johnson", 35, "bob@email.com", "2024-01-03"),
            (4, "Alice Brown", 28, "alice@email.com", "2024-01-04"),
            (5, "Charlie Wilson", 32, "charlie@email.com", "2024-01-05"),
            (6, None, 29, "test@email.com", "2024-01-06"),
            (7, "David Lee", None, "david@email.com", None),
            (8, "Eve Martinez", 31, None, "2024-01-08"),
            (9, "Frank Garcia", 27, "frank@email.com", "2024-01-09"),
            (10, "Grace Taylor", 33, "grace@email.com", "2024-01-10")
        ]
        
        columns = ["id", "name", "age", "email", "date"]
        df = spark.createDataFrame(data, columns)
        
        print("Sample data created successfully")
        print(f"Schema: {{df.schema}}")
        print(f"Row count: {{df.count()}}")
        
        # Execute user code
{chr(10).join('        ' + line for line in code.split(chr(10)))}
        
    except Exception as e:
        print(f"Error during execution: {{str(e)}}")
        traceback.print_exc()
    finally:
        if spark:
            spark.stop()

if __name__ == "__main__":
    main()
"""
        f.write(wrapped_code)
        temp_path = f.name
    
    try:
        # Execute in PySpark container
        result = subprocess.run(
            [
                "docker", "exec", "pyspark-notebook",
                "python", f"/tmp/{os.path.basename(temp_path)}"
            ],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        # First copy the file to container
        subprocess.run(
            ["docker", "cp", temp_path, f"pyspark-notebook:/tmp/{os.path.basename(temp_path)}"],
            check=True
        )
        
        # Then execute
        result = subprocess.run(
            [
                "docker", "exec", "pyspark-notebook",
                "python", f"/tmp/{os.path.basename(temp_path)}"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = []
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            # Filter out Spark warnings
            errors = [line for line in result.stderr.split('\n') 
                     if line and not any(ignore in line for ignore in ['WARN', 'INFO', 'Using Spark'])]
            if errors:
                output.append(f"Errors:\n{chr(10).join(errors)}")
        
        if result.returncode == 0:
            return "\n".join(output) if output else "Code executed successfully with no output."
        else:
            return f"Execution failed with return code {result.returncode}\n" + "\n".join(output)
            
    except subprocess.TimeoutExpired:
        return "Execution timed out after 120 seconds"
    except Exception as e:
        return f"Execution error: {str(e)}"
    finally:
        # Clean up
        try:
            os.unlink(temp_path)
            # Clean up in container
            subprocess.run(
                ["docker", "exec", "pyspark-notebook", "rm", f"/tmp/{os.path.basename(temp_path)}"],
                capture_output=True
            )
        except:
            pass