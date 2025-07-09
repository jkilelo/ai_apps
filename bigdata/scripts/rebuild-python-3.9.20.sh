#!/bin/bash

# Script to rebuild all containers with Python 3.9.20

echo "========================================"
echo "Rebuilding All Containers with Python 3.9.20"
echo "========================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check for container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}Error: Neither podman nor docker is installed!${NC}"
    exit 1
fi

echo -e "${BLUE}Using $CONTAINER_CMD for container management${NC}"

# Function to rebuild a container
rebuild_container() {
    local compose_file=$1
    local container_name=$2
    local description=$3
    
    echo -e "${YELLOW}Rebuilding $description...${NC}"
    
    # Stop and remove existing container
    echo "  Stopping existing container..."
    $COMPOSE_CMD -f "$compose_file" down 2>/dev/null || true
    
    # Remove old image to force rebuild
    echo "  Removing old image..."
    $CONTAINER_CMD rmi "$container_name" 2>/dev/null || true
    
    # Build new image
    echo "  Building new image with Python 3.9.20..."
    if $COMPOSE_CMD -f "$compose_file" build; then
        echo -e "${GREEN}  ✓ Build successful${NC}"
    else
        echo -e "${RED}  ✗ Build failed${NC}"
        return 1
    fi
    
    # Start container
    echo "  Starting container..."
    if $COMPOSE_CMD -f "$compose_file" up -d; then
        echo -e "${GREEN}  ✓ Container started${NC}"
    else
        echo -e "${RED}  ✗ Failed to start container${NC}"
        return 1
    fi
    
    # Wait for container to be ready
    sleep 5
    
    # Verify Python version
    echo "  Verifying Python version..."
    python_version=$($CONTAINER_CMD exec "$container_name" python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
    
    if [ "$python_version" = "3.9.20" ]; then
        echo -e "${GREEN}  ✓ Python $python_version installed correctly${NC}"
    else
        echo -e "${RED}  ✗ Python version is $python_version (expected 3.9.20)${NC}"
    fi
    
    echo ""
}

# Main execution
echo -e "${BLUE}Starting rebuild process...${NC}"
echo ""

# Rebuild main PySpark container
cd "$(dirname "$0")/../docker" || exit 1
rebuild_container "docker-compose.pyspark.yml" "pyspark-app" "Main PySpark Container"

# Rebuild Cloudera CDH container (if compose file exists)
cd ../cloudera || exit 1
if [ -f "docker-compose.yml" ]; then
    rebuild_container "docker-compose.yml" "cdh7-spark3" "Cloudera CDH Container"
else
    echo -e "${YELLOW}Cloudera CDH container requires manual rebuild:${NC}"
    echo "  cd bigdata/cloudera"
    echo "  ./build-and-run.sh"
fi

# Run verification script
echo -e "${BLUE}Running verification...${NC}"
cd ../scripts || exit 1
./verify-python-version.sh

echo ""
echo "========================================"
echo "Rebuild Complete!"
echo "========================================"
echo ""
echo "All containers have been rebuilt with Python 3.9.20"
echo ""
echo "Quick verification commands:"
echo "  Main PySpark: $CONTAINER_CMD exec pyspark-app python --version"
echo "  Cloudera CDH: $CONTAINER_CMD exec cdh7-spark3 python --version"
echo ""
echo "To test PySpark functionality:"
echo "  $CONTAINER_CMD exec -it pyspark-app pyspark"