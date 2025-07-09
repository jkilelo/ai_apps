#!/bin/bash

# Build and run CDH 7.1.9 with Spark 3.3.2 using Podman

set -e

echo "==================================="
echo "CDH 7.1.9 + Spark 3.3.2 Setup"
echo "==================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check for podman or docker
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

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p workspace/{data,notebooks,logs}
mkdir -p data

# Make scripts executable
chmod +x scripts/*.sh

# For Podman: Set up necessary system parameters
if [ "$CONTAINER_CMD" == "podman" ]; then
    echo -e "${YELLOW}Setting up Podman-specific configurations...${NC}"
    
    # Increase max map count for Elasticsearch/Spark
    if [ -w /proc/sys/vm/max_map_count ]; then
        sudo sysctl -w vm.max_map_count=262144
    fi
    
    # Enable lingering for rootless containers
    if command -v loginctl &> /dev/null; then
        loginctl enable-linger $USER 2>/dev/null || true
    fi
fi

# Build the image
echo -e "${YELLOW}Building CDH-Spark image...${NC}"
$COMPOSE_CMD build

# Start the services
echo -e "${YELLOW}Starting services...${NC}"
$COMPOSE_CMD up -d

# Wait for services to start
echo -e "${YELLOW}Waiting for services to initialize (30 seconds)...${NC}"
sleep 30

# Check service status
echo -e "${BLUE}Checking service status...${NC}"
$CONTAINER_CMD exec cdh7-spark3 jps

# Display access information
echo -e "${GREEN}==================================="
echo "Services are starting up!"
echo "===================================${NC}"
echo ""
echo "Web UIs will be available at:"
echo "- HDFS NameNode:      http://localhost:9870"
echo "- YARN ResourceMgr:   http://localhost:8088"
echo "- Spark Master:       http://localhost:8080"
echo "- Spark History:      http://localhost:18080"
echo "- Jupyter Lab:        http://localhost:8888"
echo ""
echo "Container Access:"
echo "- Shell: $CONTAINER_CMD exec -it cdh7-spark3 /bin/bash"
echo "- PySpark: $CONTAINER_CMD exec -it cdh7-spark3 pyspark"
echo "- Spark Shell: $CONTAINER_CMD exec -it cdh7-spark3 spark-shell"
echo ""
echo "To verify installation:"
echo "- Run: ./test-installation.sh"
echo ""
echo "To stop services:"
echo "- Run: $COMPOSE_CMD down"
echo ""
echo -e "${YELLOW}Note: Services may take 1-2 minutes to fully initialize${NC}"