#!/bin/bash

# Script to verify Python 3.9.20 installation across all containers

echo "======================================"
echo "Verifying Python 3.9.20 Installation"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check for container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo -e "${RED}Error: Neither podman nor docker is installed!${NC}"
    exit 1
fi

echo -e "${BLUE}Using $CONTAINER_CMD for container checks${NC}"
echo ""

# Function to check Python version in a container
check_python_version() {
    local container_name=$1
    local container_desc=$2
    
    echo -e "${YELLOW}Checking $container_desc...${NC}"
    
    # Check if container is running
    if ! $CONTAINER_CMD ps | grep -q "$container_name"; then
        echo -e "${RED}  ✗ Container '$container_name' is not running${NC}"
        return 1
    fi
    
    # Check Python version
    echo -n "  Python version: "
    python_version=$($CONTAINER_CMD exec "$container_name" python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    
    if [ "$python_version" = "3.9.20" ]; then
        echo -e "${GREEN}$python_version ✓${NC}"
    else
        echo -e "${RED}$python_version ✗ (Expected 3.9.20)${NC}"
    fi
    
    # Check Python3 version
    echo -n "  Python3 version: "
    python3_version=$($CONTAINER_CMD exec "$container_name" python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    
    if [ "$python3_version" = "3.9.20" ]; then
        echo -e "${GREEN}$python3_version ✓${NC}"
    else
        echo -e "${RED}$python3_version ✗ (Expected 3.9.20)${NC}"
    fi
    
    # Check pip version
    echo -n "  Pip version: "
    pip_version=$($CONTAINER_CMD exec "$container_name" pip --version 2>&1 | head -1)
    echo "$pip_version"
    
    # Check PySpark Python configuration
    echo -n "  PYSPARK_PYTHON: "
    pyspark_python=$($CONTAINER_CMD exec "$container_name" bash -c 'echo $PYSPARK_PYTHON' 2>&1)
    if [ -n "$pyspark_python" ]; then
        echo "$pyspark_python"
    else
        echo "Not set"
    fi
    
    # Test Python functionality
    echo -n "  Python functionality test: "
    if $CONTAINER_CMD exec "$container_name" python -c "import sys; assert sys.version_info[:3] == (3, 9, 20)" 2>/dev/null; then
        echo -e "${GREEN}✓ Passed${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
    
    # Test PySpark with Python 3.9.20
    echo -n "  PySpark compatibility test: "
    if $CONTAINER_CMD exec "$container_name" python -c "import pyspark; spark = pyspark.sql.SparkSession.builder.appName('test').getOrCreate(); print('OK')" 2>/dev/null | grep -q "OK"; then
        echo -e "${GREEN}✓ Passed${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
    
    echo ""
}

# Check main PySpark container
if $CONTAINER_CMD ps | grep -q "pyspark-app"; then
    check_python_version "pyspark-app" "Main PySpark Container"
else
    echo -e "${YELLOW}Main PySpark container not running. To start it:${NC}"
    echo "  cd bigdata/docker"
    echo "  docker-compose -f docker-compose.pyspark.yml up -d"
    echo ""
fi

# Check Cloudera CDH container
if $CONTAINER_CMD ps | grep -q "cdh7-spark3"; then
    check_python_version "cdh7-spark3" "Cloudera CDH Container"
else
    echo -e "${YELLOW}Cloudera CDH container not running. To start it:${NC}"
    echo "  cd bigdata/cloudera"
    echo "  ./build-and-run.sh"
    echo ""
fi

# Summary
echo "======================================"
echo "Python Version Check Summary"
echo "======================================"
echo ""
echo "Expected Python version: 3.9.20"
echo ""
echo "To rebuild containers with Python 3.9.20:"
echo "1. Main PySpark container:"
echo "   cd bigdata/docker"
echo "   docker-compose -f docker-compose.pyspark.yml down"
echo "   docker-compose -f docker-compose.pyspark.yml build"
echo "   docker-compose -f docker-compose.pyspark.yml up -d"
echo ""
echo "2. Cloudera CDH container:"
echo "   cd bigdata/cloudera"
echo "   podman-compose down"
echo "   podman-compose build"
echo "   ./build-and-run.sh"
echo ""
echo -e "${YELLOW}Note: Python 3.9.20 is compatible with PySpark 3.3.2${NC}"