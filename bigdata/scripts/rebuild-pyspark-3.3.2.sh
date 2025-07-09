#!/bin/bash

# Script to rebuild all containers with PySpark 3.3.2

echo "=================================="
echo "Rebuilding with PySpark 3.3.2"
echo "=================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check for container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
else
    echo "Error: Neither podman nor docker is installed!"
    exit 1
fi

echo -e "${BLUE}Using $CONTAINER_CMD for container management${NC}"

# Navigate to docker directory
cd "$(dirname "$0")/../docker" || exit 1

# Stop and remove existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
$COMPOSE_CMD -f docker-compose.pyspark.yml down

# Remove old images
echo -e "${YELLOW}Removing old images...${NC}"
$CONTAINER_CMD rmi pyspark-app 2>/dev/null || true

# Rebuild the PySpark container
echo -e "${YELLOW}Building PySpark 3.3.2 container...${NC}"
$COMPOSE_CMD -f docker-compose.pyspark.yml build

# Start the container
echo -e "${YELLOW}Starting PySpark 3.3.2 container...${NC}"
$COMPOSE_CMD -f docker-compose.pyspark.yml up -d pyspark

# Wait for container to be ready
echo -e "${YELLOW}Waiting for container to start...${NC}"
sleep 10

# Verify PySpark version
echo -e "${GREEN}Verifying PySpark installation...${NC}"
echo -n "PySpark version: "
$CONTAINER_CMD exec pyspark-app python -c "import pyspark; print(pyspark.__version__)"

echo -n "Spark version: "
$CONTAINER_CMD exec pyspark-app spark-submit --version 2>&1 | grep "version" | head -1

# Test PySpark functionality
echo -e "${YELLOW}Testing PySpark functionality...${NC}"
$CONTAINER_CMD exec pyspark-app python -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('VersionTest').getOrCreate()
print(f'Spark Session Created: {spark.version}')
df = spark.range(5)
print('Test DataFrame:')
df.show()
spark.stop()
print('Test completed successfully!')
"

echo -e "${GREEN}=================================="
echo "PySpark 3.3.2 Setup Complete!"
echo "==================================${NC}"
echo ""
echo "Access methods:"
echo "- Jupyter Lab: http://localhost:8888"
echo "- PySpark shell: $CONTAINER_CMD exec -it pyspark-app pyspark"
echo "- Python shell: $CONTAINER_CMD exec -it pyspark-app python"
echo ""
echo "All components now use PySpark 3.3.2"