#!/bin/bash
# Multiple ways to check PySpark version from command line

echo "🔍 PySpark Version Check - Command Line Methods"
echo "=============================================="

echo -e "\n=== Method 1: Using Python -c ==="
python -c "import pyspark; print(f'PySpark version: {pyspark.__version__}')" 2>/dev/null || echo "PySpark not installed or not in PYTHONPATH"

echo -e "\n=== Method 2: Using pip show ==="
pip show pyspark 2>/dev/null | grep -E "Name:|Version:" || echo "PySpark not installed via pip"

echo -e "\n=== Method 3: Using pip list ==="
pip list 2>/dev/null | grep -i pyspark || echo "PySpark not found in pip list"

echo -e "\n=== Method 4: Using conda list (if available) ==="
which conda >/dev/null 2>&1 && conda list pyspark 2>/dev/null | grep -v "^#" | grep pyspark || echo "Conda not available or PySpark not installed via conda"

echo -e "\n=== Method 5: Using spark-submit ==="
which spark-submit >/dev/null 2>&1 && spark-submit --version 2>&1 | head -n 5 || echo "spark-submit not found in PATH"

echo -e "\n=== Method 6: Using pyspark shell ==="
which pyspark >/dev/null 2>&1 && pyspark --version 2>&1 | head -n 5 || echo "pyspark shell not found in PATH"

echo -e "\n=== Method 7: Check SPARK_HOME ==="
if [ -n "$SPARK_HOME" ]; then
    echo "SPARK_HOME is set to: $SPARK_HOME"
    if [ -f "$SPARK_HOME/RELEASE" ]; then
        echo "Spark RELEASE file content:"
        cat "$SPARK_HOME/RELEASE"
    fi
    if [ -f "$SPARK_HOME/python/pyspark/__init__.py" ]; then
        echo "Checking PySpark in SPARK_HOME:"
        grep "__version__" "$SPARK_HOME/python/pyspark/__init__.py" 2>/dev/null || echo "Version not found in __init__.py"
    fi
else
    echo "SPARK_HOME not set"
fi

echo -e "\n=== Method 8: Docker container check ==="
echo "To check in Docker containers, use:"
echo '  docker exec <container> python -c "import pyspark; print(pyspark.__version__)"'
echo '  docker exec <container> spark-submit --version'
echo '  docker exec <container> pip show pyspark'

echo -e "\n=== Method 9: Using dpkg (Debian/Ubuntu) ==="
which dpkg >/dev/null 2>&1 && dpkg -l | grep -i spark | grep -i python || echo "No Spark packages found via dpkg"

echo -e "\n=== Method 10: Using rpm (RedHat/CentOS) ==="
which rpm >/dev/null 2>&1 && rpm -qa | grep -i pyspark || echo "No PySpark packages found via rpm"

echo -e "\n=============================================="
echo "✅ Version check completed!"

# Function to check PySpark in a specific Python environment
check_python_env() {
    local python_cmd=$1
    echo -e "\n=== Checking with $python_cmd ==="
    if which $python_cmd >/dev/null 2>&1; then
        $python_cmd -c "import pyspark; print(f'PySpark version: {pyspark.__version__}')" 2>/dev/null || echo "PySpark not available in $python_cmd"
    else
        echo "$python_cmd not found"
    fi
}

# Check different Python versions if available
echo -e "\n=== Checking different Python environments ==="
check_python_env "python"
check_python_env "python3"
check_python_env "python3.8"
check_python_env "python3.9"
check_python_env "python3.10"
check_python_env "python3.11"