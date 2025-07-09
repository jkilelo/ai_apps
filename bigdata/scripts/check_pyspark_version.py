#!/usr/bin/env python3
"""
Multiple ways to check PySpark version across different environments
"""

import sys
import subprocess
import os

def method1_spark_session():
    """Method 1: Using SparkSession (most common)"""
    print("\n=== Method 1: Using SparkSession ===")
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.appName("VersionCheck").getOrCreate()
        print(f"PySpark version: {spark.version}")
        spark.stop()
    except ImportError:
        print("PySpark not installed or not in PYTHONPATH")
    except Exception as e:
        print(f"Error: {e}")

def method2_spark_context():
    """Method 2: Using SparkContext"""
    print("\n=== Method 2: Using SparkContext ===")
    try:
        from pyspark import SparkContext
        sc = SparkContext.getOrCreate()
        print(f"PySpark version: {sc.version}")
        sc.stop()
    except ImportError:
        print("PySpark not installed or not in PYTHONPATH")
    except Exception as e:
        print(f"Error: {e}")

def method3_pyspark_module():
    """Method 3: Direct module inspection"""
    print("\n=== Method 3: Direct module inspection ===")
    try:
        import pyspark
        print(f"PySpark version: {pyspark.__version__}")
    except ImportError:
        print("PySpark not installed")
    except AttributeError:
        print("Version information not available in this PySpark installation")

def method4_pip_show():
    """Method 4: Using pip show"""
    print("\n=== Method 4: Using pip show ===")
    try:
        result = subprocess.run(['pip', 'show', 'pyspark'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    print(f"PySpark {line}")
        else:
            print("PySpark not installed via pip")
    except Exception as e:
        print(f"Error running pip: {e}")

def method5_conda_list():
    """Method 5: Using conda list (if using Anaconda)"""
    print("\n=== Method 5: Using conda list ===")
    try:
        result = subprocess.run(['conda', 'list', 'pyspark'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'pyspark' in result.stdout:
            for line in result.stdout.split('\n'):
                if 'pyspark' in line and not line.startswith('#'):
                    print(f"Found: {line.strip()}")
        else:
            print("PySpark not installed via conda or conda not available")
    except Exception as e:
        print(f"Conda not available: {e}")

def method6_spark_submit():
    """Method 6: Using spark-submit"""
    print("\n=== Method 6: Using spark-submit ===")
    try:
        result = subprocess.run(['spark-submit', '--version'], 
                              capture_output=True, text=True, stderr=subprocess.STDOUT)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'version' in line.lower() and any(x in line for x in ['Spark', 'spark']):
                    print(line.strip())
        else:
            print("spark-submit not found in PATH")
    except Exception as e:
        print(f"spark-submit not available: {e}")

def method7_pyspark_shell():
    """Method 7: Check PySpark shell version"""
    print("\n=== Method 7: PySpark shell version ===")
    try:
        # Create a temporary Python script to run in pyspark
        temp_script = """
import sys
print(f"Python version: {sys.version}")
print(f"PySpark version: {spark.version}")
sys.exit(0)
"""
        with open('/tmp/version_check.py', 'w') as f:
            f.write(temp_script)
        
        result = subprocess.run(['pyspark', '--version'], 
                              capture_output=True, text=True, stderr=subprocess.STDOUT)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print("pyspark shell not found in PATH")
            
        # Clean up
        if os.path.exists('/tmp/version_check.py'):
            os.remove('/tmp/version_check.py')
    except Exception as e:
        print(f"pyspark shell not available: {e}")

def method8_docker_check():
    """Method 8: Check PySpark in Docker containers"""
    print("\n=== Method 8: Docker container check ===")
    print("To check PySpark version in Docker containers:")
    print("1. List running containers: docker ps")
    print("2. Execute version check in container:")
    print("   docker exec <container_name> python -c \"import pyspark; print(pyspark.__version__)\"")
    print("   OR")
    print("   docker exec <container_name> spark-submit --version")
    print("   OR")
    print("   docker exec -it <container_name> pyspark --version")

def method9_environment_variables():
    """Method 9: Check Spark environment variables"""
    print("\n=== Method 9: Environment variables ===")
    spark_home = os.environ.get('SPARK_HOME')
    if spark_home:
        print(f"SPARK_HOME: {spark_home}")
        version_file = os.path.join(spark_home, 'RELEASE')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    print(f"Spark RELEASE file content: {f.read().strip()}")
            except Exception as e:
                print(f"Could not read RELEASE file: {e}")
    else:
        print("SPARK_HOME not set")
    
    pythonpath = os.environ.get('PYTHONPATH', '')
    if 'pyspark' in pythonpath.lower():
        print(f"PySpark in PYTHONPATH: {pythonpath}")

def method10_jupyter_notebook():
    """Method 10: Commands for Jupyter notebooks"""
    print("\n=== Method 10: Jupyter notebook commands ===")
    print("In a Jupyter notebook cell, you can use:")
    print("```python")
    print("# Method 1")
    print("import pyspark")
    print("print(pyspark.__version__)")
    print()
    print("# Method 2")
    print("from pyspark.sql import SparkSession")
    print("spark = SparkSession.builder.getOrCreate()")
    print("print(spark.version)")
    print()
    print("# Method 3 - Using shell command")
    print("!pip show pyspark | grep Version")
    print("```")

def main():
    print("🔍 PySpark Version Check - Multiple Methods")
    print("=" * 50)
    
    # Run all methods
    method1_spark_session()
    method2_spark_context()
    method3_pyspark_module()
    method4_pip_show()
    method5_conda_list()
    method6_spark_submit()
    method7_pyspark_shell()
    method8_docker_check()
    method9_environment_variables()
    method10_jupyter_notebook()
    
    print("\n" + "=" * 50)
    print("✅ Version check completed!")

if __name__ == "__main__":
    main()