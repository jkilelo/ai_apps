#!/bin/bash

# Script to run synthetic data generation in PySpark container

echo "Starting synthetic data generation for big data project..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker/podman is available
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo "Error: Neither docker nor podman is installed!"
    exit 1
fi

echo -e "${BLUE}Using $CONTAINER_CMD for container management${NC}"

# Navigate to the bigdata docker directory
cd "$(dirname "$0")/../docker" || exit 1

# Build the PySpark image if needed
echo -e "${YELLOW}Building PySpark container image...${NC}"
$CONTAINER_CMD compose -f docker-compose.pyspark.yml build

# Start the PySpark container
echo -e "${YELLOW}Starting PySpark container...${NC}"
$CONTAINER_CMD compose -f docker-compose.pyspark.yml up -d pyspark

# Wait for container to be ready
echo -e "${YELLOW}Waiting for container to be ready...${NC}"
sleep 10

# Copy the data generator files to container
echo -e "${BLUE}Copying data generator files to container...${NC}"
$CONTAINER_CMD cp ../data_generator/synthetic_data_generator.py pyspark-app:/workspace/
$CONTAINER_CMD cp ../data_generator/requirements.txt pyspark-app:/workspace/data_generator_requirements.txt

# Install required Python packages
echo -e "${YELLOW}Installing required Python packages...${NC}"
$CONTAINER_CMD exec pyspark-app pip install -r /workspace/data_generator_requirements.txt

# Run the data generation script
echo -e "${GREEN}Running synthetic data generation...${NC}"
$CONTAINER_CMD exec -it pyspark-app spark-submit \
    --master local[*] \
    --driver-memory 4g \
    --executor-memory 4g \
    /workspace/synthetic_data_generator.py

echo -e "${GREEN}Data generation completed!${NC}"

# Show Hive tables
echo -e "${BLUE}Verifying created tables...${NC}"
$CONTAINER_CMD exec -it pyspark-app spark-sql -e "
    USE retail_analytics;
    SHOW TABLES;
"

# Show record counts
echo -e "${BLUE}Record counts for each table:${NC}"
$CONTAINER_CMD exec -it pyspark-app spark-sql -e "
    USE retail_analytics;
    SELECT 'customers' as table_name, COUNT(*) as record_count FROM customers
    UNION ALL
    SELECT 'products', COUNT(*) FROM products
    UNION ALL
    SELECT 'stores', COUNT(*) FROM stores
    UNION ALL
    SELECT 'employees', COUNT(*) FROM employees
    UNION ALL
    SELECT 'suppliers', COUNT(*) FROM suppliers
    UNION ALL
    SELECT 'transactions', COUNT(*) FROM transactions
    UNION ALL
    SELECT 'inventory', COUNT(*) FROM inventory
    UNION ALL
    SELECT 'customer_behavior', COUNT(*) FROM customer_behavior
    UNION ALL
    SELECT 'product_reviews', COUNT(*) FROM product_reviews
    UNION ALL
    SELECT 'marketing_campaigns', COUNT(*) FROM marketing_campaigns;
"

echo -e "${GREEN}✅ Synthetic data generation complete!${NC}"
echo -e "${BLUE}You can now use these tables for your big data analytics projects.${NC}"
echo ""
echo "To access the data:"
echo "1. Jupyter Lab: http://localhost:8888"
echo "2. Spark UI: http://localhost:4040"
echo "3. Connect to container: $CONTAINER_CMD exec -it pyspark-app /bin/bash"